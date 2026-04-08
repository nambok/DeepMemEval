# DeepMemEval Methodology

## Evaluation Standards

DeepMemEval uses a rigorous, reproducible evaluation methodology designed for credibility and transparency.

## Judge Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | `gpt-4o-2024-08-06` | Strong reasoning, widely available |
| Temperature | `0` | Deterministic evaluation |
| Max tokens | `10` | Binary yes/no response only |
| Seed | `42` | Cross-run reproducibility |
| Completions | `1` | Single evaluation per scenario |

## Per-Category Judge Prompts

Each category has a tailored prompt template. The judge receives the question, expected answer, and system response, then returns a binary yes/no judgment.

### Belief Update

```
I will give you a question, the current correct answer, a list of stale answers that
should NOT appear, and a response from a memory system. The correct answer reflects the
CURRENT state after all updates. Please answer yes if the response contains the current
correct answer and does NOT include any stale answers. If the response includes both
current and stale information, answer no. If the response only contains stale information,
answer no.

Question: {question}
Current Correct Answer: {expected_answer}
Stale Answers (should NOT appear): {stale_answers}
System Response: {response}

Is the system response correct and free of stale information? Answer yes or no only.
```

### Cascade Propagation

```
I will give you a question about a downstream belief that depends on a root fact that
has changed. The root fact change was: {root_change}. The question asks about a
dependent belief that was never explicitly updated. Please answer yes if the system
correctly expresses uncertainty or acknowledges that the dependent information may be
outdated. Answer no if the system returns the old dependent belief with confidence.

Question: {question}
Root Fact Change: {root_change}
Old Dependent Belief: {old_dependent}
System Response: {response}

Does the system appropriately handle the invalidated dependent belief? Answer yes or no only.
```

### Noise Resistance

```
I will give you a question, a correct answer, and a response from a memory system.
The correct answer is a specific fact stated by the user in conversation. Please answer
yes if the response contains the correct answer. Otherwise, answer no. If the response
contains distractor information that was not explicitly stated by the user as a preference
or fact, it should still be considered correct as long as the actual answer is present.

Question: {question}
Correct Answer: {expected_answer}
System Response: {response}

Is the system response correct? Answer yes or no only.
```

### Temporal Belief

```
I will give you a question about what was believed at a specific point in time, the
correct answer for that time period, and a response from a memory system. Please answer
yes if the response contains the answer that was correct AT THE SPECIFIED TIME. The
answer may differ from the current state. Answer no if the response gives the current
answer when the question asks about a past state, or vice versa.

Question: {question}
Correct Answer (at specified time): {expected_answer}
System Response: {response}

Is the system response correct for the specified time period? Answer yes or no only.
```

### Delta Efficiency

Delta efficiency is measured quantitatively, not by LLM judge:

```
efficiency_score = 1 - (total_tokens_turns_6_to_20 / (avg_turn_1_to_5_tokens * 15))
pass = efficiency_score > 0.5
```

Systems that send the same context every turn score ~0. Systems that only send deltas score close to 1.

### Uncertainty Abstention

```
I will give you a question where the correct behavior is to express uncertainty. The
underlying fact is ambiguous, partially invalidated, or conflicting. Please answer yes
if the system expresses appropriate uncertainty, hedges its answer, or asks for
clarification. Answer no if the system returns a definitive answer without acknowledging
the uncertainty.

Question: {question}
Reason for uncertainty: {uncertainty_reason}
System Response: {response}

Does the system appropriately express uncertainty? Answer yes or no only.
```

## Scoring

### Per-Category Score

```
category_score = correct_count / total_count * 100
```

### Composite Score

```
deepmemeval_score = (
    belief_update_score     * 0.25 +
    cascade_propagation     * 0.15 +
    noise_resistance        * 0.20 +
    temporal_belief         * 0.15 +
    delta_efficiency        * 0.10 +
    uncertainty_abstention  * 0.15
)
```

### Reporting Requirements

Results must include:
1. Composite DeepMemEval score
2. Per-category breakdown
3. System configuration (model, embedding provider, parameters)
4. Full results JSON (every scenario, system response, judge verdict)
5. Run logs

## Reproducibility Requirements

- Single deterministic run (no cherry-picking best of N)
- `PYTHONHASHSEED=42` for Python systems
- `seed=42` on all judge API calls
- No ensemble or voting across multiple runs
- Full results file committed to reproduce claims

## Anti-Cheating Measures

- `belief_timeline` and `stale_answers` fields must NOT be accessed during system execution
- Hard `assert` in evaluation harness prevents oracle access
- Systems ingest conversations sequentially (cannot peek ahead)
- Each scenario's conversation history is the only input; metadata is for evaluation only
