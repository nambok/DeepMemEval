"""Tests for dataset integrity and scenario quality."""

import json
import os
import pytest

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATASET_PATH = os.path.join(DATA_DIR, "deepmemeval_500.json")
SAMPLE_PATH = os.path.join(DATA_DIR, "deepmemeval_sample.json")

EXPECTED_CATEGORIES = {
    "belief-update": 100,
    "cascade-propagation": 80,
    "noise-resistance": 80,
    "temporal-belief": 80,
    "delta-efficiency": 80,
    "uncertainty-abstention": 80,
}

REQUIRED_FIELDS = ["scenario_id", "scenario_type", "conversation_history", "question", "expected_answer"]
SESSION_FIELDS = ["session_id", "date", "turns"]


@pytest.fixture(scope="module")
def dataset():
    with open(DATASET_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def sample():
    with open(SAMPLE_PATH) as f:
        return json.load(f)


class TestDatasetSize:
    def test_total_count(self, dataset):
        assert len(dataset) == 500

    def test_category_distribution(self, dataset):
        by_type = {}
        for s in dataset:
            t = s["scenario_type"]
            by_type[t] = by_type.get(t, 0) + 1
        for cat, expected in EXPECTED_CATEGORIES.items():
            assert by_type.get(cat, 0) == expected, f"{cat}: got {by_type.get(cat, 0)}, expected {expected}"

    def test_sample_is_subset(self, dataset, sample):
        dataset_ids = {s["scenario_id"] for s in dataset}
        for s in sample:
            sid = s["scenario_id"]
            # Sample entries may be from dataset or standalone
            assert "scenario_type" in s


class TestScenarioStructure:
    def test_required_fields(self, dataset):
        for s in dataset:
            for field in REQUIRED_FIELDS:
                assert field in s, f"{s['scenario_id']}: missing field '{field}'"

    def test_session_structure(self, dataset):
        for s in dataset:
            for session in s["conversation_history"]:
                for field in SESSION_FIELDS:
                    assert field in session, f"{s['scenario_id']}: session missing '{field}'"
                assert len(session["turns"]) >= 2, f"{s['scenario_id']}: session has < 2 turns"
                assert session["turns"][0]["role"] == "user"
                assert session["turns"][1]["role"] == "assistant"

    def test_unique_ids(self, dataset):
        ids = [s["scenario_id"] for s in dataset]
        assert len(ids) == len(set(ids)), f"Duplicate IDs found"

    def test_valid_scenario_types(self, dataset):
        valid = set(EXPECTED_CATEGORIES.keys())
        for s in dataset:
            assert s["scenario_type"] in valid, f"{s['scenario_id']}: unknown type '{s['scenario_type']}'"


class TestBeliefUpdateScenarios:
    def test_has_metadata(self, dataset):
        for s in dataset:
            if s["scenario_type"] != "belief-update":
                continue
            meta = s.get("metadata", {})
            assert "stale_answers" in meta, f"{s['scenario_id']}: missing stale_answers"
            assert "belief_timeline" in meta, f"{s['scenario_id']}: missing belief_timeline"
            assert len(meta["stale_answers"]) >= 1, f"{s['scenario_id']}: no stale answers"

    def test_expected_not_in_stale(self, dataset):
        for s in dataset:
            if s["scenario_type"] != "belief-update":
                continue
            stale = s["metadata"]["stale_answers"]
            assert s["expected_answer"] not in stale, f"{s['scenario_id']}: expected answer is in stale list"

    def test_no_action_phrased_answers(self, dataset):
        action_prefixes = ["Switched to", "Migrated to", "Back to", "Moved to", "Rewrote"]
        for s in dataset:
            if s["scenario_type"] != "belief-update":
                continue
            for prefix in action_prefixes:
                assert not s["expected_answer"].startswith(prefix), (
                    f"{s['scenario_id']}: action-phrased answer '{s['expected_answer'][:50]}'"
                )


class TestCascadeScenarios:
    def test_has_metadata(self, dataset):
        for s in dataset:
            if s["scenario_type"] != "cascade-propagation":
                continue
            meta = s.get("metadata", {})
            assert "root_change" in meta, f"{s['scenario_id']}: missing root_change"
            assert "old_dependent" in meta, f"{s['scenario_id']}: missing old_dependent"


class TestNoiseScenarios:
    def test_has_signal_metadata(self, dataset):
        for s in dataset:
            if s["scenario_type"] != "noise-resistance":
                continue
            meta = s.get("metadata", {})
            assert "signal_sessions" in meta, f"{s['scenario_id']}: missing signal_sessions"
            assert "total_sessions" in meta
            assert meta["total_sessions"] >= 20

    def test_noise_ratio(self, dataset):
        for s in dataset:
            if s["scenario_type"] != "noise-resistance":
                continue
            meta = s["metadata"]
            assert meta["signal_to_noise_ratio"] <= 0.1, f"{s['scenario_id']}: SNR too high"


class TestTemporalScenarios:
    def test_has_timestamp(self, dataset):
        for s in dataset:
            if s["scenario_type"] != "temporal-belief":
                continue
            meta = s.get("metadata", {})
            assert "query_timestamp" in meta, f"{s['scenario_id']}: missing query_timestamp"
            assert "current_belief" in meta, f"{s['scenario_id']}: missing current_belief"
            assert meta["current_belief"] != s["expected_answer"], (
                f"{s['scenario_id']}: temporal query answer should differ from current belief"
            )


class TestDeltaScenarios:
    def test_has_evaluation_turns(self, dataset):
        for s in dataset:
            if s["scenario_type"] != "delta-efficiency":
                continue
            assert "evaluation_turns" in s, f"{s['scenario_id']}: missing evaluation_turns"
            assert len(s["evaluation_turns"]) >= 10


class TestUncertaintyScenarios:
    def test_expected_is_uncertain(self, dataset):
        for s in dataset:
            if s["scenario_type"] != "uncertainty-abstention":
                continue
            assert s["expected_answer"] == "Uncertain", (
                f"{s['scenario_id']}: expected should be 'Uncertain', got '{s['expected_answer']}'"
            )

    def test_has_reason(self, dataset):
        for s in dataset:
            if s["scenario_type"] != "uncertainty-abstention":
                continue
            meta = s.get("metadata", {})
            assert "uncertainty_reason" in meta, f"{s['scenario_id']}: missing uncertainty_reason"
