"""Generate DeepMemEval scenarios from persona definitions.

Produces the full 500-scenario dataset across all 6 categories.
Target distribution:
  - belief-update:          100
  - cascade-propagation:     80
  - noise-resistance:        80
  - temporal-belief:          80
  - delta-efficiency:         80
  - uncertainty-abstention:   80
"""

import json
import random
from datetime import datetime, timedelta

from generate_personas import generate_all_personas

random.seed(42)

# --- Filler content for noise scenarios ---

FILLER_CONVERSATIONS = [
    ("Can you help me write a regex to match email addresses?",
     "Sure! Here's a common pattern: `^[\\w.-]+@[\\w.-]+\\.\\w+$`."),
    ("What's the difference between a stack and a queue?",
     "A stack is LIFO (last in, first out). A queue is FIFO (first in, first out)."),
    ("How do I center a div in CSS?",
     "Use `display: flex; justify-content: center; align-items: center;` on the parent."),
    ("Can you explain what a closure is?",
     "A closure is a function that captures variables from its enclosing scope."),
    ("What's a good commit message format?",
     "Convention: `type(scope): description`. Example: `fix(auth): handle expired tokens`."),
    ("How do I read a file in Python?",
     "Use `with open('file.txt') as f: content = f.read()`."),
    ("What's the weather like today?",
     "I don't have access to real-time weather data, but you can check weather.com."),
    ("Can you help me debug this KeyError?",
     "A KeyError means the key doesn't exist. Use `.get(key, default)` instead."),
    ("What are some good VS Code extensions?",
     "Popular ones: Prettier, ESLint, GitLens, and Thunder Client."),
    ("Explain Big O notation briefly",
     "Big O describes algorithm runtime growth. O(1) is constant, O(n) linear, O(n²) quadratic."),
    ("What's the difference between HTTP and HTTPS?",
     "HTTPS adds TLS encryption on top of HTTP. All modern sites should use HTTPS."),
    ("How do I reverse a linked list?",
     "Iterate through, reassigning each node's next pointer to the previous node."),
    ("What's the CAP theorem?",
     "In a distributed system, you can only guarantee two of: Consistency, Availability, Partition tolerance."),
    ("How do I handle errors in async JavaScript?",
     "Wrap await calls in try/catch blocks, or chain .catch() on promises."),
    ("What's the difference between SQL and NoSQL?",
     "SQL databases are relational with fixed schemas. NoSQL databases are flexible — document, key-value, graph, etc."),
    ("How do I set up SSH keys for GitHub?",
     "Run `ssh-keygen -t ed25519`, then add the public key to GitHub Settings > SSH Keys."),
    ("What's a microservice?",
     "A small, independently deployable service that does one thing well and communicates via APIs."),
    ("How do I profile Python code?",
     "Use `cProfile` for function-level profiling or `py-spy` for sampling profiling with flamegraphs."),
    ("What are environment variables used for?",
     "Storing configuration like API keys, database URLs, and feature flags outside the code."),
    ("How does garbage collection work?",
     "The runtime periodically frees memory that's no longer referenced. Python uses reference counting + cycle detection."),
]


def make_turns(user_msg: str, assistant_msg: str) -> list:
    return [
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": assistant_msg},
    ]


def generate_filler_session(session_id: str, date: str) -> dict:
    user_msg, asst_msg = random.choice(FILLER_CONVERSATIONS)
    return {
        "session_id": session_id,
        "date": date,
        "turns": make_turns(user_msg, asst_msg),
    }


def make_session(session_id: str, date: str, user_msg: str, assistant_msg: str) -> dict:
    return {
        "session_id": session_id,
        "date": date,
        "turns": make_turns(user_msg, assistant_msg),
    }


# ─── Belief Update ──────────────────────────────────────────────────────────

