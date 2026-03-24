from __future__ import annotations

from typing import Optional

from app.patterns.memento import NoteMemento
from app.services.note_service import NoteService


class NoteReceiver:
    def __init__(self, service: NoteService) -> None:
        self._service = service

    def create(self, owner: str, title: str, content: str):
        return self._service.create_note(owner, title, content)

    def update(self, note_id: str, title: str, content: str):
        return self._service.update_note(note_id, title, content)

    def attach(self, note_id: str, file_path: str):
        return self._service.attach_file(note_id, file_path)

    def attach_from_bytes(self, note_id: str, filename: str, payload: bytes):
        return self._service.attach_bytes(note_id, filename, payload)

    def delete(self, note_id: str) -> None:
        self._service.delete_note(note_id)

    def snapshot(self, note_id: str) -> Optional[NoteMemento]:
        note = self._service.snapshot(note_id)
        return NoteMemento.from_note(note) if note else None

    def restore(self, memento: NoteMemento):
        note = memento.to_note()
        return self._service.override(note)

