# Contributing to DeepMemEval

Thanks for your interest in contributing. DeepMemEval is an open benchmark — contributions that improve rigor, coverage, and fairness are welcome.

## Ways to Contribute

### 1. Add a Memory System Adapter

The most impactful contribution is running the benchmark against a new memory system.

```python
# adapters/your_system.py
from src.adapter import MemorySystemAdapter

class YourSystemAdapter(MemorySystemAdapter):
    def ingest_session(self, session: dict, timestamp: str) -> None:
        """Ingest a conversation session at a given timestamp."""
        ...

    def query(self, question: str, timestamp: str = "now") -> str:
        """Query the memory system."""
        ...

    def get_context_tokens(self) -> int:
        """Return token count from the last context assembly."""
        ...

    def reset(self) -> None:
        """Reset to empty state."""
        ...
```

**Rules for adapter submissions:**
- Adapter must work with `run_deepmemeval.py` without modification
- Include a results JSON from a full 500-scenario run
- Document the system version, model, and embedding provider used
- Do not access oracle fields (`belief_timeline`, `stale_answers`, scenario `metadata`)

### 2. Expand the Dataset

Add new scenarios that test edge cases not covered by the current 500.

**Requirements:**
- All facts must be phrased as **states** ("Uses PostgreSQL for the database"), never as actions ("Switched to PostgreSQL")
- Scenario IDs must be unique across the full dataset
- Each scenario must include ground-truth metadata for evaluation
- Run `python3 dataset_generation/generate_sample.py` and verify no errors

### 3. Improve the Evaluation Harness

Fix bugs or improve the scoring logic in `evaluate.py` and `run_deepmemeval.py`.

**Be careful with:**
- Judge prompt changes — even small wording changes affect scores. Open an issue first to discuss.
- Scoring formula changes — these invalidate prior results. Requires strong justification.

### 4. Documentation

Clarify methodology, add examples, improve the README.

## Development Setup

```bash
git clone https://github.com/nambok/DeepMemEval.git
cd DeepMemEval
pip install -r requirements.txt

# Generate dataset from personas
cd dataset_generation
python3 generate_sample.py

# Run the sample (requires an adapter)
cd ..
python3 run_deepmemeval.py \
  --adapter adapters/chromadb_baseline.py \
  --dataset data/deepmemeval_sample.json \
  --output results/test_run.json
```

## Project Structure

```
DeepMemEval/
├── src/                    # Core library
│   ├── adapter.py          # MemorySystemAdapter ABC
│   └── prompts.py          # Judge prompt templates + category weights
├── adapters/               # Memory system adapters
│   └── chromadb_baseline.py
├── data/                   # Dataset files
│   ├── deepmemeval_500.json
│   └── deepmemeval_sample.json
├── dataset_generation/     # Persona + scenario generators
│   ├── generate_personas.py
│   ├── generate_sample.py
│   └── personas.py
├── docs/                   # Methodology + dataset spec
│   ├── methodology.md
│   └── dataset-spec.md
├── results/                # Benchmark results
├── evaluate.py             # GPT-4o judge evaluation
└── run_deepmemeval.py      # Benchmark runner
```

## Code Style

- Python 3.10+
- No external linter enforced — keep it readable
- Docstrings on public functions
- Comments only where non-obvious

## Submitting Results

If you've run the benchmark against a system, submit results as a PR:

1. Add your adapter to `adapters/`
2. Add your full results JSON to `results/`
3. Include in the PR description:
   - System name and version
   - Model and embedding provider
   - Composite score and per-category breakdown
   - Any notable observations

## Reporting Issues

- **Scoring bugs** — include the scenario ID, system response, and expected vs actual verdict
- **Dataset issues** — include the scenario ID and what's wrong with it
- **Adapter issues** — include the adapter name and error traceback

## License

By contributing, you agree that your contributions will be licensed under Apache 2.0.