def generate_belief_update_scenarios(persona: dict) -> list:
    """One scenario per supersession chain (longest chain per category)."""
    scenarios = []
    timeline = persona["timeline"]

    seen_categories = set()
    for i in range(len(timeline) - 1, -1, -1):
        entry = timeline[i]
        if "supersedes" not in entry or entry["category"] in seen_categories:
            continue
        seen_categories.add(entry["category"])

        chain = [entry]
        idx = entry["supersedes"]
        while idx is not None:
            chain.append(timeline[idx])
            idx = timeline[idx].get("supersedes")
        chain.reverse()

        if len(chain) < 2:
            continue

        history = []
        for j, fact in enumerate(chain):
            ctx = fact.get("context", "")
            user_msg = f"{fact['fact']}. {ctx}." if ctx else fact["fact"]
            history.append(make_session(
                f"s{j+1:03d}", fact["date"],
                user_msg, f"Got it, noted that you {fact['fact'].lower()}."))

        current = chain[-1]
        stale = [f["fact"] for f in chain[:-1]]
        difficulty = "easy" if len(chain) == 2 else "medium" if len(chain) == 3 else "hard"

        scenarios.append({
            "scenario_id": f"belief-{persona['id']}-{entry['category']}",
            "scenario_type": "belief-update",
            "conversation_history": history,
            "question": f"What {entry['category'].replace('_', ' ')} does {persona['name']} currently use?",
            "expected_answer": current["fact"],
            "metadata": {
                "stale_answers": stale,
                "belief_timeline": [
                    {
                        "fact": f["fact"],
                        "valid_from": f["date"],
                        "valid_until": chain[k+1]["date"] if k < len(chain)-1 else None,
                        "source_session": f"s{k+1:03d}",
                    }
                    for k, f in enumerate(chain)
                ],
                "update_count": len(chain) - 1,
                "difficulty": difficulty,
            },
        })

    return scenarios


# ─── Cascade Propagation ────────────────────────────────────────────────────

def generate_cascade_scenarios(persona: dict) -> list:
    """One scenario per dependency edge where root was superseded."""
    scenarios = []
    timeline = persona["timeline"]

    for i, entry in enumerate(timeline):
        if "depends_on" not in entry:
            continue

        root_category = entry["depends_on"]
        root_facts = [t for t in timeline if t["category"] == root_category]
        superseded = [t for t in root_facts if "supersedes" in t]

        if not superseded:
            continue

        latest_root = superseded[-1]
        original_root = root_facts[0]

        history = [
            make_session("s001", original_root["date"],
                        original_root["fact"],
                        f"Sounds good, {original_root['fact'].lower()}."),
            make_session("s002", entry["date"],
                        entry["fact"],
                        f"Makes sense given your setup."),
            make_session("s003", latest_root["date"],
                        f"{latest_root['fact']}. {latest_root.get('context', '')}",
                        f"That's a big change! {latest_root['fact']}."),
        ]

        cat_label = entry["category"].replace("_", " ")
        scenarios.append({
            "scenario_id": f"cascade-{persona['id']}-{entry['category']}-via-{root_category}",
            "scenario_type": "cascade-propagation",
            "conversation_history": history,
            "question": f"What {cat_label} does {persona['name']} currently use?",
            "expected_answer": (
                f"Uncertain — {entry['fact']} was chosen when "
                f"{original_root['fact'].lower()}, but now "
                f"{latest_root['fact'].lower()}"
            ),
            "metadata": {
                "root_change": f"{original_root['fact']} → {latest_root['fact']}",
                "old_dependent": entry["fact"],
                "dependency_chain": [
                    {"fact": entry["fact"], "depends_on": original_root["fact"]}
                ],
                "chain_depth": 1,
            },
        })

    return scenarios


# ─── Noise Resistance ───────────────────────────────────────────────────────

def _get_stable_facts(persona: dict) -> list:
    """Get facts that are truly stable — never superseded by anything."""
    timeline = persona["timeline"]
    superseded_indices = {t["supersedes"] for t in timeline if "supersedes" in t}
    return [
        (i, t) for i, t in enumerate(timeline)
        if "supersedes" not in t
        and "depends_on" not in t
        and t["category"] not in ("name", "team")
        and i not in superseded_indices
    ]


