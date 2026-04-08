"""Judge prompt templates for each DeepMemEval category.

Per-category prompt templates with GPT-4o judge, temperature=0, binary yes/no.
"""

JUDGE_PROMPTS = {
    "belief-update": (
        "I will give you a question, the current correct answer, a list of stale answers "
        "that should NOT appear, and a response from a memory system. The correct answer "
        "reflects the CURRENT state after all updates. Please answer yes if the response "
        "contains the current correct answer and does NOT include any stale answers. If the "
        "response includes both current and stale information, answer no. If the response "
        "only contains stale information, answer no.\n\n"
        "Question: {question}\n"
        "Current Correct Answer: {expected_answer}\n"
        "Stale Answers (should NOT appear): {stale_answers}\n"
        "System Response: {response}\n\n"
        "Is the system response correct and free of stale information? Answer yes or no only."
    ),
    "cascade-propagation": (
        "I will give you a question about a downstream belief that depends on a root fact "
        "that has changed. The root fact change was: {root_change}. The question asks about "
        "a dependent belief that was never explicitly updated. Please answer yes if the system "
        "correctly expresses uncertainty or acknowledges that the dependent information may be "
        "outdated. Answer no if the system returns the old dependent belief with confidence.\n\n"
        "Question: {question}\n"
        "Root Fact Change: {root_change}\n"
        "Old Dependent Belief: {old_dependent}\n"
        "System Response: {response}\n\n"
        "Does the system appropriately handle the invalidated dependent belief? "
        "Answer yes or no only."
    ),
    "noise-resistance": (
        "I will give you a question, a correct answer, and a response from a memory system. "
        "The correct answer is a specific fact stated by the user in conversation. Please "
        "answer yes if the response contains the correct answer. Otherwise, answer no. If the "
        "response contains additional information alongside the correct answer, it should still "
        "be considered correct as long as the actual answer is present.\n\n"
        "Question: {question}\n"
        "Correct Answer: {expected_answer}\n"
        "System Response: {response}\n\n"
        "Is the system response correct? Answer yes or no only."
    ),
    "temporal-belief": (
        "I will give you a question about what was believed at a specific point in time, the "
        "correct answer for that time period, and a response from a memory system. Please "
        "answer yes if the response contains the answer that was correct AT THE SPECIFIED TIME. "
        "The answer may differ from the current state. Answer no if the response gives the "
        "current answer when the question asks about a past state, or vice versa.\n\n"
        "Question: {question}\n"
        "Correct Answer (at specified time): {expected_answer}\n"
        "System Response: {response}\n\n"
        "Is the system response correct for the specified time period? Answer yes or no only."
    ),
    "uncertainty-abstention": (
        "I will give you a question where the correct behavior is to express uncertainty. The "
        "underlying fact is ambiguous, partially invalidated, or conflicting. Please answer yes "
        "if the system expresses appropriate uncertainty, hedges its answer, or asks for "
        "clarification. Answer no if the system returns a definitive answer without acknowledging "
        "the uncertainty.\n\n"
        "Question: {question}\n"
        "Reason for uncertainty: {uncertainty_reason}\n"
        "System Response: {response}\n\n"
        "Does the system appropriately express uncertainty? Answer yes or no only."
    ),
}

CATEGORY_WEIGHTS = {
    "belief-update": 0.25,
    "cascade-propagation": 0.15,
    "noise-resistance": 0.20,
    "temporal-belief": 0.15,
    "delta-efficiency": 0.10,
    "uncertainty-abstention": 0.15,
}
