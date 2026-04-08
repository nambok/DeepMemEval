# Dataset Generation Pipeline

## Overview

The DeepMemEval dataset is generated through a 5-phase pipeline that produces 500 curated scenarios with ground-truth belief timelines.

## Phases

### Phase 1: Persona Generation

Create 100 synthetic user personas with:
- Professional background (developer, designer, PM, data scientist, devops, etc.)
- Technology preferences that evolve over time
- Project history with decisions, migrations, and tool changes
- Communication style variations

Each persona is defined in `personas/` as a JSON file with a timeline of facts and decisions.

### Phase 2: Belief Timeline Construction

For each persona, construct a ground-truth belief timeline:
- Each belief has: `fact`, `valid_from`, `valid_until`, `source_session`, `superseded_by`
- Dependency chains are annotated (fact A depends on fact B)
- Contradiction pairs are explicitly marked

Output: `timelines/` directory with per-persona belief graphs.

### Phase 3: Conversation Generation

Generate realistic multi-session conversations:
- LLM-generated (GPT-4o) with human editing for naturalness
- Facts are embedded naturally in conversation flow
- Updates use varied language (explicit: "I switched to X", implicit: "we ended up going with X")
- Session dates are realistic (days to weeks apart)

### Phase 4: Noise Injection

For noise-resistance scenarios:
- Filler sessions sourced from ShareGPT and UltraChat (same as LongMemEval)
- Signal-to-noise ratio controlled per scenario
- Automated check: no filler session accidentally contains answer information
- Distractor facts injected at controlled similarity to real facts

### Phase 5: Validation

Quality assurance:
- 3 human evaluators independently answer 50-question sample
- Inter-annotator agreement > 0.9 required
- Judge prompt validation: run judge on known-correct and known-incorrect responses
- Edge case review: verify temporal boundary cases, cascade chain correctness

## Running

```bash
# Generate personas
python generate_personas.py --count 100 --output personas/

# Build belief timelines
python build_timelines.py --personas personas/ --output timelines/

# Generate conversations
python generate_conversations.py --timelines timelines/ --output conversations/

# Assemble scenarios with noise injection
python assemble_scenarios.py \
    --conversations conversations/ \
    --timelines timelines/ \
    --noise-source data/filler_sessions.json \
    --output data/deepmemeval_500.json

# Validate
python validate_dataset.py --dataset data/deepmemeval_500.json
```
