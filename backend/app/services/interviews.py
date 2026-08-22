from __future__ import annotations

import re


def generate_questions(job_data: dict[str, object], question_count: int) -> list[dict[str, object]]:
    title = str(job_data.get("job_title") or "this role")
    skills = list(job_data.get("required_skills") or []) + list(job_data.get("preferred_skills") or [])
    questions = [{"index": 0, "category": "motivation", "prompt": f"What interests you about {title}, and how does your experience prepare you for it?", "focus_skill": None}]
    for skill in dict.fromkeys(str(item) for item in skills):
        questions.append({"index": len(questions), "category": "technical", "prompt": f"Describe a specific situation where you used {skill}. What was your responsibility, what did you do, and what was the result?", "focus_skill": skill})
        if len(questions) >= question_count:
            return questions
    while len(questions) < question_count:
        questions.append({"index": len(questions), "category": "behavioral", "prompt": "Describe a difficult project decision. How did you evaluate options, communicate your choice, and measure the outcome?", "focus_skill": None})
    return questions


def evaluate_answer(answer: str, focus_skill: str | None) -> dict[str, object]:
    normalized = answer.lower()
    score = 0
    strengths: list[str] = []
    improvements: list[str] = []
    if len(answer.split()) >= 60:
        score += 35
        strengths.append("Provides enough detail to evaluate the example.")
    else:
        improvements.append("Add context, your specific actions, and a measurable outcome; aim for at least 60 words.")
    star_terms = ["situation", "task", "action", "result"]
    present_star = sum(term in normalized for term in star_terms)
    if present_star >= 2:
        score += 30
        strengths.append("Uses multiple STAR-style elements to structure the answer.")
    else:
        improvements.append("Make the narrative easier to follow with Situation, Task, Action, and Result elements.")
    if re.search(r"\b\d+(?:\.\d+)?%?\b", answer):
        score += 20
        strengths.append("Includes a concrete quantity or measurable result.")
    else:
        improvements.append("Where accurate, add a concrete measure such as time saved, scale, percentage, or team size.")
    if focus_skill and focus_skill.lower() in normalized:
        score += 15
        strengths.append(f"Directly connects the answer to the {focus_skill} focus area.")
    elif focus_skill:
        improvements.append(f"Name and explain how you used {focus_skill} in the example.")
    return {"score": score, "strengths": strengths, "improvements": improvements, "disclaimer": "This is deterministic structure feedback based on answer length, STAR cues, measurable language, and the stated focus skill. It is not an AI judgment of your interview performance."}
