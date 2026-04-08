"""Tests for the evaluation harness components."""

import pytest
from src.prompts import JUDGE_PROMPTS, CATEGORY_WEIGHTS


class TestJudgePrompts:
    def test_all_categories_have_prompts(self):
        expected = {"belief-update", "cascade-propagation", "noise-resistance",
                    "temporal-belief", "uncertainty-abstention"}
        assert set(JUDGE_PROMPTS.keys()) == expected

    def test_prompts_have_placeholders(self):
        assert "{question}" in JUDGE_PROMPTS["belief-update"]
        assert "{expected_answer}" in JUDGE_PROMPTS["belief-update"]
        assert "{stale_answers}" in JUDGE_PROMPTS["belief-update"]
        assert "{response}" in JUDGE_PROMPTS["belief-update"]

        assert "{root_change}" in JUDGE_PROMPTS["cascade-propagation"]
        assert "{old_dependent}" in JUDGE_PROMPTS["cascade-propagation"]

        assert "{uncertainty_reason}" in JUDGE_PROMPTS["uncertainty-abstention"]

    def test_prompts_end_with_yes_or_no(self):
        for cat, prompt in JUDGE_PROMPTS.items():
            assert "yes or no" in prompt.lower(), f"{cat} prompt missing yes/no instruction"

    def test_no_delta_prompt(self):
        assert "delta-efficiency" not in JUDGE_PROMPTS


class TestCategoryWeights:
    def test_all_categories_have_weights(self):
        expected = {"belief-update", "cascade-propagation", "noise-resistance",
                    "temporal-belief", "delta-efficiency", "uncertainty-abstention"}
        assert set(CATEGORY_WEIGHTS.keys()) == expected

    def test_weights_sum_to_one(self):
        total = sum(CATEGORY_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9, f"Weights sum to {total}, expected 1.0"

    def test_weights_are_positive(self):
        for cat, weight in CATEGORY_WEIGHTS.items():
            assert weight > 0, f"{cat} has non-positive weight {weight}"


class TestBuildJudgePrompt:
    def test_belief_update_format(self):
        from evaluate import build_judge_prompt
        scenario = {
            "scenario_type": "belief-update",
            "question": "What database?",
            "expected_answer": "Uses DuckDB",
            "metadata": {
                "stale_answers": ["Uses PostgreSQL", "Uses SQLite"],
            },
        }
        prompt = build_judge_prompt(scenario, "DuckDB for analytics")
        assert "What database?" in prompt
        assert "Uses DuckDB" in prompt
        assert "Uses PostgreSQL, Uses SQLite" in prompt
        assert "DuckDB for analytics" in prompt

    def test_cascade_format(self):
        from evaluate import build_judge_prompt
        scenario = {
            "scenario_type": "cascade-propagation",
            "question": "What testing?",
            "expected_answer": "Uncertain",
            "metadata": {
                "root_change": "Python → Go",
                "old_dependent": "Uses pytest",
            },
        }
        prompt = build_judge_prompt(scenario, "pytest")
        assert "Python → Go" in prompt
        assert "Uses pytest" in prompt

    def test_delta_returns_none(self):
        from evaluate import build_judge_prompt
        scenario = {"scenario_type": "delta-efficiency", "question": "x", "expected_answer": "x"}
        assert build_judge_prompt(scenario, "resp") is None

    def test_uncertainty_format(self):
        from evaluate import build_judge_prompt
        scenario = {
            "scenario_type": "uncertainty-abstention",
            "question": "Still using X?",
            "expected_answer": "Uncertain",
            "metadata": {"uncertainty_reason": "Root changed"},
        }
        prompt = build_judge_prompt(scenario, "I'm not sure")
        assert "Root changed" in prompt


class TestDeltaEfficiency:
    def test_efficient_system_passes(self):
        from evaluate import evaluate_delta_efficiency
        # First 5 turns: 1000 tokens each, next 15: 100 each
        scenario = {"scenario_type": "delta-efficiency"}
        result = {"token_counts": [1000]*5 + [100]*15}
        assert evaluate_delta_efficiency(scenario, result) == True

    def test_inefficient_system_fails(self):
        from evaluate import evaluate_delta_efficiency
        scenario = {"scenario_type": "delta-efficiency"}
        result = {"token_counts": [1000]*20}  # same tokens every turn
        assert evaluate_delta_efficiency(scenario, result) == False

    def test_empty_counts_fails(self):
        from evaluate import evaluate_delta_efficiency
        scenario = {"scenario_type": "delta-efficiency"}
        assert evaluate_delta_efficiency(scenario, {"token_counts": []}) is False
        assert evaluate_delta_efficiency(scenario, {}) is False
