from __future__ import annotations

import re


_ALIASES = {
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "react.js": "React",
    "reactjs": "React",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "k8s": "Kubernetes",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "google cloud": "GCP",
    "amazon web services": "AWS",
    "ci cd": "CI/CD",
    "cicd": "CI/CD",
}


def canonical_skill_name(value: str) -> str:
    """Return a stable display name for safe, unambiguous skill aliases."""
    normalized = re.sub(r"\s+", " ", value.strip().lower().replace("_", " ")).replace("-", " ")
    return _ALIASES.get(normalized, value.strip())


def canonical_skill_key(value: str) -> str:
    return canonical_skill_name(value).casefold()


def canonical_skill_list(values: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        canonical = canonical_skill_name(value)
        if not canonical:
            continue
        key = canonical.casefold()
        if key not in seen:
            seen.add(key)
            output.append(canonical)
    return output
