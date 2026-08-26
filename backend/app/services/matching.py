from __future__ import annotations

import re
from typing import Any

from app.schemas.analysis import SkillGap
from app.services.skill_normalization import canonical_skill_key, canonical_skill_list


def analyze_resume_job(resume_data: dict[str, Any], job_data: dict[str, Any], extracted_text: str) -> dict[str, Any]:
    """Produce a transparent, rule-based comparison; no model inference is used."""
    resume_skills = canonical_skill_list(list(resume_data.get("skills", [])))
    resume_skill_keys = {canonical_skill_key(skill) for skill in resume_skills}
    required = canonical_skill_list(list(job_data.get("required_skills", [])))
    preferred = [skill for skill in canonical_skill_list(list(job_data.get("preferred_skills", []))) if skill not in required]
    matched_required = [skill for skill in required if canonical_skill_key(skill) in resume_skill_keys]
    matched_preferred = [skill for skill in preferred if canonical_skill_key(skill) in resume_skill_keys]
    missing_required = [skill for skill in required if canonical_skill_key(skill) not in resume_skill_keys]
    missing_preferred = [skill for skill in preferred if canonical_skill_key(skill) not in resume_skill_keys]
    required_score = 70.0 * _coverage(len(matched_required), len(required))
    preferred_score = 20.0 * _coverage(len(matched_preferred), len(preferred))
    completeness_checks = [bool(resume_data.get(key)) for key in ("summary", "experience", "education")]
    completeness_score = 10.0 * (sum(completeness_checks) / len(completeness_checks))
    score_breakdown = {
        "required_skill_coverage": round(required_score, 2),
        "preferred_skill_coverage": round(preferred_score, 2),
        "resume_section_completeness": round(completeness_score, 2),
    }
    matched_skills = matched_required + matched_preferred
    evidence = {skill: _evidence_lines(extracted_text, skill) for skill in matched_skills}
    gaps = [
        SkillGap(skill=skill, requirement_type="required", priority="critical", job_evidence=f"Required skill: {skill}")
        for skill in missing_required
    ] + [
        SkillGap(skill=skill, requirement_type="preferred", priority="moderate", job_evidence=f"Preferred skill: {skill}")
        for skill in missing_preferred
    ]
    ats = _ats_analysis(resume_data, job_data, resume_skill_keys, required, preferred, missing_required, missing_preferred, extracted_text)
    return {
        "match_score": round(sum(score_breakdown.values()), 2),
        "score_breakdown": score_breakdown,
        "matched_skills": matched_skills,
        "missing_skills": missing_required + missing_preferred,
        "partially_matched_areas": _partial_areas(resume_data, job_data),
        "resume_evidence": evidence,
        "ats": ats,
        "skill_gaps": [gap.model_dump() for gap in gaps],
    }


def _coverage(matched: int, total: int) -> float:
    return 1.0 if total == 0 else matched / total


_EVIDENCE_ALIASES = {
    "PostgreSQL": ("postgresql", "postgres"),
    "Node.js": ("node\\.?js", "nodejs"),
    "React": ("react\\.?js", "reactjs", "react"),
    "REST APIs": ("restful?\\s+apis?", "rest\\s+apis?"),
    "Kubernetes": ("kubernetes", "k8s"),
    "scikit-learn": ("scikit[- ]learn", "sklearn"),
    "GCP": ("gcp", "google\\s+cloud"),
    "AWS": ("aws", "amazon\\s+web\\s+services"),
    "CI/CD": ("ci\\s*/?\\s*cd", "cicd"),
}


def _evidence_lines(text: str, skill: str) -> list[str]:
    terms = _EVIDENCE_ALIASES.get(skill, (re.escape(skill),))
    pattern = rf"(?<![\w.+#-])(?:{'|'.join(terms)})(?![\w-])"
    lines = [line.strip() for line in text.splitlines() if re.search(pattern, line, re.IGNORECASE)]
    return lines[:3]


def _partial_areas(resume_data: dict[str, Any], job_data: dict[str, Any]) -> list[str]:
    areas: list[str] = []
    if job_data.get("experience_requirements") and not resume_data.get("experience"):
        areas.append("Experience requirements are stated, but no experience section was detected in the resume.")
    if job_data.get("education_requirements") and not resume_data.get("education"):
        areas.append("Education requirements are stated, but no education section was detected in the resume.")
    return areas


def _ats_analysis(
    resume_data: dict[str, Any], job_data: dict[str, Any], resume_skill_keys: set[str], required: list[str], preferred: list[str], missing_required: list[str], missing_preferred: list[str], extracted_text: str
) -> dict[str, object]:
    terms = required + preferred
    keyword_coverage = round(100 * _coverage(len([term for term in terms if canonical_skill_key(term) in resume_skill_keys]), len(terms)), 2)
    checks = [
        {"name": "Readable source text", "passed": len(extracted_text.strip()) >= 80, "detail": "The uploaded document yielded readable text." if len(extracted_text.strip()) >= 80 else "Very little readable text was extracted."},
        {"name": "Skills section", "passed": bool(resume_data.get("skills")), "detail": "Skills were detected." if resume_data.get("skills") else "No supported skills were detected."},
        {"name": "Experience section", "passed": bool(resume_data.get("experience")), "detail": "Experience evidence was detected." if resume_data.get("experience") else "No experience section was detected."},
        {"name": "Education section", "passed": bool(resume_data.get("education")), "detail": "Education evidence was detected." if resume_data.get("education") else "No education section was detected."},
    ]
    improvements = [f"Add evidence for required skill: {skill}." for skill in missing_required] + [f"Consider adding preferred skill evidence: {skill}." for skill in missing_preferred]
    return {"keyword_coverage": keyword_coverage, "missing_important_keywords": missing_required + missing_preferred, "checks": checks, "improvement_areas": improvements, "score_breakdown": {"required_keywords": len(required), "preferred_keywords": len(preferred), "detected_resume_skills": len(resume_skill_keys)}}
