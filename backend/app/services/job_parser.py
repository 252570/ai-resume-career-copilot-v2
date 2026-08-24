from __future__ import annotations

import re

from app.schemas.job import JobRequirementData
from app.services.resume_parser import SKILL_PATTERNS

EXPERIENCE_PATTERN = re.compile(r"[^.\n]{0,80}\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\+?\s+years?[^.\n]{0,100}", re.IGNORECASE)
EDUCATION_PATTERN = re.compile(r"[^.\n]{0,80}\b(?:bachelor(?:'s)?|master(?:'s)?|ph\.?d|degree|bsc|msc|mba)[^.\n]{0,100}", re.IGNORECASE)
COMPANY_PATTERN = re.compile(r"^\s*(?:company|employer)\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
TITLE_PATTERN = re.compile(r"^\s*(?:job\s*)?title\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)


def parse_job_description(text: str, supplied_title: str | None = None, supplied_company: str | None = None) -> JobRequirementData:
    """Extract only literal, rule-based job requirement signals from source text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = supplied_title or _first_group(TITLE_PATTERN, text) or _likely_title(lines)
    company = supplied_company or _first_group(COMPANY_PATTERN, text)
    required_scope = _section_text(lines, ("requirements", "required qualifications", "what you will need", "must have"))
    preferred_scope = _section_text(lines, ("preferred qualifications", "nice to have", "preferred", "bonus"))
    all_skills = _skills_in(text)
    preferred_skills = _skills_in(preferred_scope)
    required_skills = _skills_in(required_scope)
    if not required_skills:
        required_skills = [skill for skill in all_skills if skill not in preferred_skills]
    return JobRequirementData(
        job_title=title,
        company_name=company,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        experience_requirements=_unique_matches(EXPERIENCE_PATTERN, text),
        education_requirements=_unique_matches(EDUCATION_PATTERN, text),
        important_keywords=all_skills,
    )


def _skills_in(text: str) -> list[str]:
    return [name for name, pattern in SKILL_PATTERNS.items() if re.search(pattern, text, re.IGNORECASE)]


def _first_group(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def _likely_title(lines: list[str]) -> str | None:
    for line in lines[:6]:
        if 3 <= len(line) <= 120 and not re.search(r"@|https?://|\b(?:company|location|about us)\b", line, re.IGNORECASE):
            return line
    return None


def _section_text(lines: list[str], headings: tuple[str, ...]) -> str:
    for index, line in enumerate(lines):
        normalized = re.sub(r"[:\-–—]+$", "", line.lower()).strip()
        if normalized in headings or any(normalized.startswith(f"{heading}:") for heading in headings):
            output: list[str] = []
            for candidate in lines[index + 1 :]:
                if len(output) and candidate.lower() in {"responsibilities", "benefits", "about us", "application"}:
                    break
                output.append(candidate)
                if len(output) >= 12:
                    break
            return "\n".join(output)
    return ""


def _unique_matches(pattern: re.Pattern[str], text: str) -> list[str]:
    matches: list[str] = []
    for match in pattern.finditer(text):
        value = re.sub(r"\s+", " ", match.group(0)).strip(" -:;")
        if value and value not in matches:
            matches.append(value)
    return matches[:8]
