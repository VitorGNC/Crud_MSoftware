from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.models.note import Note


@dataclass
class NoteMemento:
    note_id: str
    state: Dict[str, Any]
    timestamp: datetime

    @classmethod
    def from_note(cls, note: Note) -> NoteMemento:
        return cls(note_id=note.note_id, state=note.to_dict(), timestamp=datetime.utcnow())

    def to_note(self) -> Note:
        return Note.from_dict(self.state)


class NoteCaretaker:
    def __init__(self) -> None:
        self._history: List[Tuple[str, NoteMemento]] = []
        self._by_note: Dict[str, List[NoteMemento]] = {}

    def push(self, memento: NoteMemento) -> None:
        self._history.append((memento.note_id, memento))
        self._by_note.setdefault(memento.note_id, []).append(memento)

    def pop(self) -> Optional[Tuple[str, NoteMemento]]:
        if not self._history:
            return None
        note_id, memento = self._history.pop()
        stack = self._by_note.get(note_id)
        if stack:
            stack.pop()
            if not stack:
                self._by_note.pop(note_id, None)
        return note_id, memento

    def history_for(self, note_id: str) -> List[NoteMemento]:
        return list(self._by_note.get(note_id, []))
