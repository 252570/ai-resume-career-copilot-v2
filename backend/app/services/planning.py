from __future__ import annotations

from app.models import ProjectRecommendation, RoadmapItem

SKILL_GUIDANCE: dict[str, dict[str, object]] = {
    "Python": {"prerequisites": ["Programming fundamentals"], "stage": "Foundation", "practice": "Build a command-line data transformation tool."},
    "SQL": {"prerequisites": ["Relational data basics"], "stage": "Foundation", "practice": "Design and query a small relational database."},
    "PostgreSQL": {"prerequisites": ["SQL"], "stage": "Applied", "practice": "Add migrations, indexes, and query tests to a PostgreSQL service."},
    "FastAPI": {"prerequisites": ["Python", "HTTP basics"], "stage": "Applied", "practice": "Build a validated CRUD API with tests."},
    "Docker": {"prerequisites": ["Command line basics"], "stage": "Applied", "practice": "Containerize a service with environment-based configuration."},
    "AWS": {"prerequisites": ["Networking basics"], "stage": "Applied", "practice": "Deploy a small static app and document the architecture."},
    "JavaScript": {"prerequisites": ["Programming fundamentals"], "stage": "Foundation", "practice": "Build an interactive page that manipulates the DOM without a framework."},
    "TypeScript": {"prerequisites": ["JavaScript"], "stage": "Applied", "practice": "Convert a small JavaScript project to typed TypeScript with strict mode on."},
    "React": {"prerequisites": ["JavaScript", "HTML", "CSS"], "stage": "Applied", "practice": "Build a component-driven app using state, props, and hooks."},
    "Next.js": {"prerequisites": ["React"], "stage": "Applied", "practice": "Build a Next.js app with routing, server components, and one API route."},
    "Node.js": {"prerequisites": ["JavaScript"], "stage": "Applied", "practice": "Build a small REST server with Express, validation, and error handling."},
    "Java": {"prerequisites": ["Programming fundamentals"], "stage": "Foundation", "practice": "Build an object-oriented console application with unit tests."},
    "C++": {"prerequisites": ["Programming fundamentals"], "stage": "Foundation", "practice": "Implement a data structure and measure its runtime performance."},
    "C#": {"prerequisites": ["Programming fundamentals"], "stage": "Foundation", "practice": "Build a small .NET console or Web API application."},
    "Git": {"prerequisites": ["Command line basics"], "stage": "Foundation", "practice": "Practice branching, merging, and pull requests on a sample repository."},
    "Linux": {"prerequisites": ["Command line basics"], "stage": "Foundation", "practice": "Automate a routine task with a shell script on a Linux machine."},
    "Pandas": {"prerequisites": ["Python"], "stage": "Foundation", "practice": "Clean and analyze a messy CSV dataset and summarize the findings."},
    "NumPy": {"prerequisites": ["Python"], "stage": "Foundation", "practice": "Implement vectorized numerical operations without Python loops."},
    "Machine Learning": {"prerequisites": ["Python", "Statistics basics"], "stage": "Applied", "practice": "Train and evaluate a supervised model on a public dataset with a clear metric."},
    "Deep Learning": {"prerequisites": ["Machine Learning", "Python"], "stage": "Advanced", "practice": "Train a small neural network and document its architecture and results."},
    "TensorFlow": {"prerequisites": ["Machine Learning", "Python"], "stage": "Applied", "practice": "Build and train a model end to end with TensorFlow/Keras."},
    "PyTorch": {"prerequisites": ["Machine Learning", "Python"], "stage": "Applied", "practice": "Implement a training loop in PyTorch for a small dataset."},
    "scikit-learn": {"prerequisites": ["Python", "Pandas"], "stage": "Applied", "practice": "Build a full train/test pipeline with scikit-learn and report metrics."},
    "Django": {"prerequisites": ["Python", "HTTP basics"], "stage": "Applied", "practice": "Build a database-backed web app using Django's ORM and admin."},
    "Flask": {"prerequisites": ["Python", "HTTP basics"], "stage": "Applied", "practice": "Build a small REST API with Flask and automated tests."},
    "REST APIs": {"prerequisites": ["HTTP basics"], "stage": "Applied", "practice": "Design and document a RESTful API with correct status codes."},
    "GraphQL": {"prerequisites": ["HTTP basics", "REST APIs"], "stage": "Applied", "practice": "Expose a small schema with queries and mutations."},
    "MySQL": {"prerequisites": ["SQL"], "stage": "Applied", "practice": "Design a normalized schema and write indexed queries."},
    "MongoDB": {"prerequisites": ["Database basics"], "stage": "Applied", "practice": "Model and query a document database for a small application."},
    "Redis": {"prerequisites": ["Database basics"], "stage": "Applied", "practice": "Add caching to an API and measure the latency improvement."},
    "Kubernetes": {"prerequisites": ["Docker"], "stage": "Advanced", "practice": "Deploy a multi-container app to a local Kubernetes cluster."},
    "Azure": {"prerequisites": ["Networking basics"], "stage": "Applied", "practice": "Deploy a small service to Azure and document the setup."},
    "GCP": {"prerequisites": ["Networking basics"], "stage": "Applied", "practice": "Deploy a small service to Google Cloud and document the setup."},
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
