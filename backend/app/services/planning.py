from __future__ import annotations

from app.models import ProjectRecommendation, RoadmapItem

SKILL_GUIDANCE: dict[str, dict[str, object]] = {
    "Python": {"prerequisites": ["Programming fundamentals"], "stage": "Foundation", "practice": "Build a command-line data transformation tool."},
    "SQL": {"prerequisites": ["Relational data basics"], "stage": "Foundation", "practice": "Design and query a small relational database."},
    "PostgreSQL": {"prerequisites": ["SQL"], "stage": "Applied", "practice": "Add migrations, indexes, and query tests to a PostgreSQL service."},
    "FastAPI": {"prerequisites": ["Python", "HTTP basics"], "stage": "Applied", "practice": "Build a validated CRUD API with tests."},
    "Docker": {"prerequisites": ["Command line basics"], "stage": "Applied", "practice": "Containerize a service with environment-based configuration."},
    "AWS": {"prerequisites": ["Networking basics"], "stage": "Applied", "practice": "Deploy a small static app and document the architecture."},
}


def build_plan(gaps: list[dict[str, object]]) -> tuple[list[RoadmapItem], list[ProjectRecommendation]]:
    roadmap: list[RoadmapItem] = []
    projects: list[ProjectRecommendation] = []
    for sequence, gap in enumerate(gaps, start=1):
        skill = str(gap["skill"])
        guide = SKILL_GUIDANCE.get(skill, {"prerequisites": ["Relevant fundamentals"], "stage": "Applied", "practice": f"Build a focused exercise that demonstrates {skill}."})
        roadmap.append(RoadmapItem(skill=skill, priority=str(gap["priority"]), prerequisites=list(guide["prerequisites"]), sequence=sequence, practice_suggestion=str(guide["practice"]), learning_stage=str(guide["stage"])))
        projects.append(ProjectRecommendation(
            title=f"{skill} Evidence Project", purpose=f"Create verifiable portfolio evidence for the {skill} requirement.", skills_developed=[skill],
            suggested_technology=[skill, "Git", "README"], difficulty="Intermediate" if str(gap["priority"]) == "critical" else "Foundational",
            portfolio_value=f"Shows a recruiter observable work aligned with the job requirement for {skill}.",
        ))
    return roadmap, projects
