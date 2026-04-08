## Description

<!-- What does this PR do? Keep it brief. -->

## Type

- [ ] New adapter (memory system integration)
- [ ] New scenarios (dataset expansion)
- [ ] Bug fix (evaluation harness, scoring, adapter interface)
- [ ] Documentation
- [ ] Other

## Checklist

- [ ] `python3 dataset_generation/generate_sample.py` runs without errors (if dataset changes)
- [ ] No duplicate scenario IDs (`scenario_id` is unique across the full dataset)
- [ ] All facts are phrased as **states**, not actions (e.g., "Uses X" not "Switched to X")
- [ ] Oracle fields (`belief_timeline`, `stale_answers`, `metadata`) are not accessed during system execution
- [ ] Adapter implements all 4 methods: `ingest_session`, `query`, `get_context_tokens`, `reset`

## New Adapter Checklist (if applicable)

- [ ] Adapter file added to `adapters/`
- [ ] System name and version documented in adapter docstring
- [ ] Baseline results included in `results/`
- [ ] Results JSON includes full system configuration
