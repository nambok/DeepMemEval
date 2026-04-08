"""DeepMemEval evaluation script.

Evaluates system responses against ground truth using GPT-4o as judge.

Usage:
    python evaluate.py --judge gpt-4o --results results/system.json --reference data/deepmemeval_500.json
"""

import argparse
import json
import os
import sys

import backoff
import numpy as np
import openai
from openai import OpenAI
from tqdm import tqdm

from src.prompts import JUDGE_PROMPTS, CATEGORY_WEIGHTS


JUDGE_MODELS = {
    "gpt-4o": "gpt-4o-2024-08-06",
    "gpt-4o-mini": "gpt-4o-mini-2024-07-18",
}


@backoff.on_exception(backoff.expo, (openai.RateLimitError, openai.APIError))
def judge_with_backoff(client, **kwargs):
    return client.chat.completions.create(**kwargs)


def build_judge_prompt(scenario: dict, response: str) -> str:
    """Build the appropriate judge prompt based on scenario type."""
    scenario_type = scenario["scenario_type"]
    metadata = scenario.get("metadata", {})

    if scenario_type == "delta-efficiency":
        return None  # quantitative, not LLM-judged

    template = JUDGE_PROMPTS[scenario_type]

    format_args = {
        "question": scenario["question"],
        "expected_answer": scenario["expected_answer"],
        "response": response,
    }

    if scenario_type == "belief-update":
        stale = metadata.get("stale_answers", [])
        format_args["stale_answers"] = ", ".join(stale) if stale else "None"

    elif scenario_type == "cascade-propagation":
        format_args["root_change"] = metadata.get("root_change", "")
        format_args["old_dependent"] = metadata.get("old_dependent", "")

    elif scenario_type == "uncertainty-abstention":
        format_args["uncertainty_reason"] = metadata.get("uncertainty_reason", "")

    return template.format(**format_args)


def evaluate_delta_efficiency(scenario: dict, result: dict) -> bool:
    """Evaluate delta efficiency quantitatively."""
    token_counts = result.get("token_counts", [])
    if not token_counts or len(token_counts) < 2:
        return False

    early_avg = np.mean(token_counts[:5]) if len(token_counts) >= 5 else token_counts[0]
    late_total = sum(token_counts[5:])
    expected_total = early_avg * len(token_counts[5:])

    if expected_total == 0:
        return False

    efficiency = 1 - (late_total / expected_total)
    return efficiency > 0.5


def main():
    parser = argparse.ArgumentParser(description="DeepMemEval evaluation")
    parser.add_argument("--judge", required=True, choices=list(JUDGE_MODELS.keys()))
    parser.add_argument("--results", required=True, help="Path to system results JSON")
    parser.add_argument("--reference", required=True, help="Path to reference dataset JSON")
    parser.add_argument("--output", default=None, help="Path to save evaluation results")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    model = JUDGE_MODELS[args.judge]

    with open(args.reference) as f:
        reference = json.load(f)
    ref_by_id = {s["scenario_id"]: s for s in reference}

    with open(args.results) as f:
        results = json.load(f)

    output_path = args.output or f"{args.results}.eval-{args.judge}"
    category_scores = {}

    evaluated = []

    for result in tqdm(results, desc="Evaluating"):
        sid = result["scenario_id"]
        if sid not in ref_by_id:
            print(f"Warning: skipping {sid} — not in reference data")
            continue

        scenario = ref_by_id[sid]
        response = result["response"]
        scenario_type = scenario["scenario_type"]

        if scenario_type == "delta-efficiency":
            label = evaluate_delta_efficiency(scenario, result)
        else:
            prompt = build_judge_prompt(scenario, response)
            assert prompt is not None

            completion = judge_with_backoff(
                client,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                n=1,
                temperature=0,
                max_tokens=10,
                seed=42,
            )
            eval_response = completion.choices[0].message.content.strip()
            label = "yes" in eval_response.lower()

        result["eval_label"] = label
        result["eval_model"] = model
        evaluated.append(result)

        if scenario_type not in category_scores:
            category_scores[scenario_type] = []
        category_scores[scenario_type].append(1 if label else 0)

    # Print results
    print("\n" + "=" * 60)
    print("DeepMemEval Results")
    print("=" * 60)

    composite = 0.0
    for category, scores in sorted(category_scores.items()):
        cat_score = np.mean(scores) * 100
        weight = CATEGORY_WEIGHTS.get(category, 0)
        weighted = cat_score * weight
        composite += weighted
        print(f"  {category:30s} {cat_score:6.1f}% ({len(scores)} scenarios)")

    print("-" * 60)
    print(f"  {'COMPOSITE SCORE':30s} {composite:6.1f}%")
    print("=" * 60)

    overall = np.mean([1 if r["eval_label"] else 0 for r in evaluated]) * 100
    print(f"  {'RAW ACCURACY (unweighted)':30s} {overall:6.1f}%")

    # Save
    with open(output_path, "w") as f:
        for entry in evaluated:
            print(json.dumps(entry), file=f)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
