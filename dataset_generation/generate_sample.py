"""Generate sample DeepMemEval scenarios from persona definitions.

Produces a proof-of-concept dataset with scenarios across all 6 categories.
"""

import json
import random
from datetime import datetime, timedelta

from personas import PERSONAS


random.seed(42)


def make_turns(user_msg: str, assistant_msg: str) -> list:
    return [
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": assistant_msg},
    ]


def generate_filler_session(session_id: str, date: str) -> dict:
    """Generate a realistic but irrelevant filler session."""
    fillers = [
        make_turns("Can you help me write a regex to match email addresses?",
                   "Sure! Here's a common pattern: `^[\\w.-]+@[\\w.-]+\\.\\w+$`. Want me to explain each part?"),
        make_turns("What's the difference between a stack and a queue?",
                   "A stack is LIFO (last in, first out) — think of a stack of plates. A queue is FIFO (first in, first out) — like a line at a store."),
        make_turns("How do I center a div in CSS?",
                   "The modern way is `display: flex; justify-content: center; align-items: center;` on the parent container."),
        make_turns("Can you explain what a closure is?",
                   "A closure is a function that captures variables from its surrounding scope. Even after the outer function returns, the inner function retains access to those variables."),
        make_turns("What's a good commit message format?",
                   "A common convention is: `type(scope): description`. For example: `fix(auth): handle expired tokens`. Keep the subject line under 72 characters."),
        make_turns("How do I read a file in Python?",
                   "Use `with open('file.txt', 'r') as f: content = f.read()`. The `with` statement ensures the file is properly closed."),
        make_turns("What's the weather like today?",
                   "I don't have access to real-time weather data, but you can check weather.com or use a weather API."),
        make_turns("Can you help me debug this error: KeyError 'user_id'?",
                   "A KeyError means the key doesn't exist in the dictionary. Check if 'user_id' is present before accessing it, or use `.get('user_id', default)`."),
        make_turns("What are some good VS Code extensions?",
                   "Popular ones include Prettier (formatting), ESLint (linting), GitLens (git history), and Thunder Client (API testing)."),
        make_turns("Explain Big O notation briefly",
                   "Big O describes how an algorithm's runtime grows with input size. O(1) is constant, O(n) is linear, O(n²) is quadratic. It measures the worst-case upper bound."),
    ]
    return {
        "session_id": session_id,
        "date": date,
        "turns": random.choice(fillers),
    }


def make_session(session_id: str, date: str, user_msg: str, assistant_msg: str) -> dict:
    return {
        "session_id": session_id,
        "date": date,
        "turns": make_turns(user_msg, assistant_msg),
    }


def generate_belief_update_scenarios(persona: dict) -> list:
    """Generate belief-update scenarios from a persona's timeline."""
    scenarios = []
    timeline = persona["timeline"]

    # Find facts with supersedes chains
    for i, entry in enumerate(timeline):
        if "supersedes" not in entry:
            continue

        chain = [entry]
        idx = entry["supersedes"]
        while idx is not None:
            chain.append(timeline[idx])
            idx = timeline[idx].get("supersedes")
        chain.reverse()

        if len(chain) < 2:
            continue

        # Build conversation history
        history = []
        for j, fact in enumerate(chain):
            ctx = fact.get("context", "")
            user_msg = fact["fact"]
            if ctx:
                user_msg = f"{fact['fact']}. {ctx}."
            assistant_msg = f"Got it, noted that you {fact['fact'].lower()}."
            history.append(make_session(f"s{j+1:03d}", fact["date"], user_msg, assistant_msg))

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
                        "valid_until": chain[k + 1]["date"] if k < len(chain) - 1 else None,
                        "source_session": f"s{k+1:03d}",
                    }
                    for k, f in enumerate(chain)
                ],
                "update_count": len(chain) - 1,
                "difficulty": difficulty,
            },
        })

    return scenarios


