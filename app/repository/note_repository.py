from __future__ import annotations

from typing import Dict, List, Optional

from app.models.note import Note
from app.repository.strategies import StorageStrategy


class NoteRepository:
    def __init__(self, strategy: StorageStrategy) -> None:
        self._strategy = strategy
        self._notes: Dict[str, Note] = {}
        self._load()

    def _load(self) -> None:
        data = self._strategy.load()
        self._notes = {item["note_id"]: Note.from_dict(item) for item in data}

    def _persist(self) -> None:
        payload = [note.to_dict() for note in self._notes.values()]
        self._strategy.persist(payload)

    def set_strategy(self, strategy: StorageStrategy) -> None:
        snapshot = [note.to_dict() for note in self._notes.values()]
        strategy.persist(snapshot)
        self._strategy = strategy
        self._load()

    def create(self, note: Note) -> Note:
        self._notes[note.note_id] = note
        self._persist()
        return note

    def update(self, note: Note) -> Note:
        if note.note_id not in self._notes:
            raise KeyError(f"Nota {note.note_id} nao encontrada")
        self._notes[note.note_id] = note
        self._persist()
        return note

    def override(self, note: Note) -> Note:
        self._notes[note.note_id] = note
        self._persist()
        return note

    def remove(self, note_id: str) -> None:
        if note_id not in self._notes:
            raise KeyError(f"Nota {note_id} nao encontrada")
        del self._notes[note_id]
        self._persist()

    def list_by_owner(self, owner: str) -> List[Note]:
        return [note for note in self._notes.values() if note.owner == owner]

    def get(self, note_id: str) -> Optional[Note]:
        return self._notes.get(note_id)

    def all_notes(self) -> List[Note]:
        return list(self._notes.values())
