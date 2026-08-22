"""Local-development resume storage with generated filenames and no user-controlled paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class StoredResumeFile:
    storage_key: str


class ResumeStorage:
    """Write original uploads with exclusive creation so existing files are never overwritten."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir

    def save(self, content: bytes, suffix: str) -> StoredResumeFile:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        storage_key = f"{uuid4().hex}{suffix.lower()}"
        destination = self.storage_dir / storage_key
        with destination.open("xb") as output:
            output.write(content)
        return StoredResumeFile(storage_key=storage_key)

    def delete(self, storage_key: str) -> None:
        candidate = self.storage_dir / Path(storage_key).name
        if candidate.exists():
            candidate.unlink()
