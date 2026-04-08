# Dataset Generation Pipeline

## Overview

The DeepMemEval dataset is generated through a programmatic pipeline that produces 500 scenarios with ground-truth belief timelines from 50 synthetic personas.

## Pipeline

### Step 1: Persona Generation (`generate_personas.py`)

Programmatically generates 50 diverse personas by combining:
- 50 unique name combinations from name pools
- 15 professional roles (backend, frontend, devops, data science, PM, mobile, security, etc.)
- 6 technology stack templates with realistic supersession chains and dependency edges
- 30 company profiles

Each persona has 8–14 timeline entries including:
- Supersession chains (PostgreSQL → SQLite → DuckDB)
- Dependency edges (pytest depends on Python — if language changes, testing is uncertain)
- Stable facts (deployment, auth, monitoring — never change)
- Identity (name, team, company)

### Step 2: Scenario Generation (`generate_sample.py`)

Generates scenarios across all 6 categories from persona timelines:
- **Belief Update** — one per supersession chain (longest chain per category)
- **Cascade Propagation** — one per dependency edge where root was superseded
- **Noise Resistance** — 1–2 per persona, signal buried in 20–40 filler sessions
- **Temporal Belief** — one per supersession chain, querying a past time point
- **Delta Efficiency** — one per persona, measuring token counts over 20 turns
- **Uncertainty Abstention** — one per dependency edge invalidated by root change

Raw generation produces ~730 scenarios. A balancing step trims to the target distribution (100/80/80/80/80/80 = 500).

### Hand-Written Seed Personas (`personas.py`)

5 hand-curated personas (Alex Chen, Maria Santos, James Kim, Priya Patel, Tom O'Brien) serve as readable examples and validation fixtures.

## Running

```bash
# Generate the full 500-scenario dataset
cd dataset_generation
python3 generate_sample.py

# Output:
#   ../data/deepmemeval_500.json (full dataset)
#   ../data/deepmemeval_sample.json (10-scenario sample)
```

## Filler Content

Noise-resistance scenarios use 20 hand-written filler conversations (coding questions, general Q&A) embedded directly in `generate_sample.py`. These are generic and contain no overlap with persona facts.
