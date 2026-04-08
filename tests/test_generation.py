"""Tests for the dataset generation pipeline."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dataset_generation"))


class TestPersonas:
    def test_handwritten_personas_load(self):
        from personas import PERSONAS
        assert len(PERSONAS) == 5

    def test_persona_structure(self):
        from personas import PERSONAS
        for p in PERSONAS:
            assert "id" in p
            assert "name" in p
            assert "timeline" in p
            assert len(p["timeline"]) >= 5

    def test_all_facts_are_states(self):
        from personas import PERSONAS
        action_prefixes = ["Switched to", "Migrated to", "Back to", "Moved to",
                          "Rewrote", "Simplified to"]
        for p in PERSONAS:
            for entry in p["timeline"]:
                for prefix in action_prefixes:
                    assert not entry["fact"].startswith(prefix), (
                        f"{p['id']}: action-phrased fact '{entry['fact'][:50]}'"
                    )


class TestGeneratedPersonas:
    def test_generates_50(self):
        from generate_personas import generate_all_personas
        personas = generate_all_personas(count=50)
        assert len(personas) == 50

    def test_unique_ids(self):
        from generate_personas import generate_all_personas
        personas = generate_all_personas(count=50)
        ids = [p["id"] for p in personas]
        assert len(ids) == len(set(ids))

    def test_all_have_supersession_chains(self):
        from generate_personas import generate_all_personas
        personas = generate_all_personas(count=50)
        for p in personas:
            has_supersedes = any("supersedes" in t for t in p["timeline"])
            assert has_supersedes, f"{p['id']} has no supersession chains"

    def test_all_have_identity(self):
        from generate_personas import generate_all_personas
        personas = generate_all_personas(count=50)
        for p in personas:
            categories = {t["category"] for t in p["timeline"]}
            assert "name" in categories, f"{p['id']} missing name"
            assert "team" in categories, f"{p['id']} missing team"


class TestScenarioGeneration:
    def test_generator_runs(self):
        """Smoke test: generator produces scenarios without errors."""
        from generate_personas import generate_all_personas
        # Import generator functions directly
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dataset_generation"))
        import generate_sample as gen

        personas = generate_all_personas(count=5)
        scenarios = []
        for p in personas:
            scenarios.extend(gen.generate_belief_update_scenarios(p))
            scenarios.extend(gen.generate_cascade_scenarios(p))
            scenarios.extend(gen.generate_noise_scenarios(p, max_per_persona=1))
            scenarios.extend(gen.generate_temporal_scenarios(p))
            scenarios.extend(gen.generate_delta_scenarios(p))
            scenarios.extend(gen.generate_uncertainty_scenarios(p))

        assert len(scenarios) > 0

    def test_no_duplicate_ids_per_persona(self):
        from generate_personas import generate_all_personas
        import generate_sample as gen

        personas = generate_all_personas(count=10)
        for p in personas:
            scenarios = []
            scenarios.extend(gen.generate_belief_update_scenarios(p))
            scenarios.extend(gen.generate_cascade_scenarios(p))
            scenarios.extend(gen.generate_noise_scenarios(p, max_per_persona=2))
            scenarios.extend(gen.generate_temporal_scenarios(p))
            scenarios.extend(gen.generate_delta_scenarios(p))
            scenarios.extend(gen.generate_uncertainty_scenarios(p))

            ids = [s["scenario_id"] for s in scenarios]
            assert len(ids) == len(set(ids)), f"{p['id']}: duplicate IDs {[x for x in ids if ids.count(x) > 1]}"
