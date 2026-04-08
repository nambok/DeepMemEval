# Dataset Specification

## Overview

The DeepMemEval dataset consists of 500 curated scenarios distributed across six categories. Each scenario tests a specific aspect of memory quality that is not covered by retrieval-focused benchmarks.

## Schema

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `scenario_id` | string | Unique identifier (e.g., `belief-001`, `cascade-042`) |
| `scenario_type` | string | One of: `belief-update`, `cascade-propagation`, `noise-resistance`, `temporal-belief`, `delta-efficiency`, `uncertainty-abstention` |
| `conversation_history` | array | Ordered list of sessions |
| `question` | string | The evaluation question |
| `expected_answer` | string | Ground-truth correct answer |
| `metadata` | object | Category-specific metadata (for evaluation only, NOT accessible during system execution) |

### Session Format

Each session in `conversation_history`:

```json
{
  "session_id": "s001",
  "date": "2025-01-15",
  "turns": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### Category-Specific Metadata

#### Belief Update

```json
{
  "stale_answers": ["PostgreSQL", "SQLite"],
  "belief_timeline": [
    {
      "fact": "Uses PostgreSQL",
      "valid_from": "2025-01-15",
      "valid_until": "2025-02-20",
      "source_session": "s001"
    }
  ],
  "update_count": 2,
  "difficulty": "medium"
}
```

#### Cascade Propagation

```json
{
  "root_change": "Switched backend from Python to Go",
  "root_change_session": "s007",
  "dependency_chain": [
    {"fact": "Uses Django", "depends_on": "Uses Python"},
    {"fact": "Uses pytest", "depends_on": "Uses Django"}
  ],
  "old_dependent": "pytest",
  "chain_depth": 2
}
```

#### Noise Resistance

```json
{
  "total_sessions": 80,
  "signal_sessions": ["s012", "s034", "s067"],
  "noise_sessions": 77,
  "signal_to_noise_ratio": 0.0375,
  "distractor_facts": ["User asked about Kubernetes once"],
  "sub_category": "chitchat-filtering"
}
```

#### Temporal Belief

```json
{
  "query_timestamp": "2025-04-15",
  "belief_at_timestamp": "Neovim",
  "current_belief": "VS Code",
  "belief_timeline": [...],
  "difficulty": "explicit-timestamp"
}
```

#### Delta Efficiency

```json
{
  "total_turns": 20,
  "established_facts_by_turn_5": ["user name", "project", "tech stack"],
  "new_facts_after_turn_5": [
    {"turn": 15, "fact": "Changed deployment target"}
  ]
}
```

#### Uncertainty Abstention

```json
{
  "uncertainty_reason": "Root fact changed, downstream belief never explicitly updated",
  "sub_category": "partially-invalidated",
  "conflicting_facts": ["Uses Docker", "Uses Podman"]
}
```

## Distribution

| Category | Count | Difficulty Distribution |
|----------|-------|------------------------|
| Belief Update | 100 | 30 easy, 40 medium, 30 hard |
| Cascade Propagation | 80 | 30 depth-1, 30 depth-2, 20 depth-3 |
| Noise Resistance | 80 | 20 per sub-category |
| Temporal Belief | 80 | 30 explicit, 25 relative, 25 implicit |
| Delta Efficiency | 80 | 40 stable-context, 40 evolving-context |
| Uncertainty Abstention | 80 | 20 per sub-category |

## Persona Pool

Scenarios are built from 100 synthetic user personas. Each persona has:

- Professional background (developer, designer, PM, data scientist, etc.)
- Technology preferences that evolve over time
- Project history with decisions, migrations, and changes
- Communication style (concise, verbose, technical, casual)

Persona definitions are in `dataset_generation/personas/`.
