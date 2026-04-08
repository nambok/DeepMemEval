# DeepMemEval

**Benchmarking Belief Management, Memory Quality, and Context Efficiency in AI Agent Memory Systems**

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

## Overview

DeepMemEval is a benchmark for evaluating AI agent memory systems on capabilities that existing retrieval benchmarks do not test: belief management, memory quality under noise, temporal belief tracking, cascade propagation, context efficiency, and epistemic uncertainty.

Existing memory benchmarks ask: **"Can you find the right memory?"** (retrieval accuracy from clean, static histories)

DeepMemEval asks: **"Is what you stored correct, current, and efficiently delivered?"** (memory quality under real-world conditions)

## Why DeepMemEval?

Current memory benchmarks evaluate a simplified scenario:

- Fresh database per question (no accumulated noise)
- Static facts (no evolving beliefs)
- Single retrieval per question (no multi-turn context building)
- No measurement of token efficiency
- No measurement of memory quality at ingest

In real agent deployments, facts change, noise accumulates, context windows have budgets, and systems run for weeks. DeepMemEval tests these conditions.

## Six Test Categories (500 Scenarios)

| Category | Count | Weight | What It Tests |
|----------|-------|--------|---------------|
| **Belief Update** | 100 | 25% | When a fact changes, does the system return only the current belief? |
| **Cascade Propagation** | 80 | 15% | When a root fact changes, are dependent beliefs also invalidated? |
| **Noise Resistance** | 80 | 20% | Can the system find signal in 20–40 sessions of conversational noise? |
| **Temporal Belief** | 80 | 15% | Can the system answer "what was believed at time X?" |
| **Delta Efficiency** | 80 | 10% | Does context size grow linearly or stay efficient over 20 turns? |
| **Uncertainty Abstention** | 80 | 15% | Does the system express uncertainty when beliefs are partially invalidated? |

### Category Details

#### 1. Belief Update Correctness (100 scenarios)

Multi-session conversations where user facts are stated and later updated, sometimes multiple times.

**Strict belief update evaluation**: Unlike benchmarks that accept responses including stale information alongside the updated answer, DeepMemEval requires returning **only** the current belief. Returning stale data is a failure.

```
Session 1 (Jan): "I'm using PostgreSQL for our main database"
Session 5 (Feb): "We migrated to SQLite, PostgreSQL was overkill"
Session 8 (Mar): "Actually we moved to DuckDB for analytics"

Question: "What database does the user currently use?"
✅ Correct: "DuckDB"
❌ Incorrect: "PostgreSQL" or "SQLite" or "PostgreSQL, but they later switched to DuckDB"
```

Difficulty levels: Easy — single update, clear language. Medium — multiple updates. Scenarios are weighted toward easy (2-step chains) with medium (3-step chains) for variety.

#### 2. Cascade Propagation (80 scenarios)

When a root fact changes, dependent beliefs that were never explicitly contradicted should be flagged as uncertain.

```
Session 1: "I'm building the backend in Python using Django"
Session 2: "The Django ORM handles our database migrations"
Session 3: "We use pytest for all our Django tests"
Session 7: "We rewrote the backend in Go"

Question: "What test framework does the user use for their backend?"
✅ Correct: Expresses uncertainty (pytest was Django-specific, they switched to Go)
❌ Incorrect: "pytest" returned with confidence
```

#### 3. Noise Resistance (80 scenarios)

1 important fact embedded within 20–40 sessions of realistic conversational noise (chitchat, coding questions, general Q&A). Tests whether the system stores everything (and drowns in noise) or extracts what matters.

Variants:
- **Light noise** (40): 1 signal in 20 filler sessions (5% SNR)
- **Heavy noise** (40): 1 signal in 40 filler sessions (2.5% SNR)

#### 4. Temporal Belief Queries (80 scenarios)

Facts that evolve over time, with questions about past and present states.

```
Session 1 (Jan): "I'm using VS Code"
Session 5 (Mar): "Switched to Neovim last week"
Session 9 (Jun): "Back to VS Code, Neovim was too much config"

Question: "What editor was the user using in April?"
✅ Correct: "Neovim"
```

All scenarios use explicit timestamps — the question specifies a month/year and the system must return what was believed at that time, not the current state.

#### 5. Delta Efficiency (80 scenarios)

20-turn conversations measuring context tokens sent at turns 1, 5, 10, 15, 20. Systems that track what the agent already knows should send dramatically less on later turns.

Efficiency score: `1 - (total_tokens_turns_6_to_20 / (avg_tokens_turns_1_to_5 × 15))`

