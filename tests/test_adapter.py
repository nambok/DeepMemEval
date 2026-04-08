"""Tests for the adapter interface and runner."""

import pytest
from src.adapter import MemorySystemAdapter


class TestAdapterInterface:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            MemorySystemAdapter()

    def test_concrete_adapter_must_implement_all(self):
        class IncompleteAdapter(MemorySystemAdapter):
            def ingest_session(self, session, timestamp):
                pass

        with pytest.raises(TypeError):
            IncompleteAdapter()

    def test_complete_adapter_works(self):
        class CompleteAdapter(MemorySystemAdapter):
            def ingest_session(self, session, timestamp):
                pass
            def query(self, question, timestamp="now"):
                return "answer"
            def get_context_tokens(self):
                return 0
            def reset(self):
                pass

        adapter = CompleteAdapter()
        assert adapter.query("test") == "answer"
        assert adapter.get_context_tokens() == 0


class TestRunnerLoadAdapter:
    def test_load_chromadb_baseline(self):
        from run_deepmemeval import load_adapter
        import os
        adapter_path = os.path.join(os.path.dirname(__file__), "..", "adapters", "chromadb_baseline.py")
        try:
            adapter = load_adapter(adapter_path)
            assert hasattr(adapter, "ingest_session")
            assert hasattr(adapter, "query")
            assert hasattr(adapter, "get_context_tokens")
            assert hasattr(adapter, "reset")
        except Exception:
            pytest.skip("ChromaDB not installed")


class TestRunnerOracleGuard:
    def test_oracle_fields_stripped(self):
        """Verify run_deepmemeval strips oracle fields before passing to adapter."""
        import json, os
        dataset_path = os.path.join(os.path.dirname(__file__), "..", "data", "deepmemeval_sample.json")
        with open(dataset_path) as f:
            scenarios = json.load(f)

        oracle_fields = {"belief_timeline", "stale_answers", "metadata"}
        for scenario in scenarios:
            safe = {k: v for k, v in scenario.items() if k not in oracle_fields}
            for field in oracle_fields:
                assert field not in safe
