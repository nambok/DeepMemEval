"""DeepMemEval benchmark runner.

Runs a memory system adapter against the DeepMemEval dataset.

Usage:
    python run_deepmemeval.py \
        --adapter adapters/your_system.py \
        --dataset data/deepmemeval_500.json \
        --output results/your_system.json
"""

import argparse
import importlib.util
import json
import sys
import time

from tqdm import tqdm


def load_adapter(adapter_path: str):
    """Dynamically load a MemorySystemAdapter from a Python file."""
    spec = importlib.util.spec_from_file_location("adapter_module", adapter_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (
            isinstance(attr, type)
            and attr_name != "MemorySystemAdapter"
            and hasattr(attr, "ingest_session")
            and hasattr(attr, "query")
            and hasattr(attr, "reset")
        ):
            return attr()

    print("Error: No MemorySystemAdapter implementation found in", adapter_path)
    sys.exit(1)


def run_scenario(adapter, scenario: dict) -> dict:
    """Run a single scenario against the adapter."""
    adapter.reset()

    scenario_type = scenario["scenario_type"]
    history = scenario["conversation_history"]

    # Verify no oracle access
    assert "belief_timeline" not in scenario.get("_accessible", {}), (
        "Oracle access detected: belief_timeline must not be accessible during execution"
    )

    # Ingest sessions sequentially
    for session in history:
        adapter.ingest_session(session, timestamp=session["date"])

    # Query
    result = {
        "scenario_id": scenario["scenario_id"],
        "scenario_type": scenario_type,
    }

    if scenario_type == "delta-efficiency":
        token_counts = []
        turns = scenario.get("evaluation_turns", [])
        for turn in turns:
            response = adapter.query(turn["question"])
            tokens = adapter.get_context_tokens()
            token_counts.append(tokens)
        result["token_counts"] = token_counts
        result["response"] = f"Token counts over {len(turns)} turns: {token_counts}"
    elif scenario_type == "temporal-belief":
        query_ts = scenario.get("metadata", {}).get("query_timestamp", "now")
        result["response"] = adapter.query(scenario["question"], timestamp=query_ts)
    else:
        result["response"] = adapter.query(scenario["question"])

    return result


def main():
    parser = argparse.ArgumentParser(description="Run DeepMemEval benchmark")
    parser.add_argument("--adapter", required=True, help="Path to adapter Python file")
    parser.add_argument("--dataset", required=True, help="Path to dataset JSON")
    parser.add_argument("--output", required=True, help="Path to save results")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of scenarios")
    args = parser.parse_args()

    adapter = load_adapter(args.adapter)
    print(f"Loaded adapter: {type(adapter).__name__}")

    with open(args.dataset) as f:
        scenarios = json.load(f)

    if args.limit:
        scenarios = scenarios[: args.limit]

    print(f"Running {len(scenarios)} scenarios...")

    results = []
    errors = 0
    start = time.time()

    for scenario in tqdm(scenarios, desc="DeepMemEval"):
        # Strip oracle fields before passing to adapter
        safe_scenario = {
            k: v
            for k, v in scenario.items()
            if k not in ("belief_timeline", "stale_answers", "metadata")
        }
        safe_scenario["_accessible"] = {}

        try:
            result = run_scenario(adapter, safe_scenario)
            results.append(result)
        except Exception as e:
            print(f"\nError on {scenario['scenario_id']}: {e}")
            results.append(
                {
                    "scenario_id": scenario["scenario_id"],
                    "scenario_type": scenario["scenario_type"],
                    "response": f"ERROR: {e}",
                    "error": True,
                }
            )
            errors += 1

    elapsed = time.time() - start

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"  Scenarios: {len(results)}")
    print(f"  Errors: {errors}")
    print(f"  Saved to: {args.output}")


if __name__ == "__main__":
    main()