#### 6. Uncertainty Abstention (80 scenarios)

When beliefs are partially invalidated, conflicting, or ambiguous, the system should express uncertainty rather than returning stale data confidently.

All scenarios test partially-invalidated beliefs: a root fact changed (e.g., language switch) and a dependent belief (e.g., test framework) was never explicitly updated. The system should express uncertainty rather than confidently returning the stale dependent.

## Methodology

DeepMemEval uses a rigorous, reproducible evaluation methodology.

### Judge

- **Model**: `gpt-4o-2024-08-06` (`temperature=0`, `max_tokens=10`, `seed=42`)
- **Scoring**: Binary yes/no per scenario
- **Per-category prompt templates** tailored to each evaluation dimension

### Reproducibility

- Single deterministic run
- `PYTHONHASHSEED=42` for Python systems
- Full results JSON published (every scenario, every response)
- Full run logs published

### Legitimacy

- Ground-truth belief timelines never accessible during system execution
- Hard `assert` guarding against oracle leakage
- Evaluation script is open source — anyone can verify

### Scoring

```
DeepMemEval Score = weighted average across categories

  Belief Update:          25%
  Cascade Propagation:    15%
  Noise Resistance:       20%
  Temporal Belief:        15%
  Delta Efficiency:       10%
  Uncertainty Abstention: 15%
```

Per-category scores are also reported individually.

## Quick Start

### Running the Benchmark

```bash
git clone https://github.com/nambok/DeepMemEval.git
cd DeepMemEval
pip install -r requirements.txt

# Run your system
python run_deepmemeval.py \
  --adapter adapters/your_system.py \
  --dataset data/deepmemeval_500.json \
  --output results/your_system.json

# Evaluate
export OPENAI_API_KEY=your-key
python evaluate.py \
  --judge gpt-4o-2024-08-06 \
  --results results/your_system.json \
  --reference data/deepmemeval_500.json
```

### System Adapter Interface

Implement a simple Python adapter for your memory system:

```python
class MemorySystemAdapter:
    def ingest_session(self, session: dict, timestamp: str) -> None:
        """Ingest a conversation session at a given timestamp."""
        ...

    def query(self, question: str, timestamp: str = "now") -> str:
        """Query the memory system. Timestamp enables point-in-time queries."""
        ...

    def get_context_tokens(self) -> int:
        """Return the number of tokens in the last context assembly."""
        ...

    def reset(self) -> None:
        """Reset the memory system to empty state."""
        ...
```

See `adapters/` for reference implementations.

## Dataset

The dataset is released at `data/deepmemeval_500.json`.

Each scenario contains:

```json
{
  "scenario_id": "belief-p001-database",
  "scenario_type": "belief-update",
  "conversation_history": [...],
  "question": "What database does Alex Chen currently use?",
  "expected_answer": "Uses DuckDB for analytics workloads",
  "metadata": {
    "stale_answers": ["Uses PostgreSQL for the main application database", "Uses SQLite for the main application database"],
    "belief_timeline": [
      {"fact": "Uses PostgreSQL for the main application database", "valid_from": "2025-01-10", "valid_until": "2025-02-15"},
      {"fact": "Uses SQLite for the main application database", "valid_from": "2025-02-15", "valid_until": "2025-04-01"},
      {"fact": "Uses DuckDB for analytics workloads", "valid_from": "2025-04-01", "valid_until": null}
    ],
    "update_count": 2,
    "difficulty": "medium"
  }
}
```

### Dataset Generation

See `dataset_generation/` for the generation pipeline:

1. **Persona generation** (`generate_personas.py`) — 50 synthetic user personas with evolving technology timelines, supersession chains, and dependency annotations
2. **Scenario generation** (`generate_sample.py`) — produces 500 scenarios across all 6 categories from persona timelines, with balanced distribution and automated quality checks
3. **Hand-written seed personas** (`personas.py`) — 5 curated personas used as templates

## Limitations

- **Temporal Belief** is the least novel dimension — other benchmarks (agent-memory-eval, Engram) test temporal reasoning in some form, though DeepMemEval's "what was believed at time X" framing is more specific.
- **The dataset is programmatically generated**, not human-curated from real conversations. Scenarios are realistic but synthetic — real user conversations have messier language, topic drift, and ambiguity that templates don't fully capture.

## Citation

```bibtex
@software{deepmemeval2026,
  author = {Nam Rodriguez},
  title = {DeepMemEval: Benchmarking Belief Management, Memory Quality, and Context Efficiency in AI Agent Memory Systems},
  year = {2026},
  url = {https://github.com/nambok/DeepMemEval},
}
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
