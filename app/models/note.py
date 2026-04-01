from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Note:
    note_id: str
    owner: str
    title: str
    content: str
    attachments: List[str] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "note_id": self.note_id,
            "owner": self.owner,
            "title": self.title,
            "content": self.content,
            "attachments": list(self.attachments),
            "updated_at": self.updated_at.isoformat(),
        }
        return data

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> Note:
        data = dict(payload)
        attachments = data.get("attachments", [])
        data["attachments"] = list(attachments)
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            data["updated_at"] = datetime.fromisoformat(updated_at)
        elif isinstance(updated_at, datetime):
            data["updated_at"] = updated_at
        else:
            data["updated_at"] = datetime.utcnow()
        return cls(**data)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()

    def clone(self) -> Note:
        return Note.from_dict(self.to_dict())