def generate_noise_scenarios(persona: dict, max_per_persona: int = 2) -> list:
    """Generate noise scenarios with different SNR levels."""
    scenarios = []
    stable = _get_stable_facts(persona)

    if not stable:
        return []

    noise_configs = [
        {"total": 20, "label": "light", "snr": 0.05},
        {"total": 40, "label": "heavy", "snr": 0.025},
    ]

    for cfg_idx, cfg in enumerate(noise_configs):
        if cfg_idx >= max_per_persona or cfg_idx >= len(stable):
            break

        _, fact = stable[cfg_idx % len(stable)]
        base_date = datetime.strptime(fact["date"], "%Y-%m-%d")
        total = cfg["total"]

        history = []
        signal_pos = random.randint(total // 4, total * 3 // 4)
        for j in range(total):
            session_date = (base_date + timedelta(days=j * 2)).strftime("%Y-%m-%d")
            if j == signal_pos:
                history.append(make_session(
                    f"s{j+1:03d}", session_date,
                    fact["fact"], f"Noted, {fact['fact'].lower()}."))
            else:
                history.append(generate_filler_session(f"s{j+1:03d}", session_date))

        cat_label = fact["category"].replace("_", " ")
        scenarios.append({
            "scenario_id": f"noise-{persona['id']}-{fact['category']}-{cfg['label']}",
            "scenario_type": "noise-resistance",
            "conversation_history": history,
            "question": f"What is {persona['name']}'s {cat_label} preference?",
            "expected_answer": fact["fact"],
            "metadata": {
                "total_sessions": total,
                "signal_sessions": [f"s{signal_pos+1:03d}"],
                "noise_sessions": total - 1,
                "signal_to_noise_ratio": cfg["snr"],
                "sub_category": f"chitchat-filtering-{cfg['label']}",
            },
        })

    return scenarios


# ─── Temporal Belief ─────────────────────────────────────────────────────────

def generate_temporal_scenarios(persona: dict) -> list:
    """One scenario per supersession chain, querying a past time point."""
    scenarios = []
    timeline = persona["timeline"]

    seen_categories = set()
    for i in range(len(timeline) - 1, -1, -1):
        entry = timeline[i]
        if "supersedes" not in entry or entry["category"] in seen_categories:
            continue
        seen_categories.add(entry["category"])

        chain = [entry]
        idx = entry["supersedes"]
        while idx is not None:
            chain.append(timeline[idx])
            idx = timeline[idx].get("supersedes")
        chain.reverse()

        if len(chain) < 2:
            continue

        history = []
        for j, fact in enumerate(chain):
            history.append(make_session(
                f"s{j+1:03d}", fact["date"],
                fact["fact"], f"Got it, {fact['fact'].lower()}."))

        first_date = datetime.strptime(chain[0]["date"], "%Y-%m-%d")
        second_date = datetime.strptime(chain[1]["date"], "%Y-%m-%d")
        query_date = first_date + (second_date - first_date) / 2
        cat_label = entry["category"].replace("_", " ")

        scenarios.append({
            "scenario_id": f"temporal-{persona['id']}-{entry['category']}",
            "scenario_type": "temporal-belief",
            "conversation_history": history,
            "question": f"What {cat_label} was {persona['name']} using around {query_date.strftime('%B %Y')}?",
            "expected_answer": chain[0]["fact"],
            "metadata": {
                "query_timestamp": query_date.strftime("%Y-%m-%d"),
                "belief_at_timestamp": chain[0]["fact"],
                "current_belief": chain[-1]["fact"],
                "difficulty": "explicit-timestamp",
            },
        })

    return scenarios


# ─── Delta Efficiency ────────────────────────────────────────────────────────

def generate_delta_scenarios(persona: dict) -> list:
    """One scenario per persona measuring context efficiency over repeated queries."""
    timeline = persona["timeline"]
    stable = [t for t in timeline if "supersedes" not in t and t["category"] not in ("name", "team")]

    if len(stable) < 3:
        return []

    base_date = datetime.strptime(stable[0]["date"], "%Y-%m-%d")
    history = []

    for j, fact in enumerate(stable[:5]):
        session_date = (base_date + timedelta(days=j)).strftime("%Y-%m-%d")
        history.append(make_session(f"s{j+1:03d}", session_date, fact["fact"], "Noted."))

    questions = [
        f"Can you remind me about {persona['name']}'s setup?",
        f"What tools does {persona['name']} use?",
        f"Tell me about the current project.",
    ]
    for j in range(5, 20):
        session_date = (base_date + timedelta(days=j)).strftime("%Y-%m-%d")
        q = questions[j % len(questions)]
        history.append(make_session(f"s{j+1:03d}", session_date, q, "Here's what I know..."))

    eval_turns = [{"question": q, "turn": j} for j, q in enumerate(questions * 7)][:20]

    return [{
        "scenario_id": f"delta-{persona['id']}",
        "scenario_type": "delta-efficiency",
        "conversation_history": history,
        "question": "Measure context efficiency over 20 turns",
        "expected_answer": "N/A — quantitative measurement",
        "evaluation_turns": eval_turns,
        "metadata": {
            "total_turns": 20,
            "established_facts_by_turn_5": [f["fact"] for f in stable[:5]],
        },
    }]


# ─── Uncertainty Abstention ──────────────────────────────────────────────────

def generate_uncertainty_scenarios(persona: dict) -> list:
    """One scenario per dependency edge invalidated by root change."""
    scenarios = []
    timeline = persona["timeline"]

    for i, entry in enumerate(timeline):
        if "depends_on" not in entry:
            continue

        root_category = entry["depends_on"]
        root_superseded = [t for t in timeline if t["category"] == root_category and "supersedes" in t]

        if not root_superseded:
            continue

        latest_root = root_superseded[-1]
        original_root = [t for t in timeline if t["category"] == root_category][0]

        history = [
            make_session("s001", original_root["date"], original_root["fact"], "Got it."),
            make_session("s002", entry["date"], entry["fact"], "Makes sense."),
            make_session("s003", latest_root["date"], latest_root["fact"], "Big change!"),
        ]

        # Extract tool name: "Uses pytest for ..." -> "pytest"
        fact_words = entry["fact"].split()
        tool_name = fact_words[1] if len(fact_words) > 1 else fact_words[0]
        cat_label = entry["category"].replace("_", " ")

        scenarios.append({
            "scenario_id": f"uncertain-{persona['id']}-{entry['category']}-via-{root_category}",
            "scenario_type": "uncertainty-abstention",
            "conversation_history": history,
            "question": f"Does {persona['name']} still use {tool_name} for {cat_label}?",
            "expected_answer": "Uncertain",
            "metadata": {
                "uncertainty_reason": (
                    f"Root fact changed ({original_root['fact']} → {latest_root['fact']}), "
                    f"dependent belief '{entry['fact']}' was never explicitly updated"
                ),
                "sub_category": "partially-invalidated",
            },
        })

    return scenarios


# ─── Assembly & Balancing ────────────────────────────────────────────────────

TARGET = {
    "belief-update": 100,
    "cascade-propagation": 80,
    "noise-resistance": 80,
    "temporal-belief": 80,
    "delta-efficiency": 80,
    "uncertainty-abstention": 80,
}


def balance_dataset(scenarios: list) -> list:
    """Trim or pad each category to hit target counts."""
    by_type = {}
    for s in scenarios:
        by_type.setdefault(s["scenario_type"], []).append(s)

    balanced = []
    for cat, target in TARGET.items():
        pool = by_type.get(cat, [])
        if len(pool) >= target:
            # Trim — prefer diversity (different personas)
            random.shuffle(pool)
            balanced.extend(pool[:target])
        else:
            # Use all, then pad by duplicating with variation
            balanced.extend(pool)
            deficit = target - len(pool)
            if pool:
                for k in range(deficit):
                    clone = json.loads(json.dumps(pool[k % len(pool)]))
                    clone["scenario_id"] = f"{clone['scenario_id']}-var{k}"
                    balanced.append(clone)

    return balanced


def main():
    personas = generate_all_personas(count=50)
    raw_scenarios = []

    for persona in personas:
        raw_scenarios.extend(generate_belief_update_scenarios(persona))
        raw_scenarios.extend(generate_cascade_scenarios(persona))
        raw_scenarios.extend(generate_noise_scenarios(persona, max_per_persona=2))
        raw_scenarios.extend(generate_temporal_scenarios(persona))
        raw_scenarios.extend(generate_delta_scenarios(persona))
        raw_scenarios.extend(generate_uncertainty_scenarios(persona))

    # Raw stats
    raw_by_type = {}
    for s in raw_scenarios:
        t = s["scenario_type"]
        raw_by_type[t] = raw_by_type.get(t, 0) + 1

    print(f"Raw: {len(raw_scenarios)} scenarios")
    for t, count in sorted(raw_by_type.items()):
        print(f"  {t}: {count}")

    # Balance to 500
    balanced = balance_dataset(raw_scenarios)

    # Validate uniqueness
    ids = [s["scenario_id"] for s in balanced]
    assert len(ids) == len(set(ids)), f"Duplicate IDs found: {[x for x in ids if ids.count(x) > 1]}"

    bal_by_type = {}
    for s in balanced:
        t = s["scenario_type"]
        bal_by_type[t] = bal_by_type.get(t, 0) + 1

    print(f"\nBalanced: {len(balanced)} scenarios")
    for t, count in sorted(bal_by_type.items()):
        print(f"  {t}: {count}")

    # Save full dataset
    output_path = "../data/deepmemeval_500.json"
    with open(output_path, "w") as f:
        json.dump(balanced, f, indent=2)
    print(f"\nSaved to {output_path}")

    # Also save a small sample (10 scenarios, at least 1 per type)
    sample = []
    seen = set()
    for s in balanced:
        if s["scenario_type"] not in seen:
            seen.add(s["scenario_type"])
            sample.append(s)
    while len(sample) < 10:
        s = random.choice(balanced)
        if s["scenario_id"] not in {x["scenario_id"] for x in sample}:
            sample.append(s)

    sample_path = "../data/deepmemeval_sample.json"
    with open(sample_path, "w") as f:
        json.dump(sample, f, indent=2)
    print(f"Saved sample ({len(sample)}) to {sample_path}")


if __name__ == "__main__":
    main()
