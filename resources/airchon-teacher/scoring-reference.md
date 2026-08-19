# Scoring and Tier-Assignment Reference

Load-trigger: Read this file if you want to double-check the exact
scoring/tier-assignment mechanics behind Step 4 and Step 5 of
`classification-flow.md` (or the routed `grade`/`finalize` modes).
The rubric bullets and tier table already inline in those steps are
sufficient for normal grading -- this file is the illustrative
pseudocode underneath them, not new rules.

## Step 4 scoring logic

```python
def score_exam(responses, answer_key):
    """
    responses: dict of {question_id: user_answer}
    answer_key: dict of {question_id: {correct_answer: str, points: float}}
    """
    score = 0.0
    for q_id, answer in responses.items():
        if q_id in answer_key:
            # For CHOICE/SHORT: exact match or rubric-based
            # For ESSAY: instructor judgment (1.0 or 0.5 or 0.25)
            is_correct = evaluate_answer(answer, answer_key[q_id])
            if is_correct:
                score += answer_key[q_id]["points"]  # 0.25 per question
    return score  # 0.0-10.0
```

## Step 5 tier-assignment logic

```python
def assign_tier(score):
    """
    score: float 0.0-10.0
    Returns: tier_name (str), description (str), next_step (str)
    """
    if score < 6.0:
        return ("Slumberer", "Foundational", "Start with the Slumberer module cluster")
    elif 6.0 <= score <= 7.0:
        return ("Gnostic", "Intermediate", "Ready for hands-on design exercises")
    elif 7.1 <= score <= 8.0:
        return ("Demiurge", "Advanced", "Ready for architecture challenges")
    else:  # 8.1-10.0
        return ("Archon", "Mastery", "Ready for capstone projects and mentoring")
```