def generate_cascade_scenarios(persona: dict) -> list:
    """Generate cascade-propagation scenarios from dependency chains."""
    scenarios = []
    timeline = persona["timeline"]

    for i, entry in enumerate(timeline):
        if "depends_on" not in entry:
            continue

        # Find the root fact and check if it was superseded
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

        scenarios.append({
            "scenario_id": f"cascade-{persona['id']}-{entry['category']}",
            "scenario_type": "cascade-propagation",
            "conversation_history": history,
            "question": f"What {entry['category'].replace('_', ' ')} does {persona['name']} use for their backend?",
            "expected_answer": f"Uncertain — {entry['fact']} was specific to {original_root['fact']}, but they {latest_root['fact'].lower()}",
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


def generate_noise_scenarios(persona: dict) -> list:
    """Generate noise-resistance scenarios."""
    scenarios = []
    timeline = persona["timeline"]

    # Pick a stable fact (no supersedes)
    stable_facts = [t for t in timeline if "supersedes" not in t and t["category"] not in ("name", "team")]
    if not stable_facts:
        return []

    fact = stable_facts[0]
    base_date = datetime.strptime(fact["date"], "%Y-%m-%d")

    # Build history with signal buried in noise
    history = []
    signal_session = random.randint(5, 15)
    for j in range(20):
        session_date = (base_date + timedelta(days=j * 2)).strftime("%Y-%m-%d")
        if j == signal_session:
            history.append(make_session(
                f"s{j+1:03d}", session_date,
                fact["fact"], f"Noted, {fact['fact'].lower()}."))
        else:
            history.append(generate_filler_session(f"s{j+1:03d}", session_date))

    scenarios.append({
        "scenario_id": f"noise-{persona['id']}-{fact['category']}",
        "scenario_type": "noise-resistance",
        "conversation_history": history,
        "question": f"What is {persona['name']}'s {fact['category'].replace('_', ' ')} preference?",
        "expected_answer": fact["fact"],
        "metadata": {
            "total_sessions": 20,
            "signal_sessions": [f"s{signal_session+1:03d}"],
            "noise_sessions": 19,
            "signal_to_noise_ratio": 0.05,
            "sub_category": "chitchat-filtering",
        },
    })

    return scenarios


def generate_temporal_scenarios(persona: dict) -> list:
    """Generate temporal-belief scenarios."""
    scenarios = []
    timeline = persona["timeline"]

    for i, entry in enumerate(timeline):
        if "supersedes" not in entry:
            continue

        chain = [entry]
        idx = entry["supersedes"]
        while idx is not None:
            chain.append(timeline[idx])
            idx = timeline[idx].get("supersedes")
        chain.reverse()

        if len(chain) < 2:
            continue

        # Build history
        history = []
        for j, fact in enumerate(chain):
            history.append(make_session(
                f"s{j+1:03d}", fact["date"],
                fact["fact"], f"Got it, {fact['fact'].lower()}."))

        # Ask about a middle time point
        if len(chain) >= 2:
            first_date = datetime.strptime(chain[0]["date"], "%Y-%m-%d")
            second_date = datetime.strptime(chain[1]["date"], "%Y-%m-%d")
            query_date = first_date + (second_date - first_date) / 2
            query_date_str = query_date.strftime("%Y-%m-%d")

            scenarios.append({
                "scenario_id": f"temporal-{persona['id']}-{entry['category']}",
                "scenario_type": "temporal-belief",
                "conversation_history": history,
                "question": f"What {entry['category'].replace('_', ' ')} was {persona['name']} using around {query_date.strftime('%B %Y')}?",
                "expected_answer": chain[0]["fact"],
                "metadata": {
                    "query_timestamp": query_date_str,
                    "belief_at_timestamp": chain[0]["fact"],
                    "current_belief": chain[-1]["fact"],
                    "difficulty": "explicit-timestamp",
                },
            })

    return scenarios


def generate_delta_scenarios(persona: dict) -> list:
    """Generate delta-efficiency scenarios."""
    timeline = persona["timeline"]
    stable_facts = [t for t in timeline if "supersedes" not in t]

    if len(stable_facts) < 3:
        return []

    base_date = datetime.strptime(stable_facts[0]["date"], "%Y-%m-%d")
    history = []

    # 5 sessions establishing context
    for j, fact in enumerate(stable_facts[:5]):
        session_date = (base_date + timedelta(days=j)).strftime("%Y-%m-%d")
        history.append(make_session(
            f"s{j+1:03d}", session_date,
            fact["fact"], f"Noted."))

    # 15 follow-up sessions asking questions (context should be established)
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
            "established_facts_by_turn_5": [f["fact"] for f in stable_facts[:5]],
        },
    }]


def generate_uncertainty_scenarios(persona: dict) -> list:
    """Generate uncertainty-abstention scenarios."""
    scenarios = []
    timeline = persona["timeline"]

    # Find cascade invalidation cases
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

        scenarios.append({
            "scenario_id": f"uncertain-{persona['id']}-{entry['category']}",
            "scenario_type": "uncertainty-abstention",
            "conversation_history": history,
            "question": f"Does {persona['name']} still use {entry['fact'].split(' ')[-1]} for {entry['category'].replace('_', ' ')}?",
            "expected_answer": "Uncertain",
            "metadata": {
                "uncertainty_reason": f"Root fact changed ({original_root['fact']} → {latest_root['fact']}), dependent belief '{entry['fact']}' was never explicitly updated",
                "sub_category": "partially-invalidated",
            },
        })

    return scenarios


def main():
    all_scenarios = []

    for persona in PERSONAS:
        all_scenarios.extend(generate_belief_update_scenarios(persona))
        all_scenarios.extend(generate_cascade_scenarios(persona))
        all_scenarios.extend(generate_noise_scenarios(persona))
        all_scenarios.extend(generate_temporal_scenarios(persona))
        all_scenarios.extend(generate_delta_scenarios(persona))
        all_scenarios.extend(generate_uncertainty_scenarios(persona))

    # Summary
    by_type = {}
    for s in all_scenarios:
        t = s["scenario_type"]
        by_type[t] = by_type.get(t, 0) + 1

    print(f"Generated {len(all_scenarios)} scenarios:")
    for t, count in sorted(by_type.items()):
        print(f"  {t}: {count}")

    output_path = "../data/deepmemeval_sample.json"
    with open(output_path, "w") as f:
        json.dump(all_scenarios, f, indent=2)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
