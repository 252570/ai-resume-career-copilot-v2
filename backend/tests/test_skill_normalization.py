from app.services.matching import analyze_resume_job
from app.services.skill_normalization import canonical_skill_list


def test_canonical_skill_list_deduplicates_safe_aliases() -> None:
    assert canonical_skill_list(["Postgres", "PostgreSQL", "nodejs", "Node.js"]) == ["PostgreSQL", "Node.js"]


def test_matching_uses_aliases_but_keeps_job_label_and_evidence() -> None:
    result = analyze_resume_job(
        {"skills": ["Postgres", "nodejs"], "summary": ["Backend"], "experience": ["Built APIs"], "education": ["Degree"]},
        {"required_skills": ["PostgreSQL", "Node.js"], "preferred_skills": [], "experience_requirements": [], "education_requirements": []},
        "Built services with PostgreSQL and Node.js.\n",
    )

    assert result["matched_skills"] == ["PostgreSQL", "Node.js"]
    assert result["missing_skills"] == []
    assert result["resume_evidence"]["PostgreSQL"] == ["Built services with PostgreSQL and Node.js."]
