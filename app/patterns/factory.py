from __future__ import annotations

from app.patterns.command import (
    AttachContentCommand,
    AttachFileCommand,
    CreateNoteCommand,
    DeleteNoteCommand,
    UpdateNoteCommand,
)
from app.patterns.receiver import NoteReceiver


class CommandFactory:
    """Centraliza a criação de todos os comandos do sistema de notas."""

    def __init__(self, receiver: NoteReceiver) -> None:
        self._receiver = receiver

    def create_note(self, owner: str, title: str, content: str) -> CreateNoteCommand:
        return CreateNoteCommand(self._receiver, owner, title, content)

    def update_note(self, note_id: str, title: str, content: str) -> UpdateNoteCommand:
        return UpdateNoteCommand(self._receiver, note_id, title, content)

    def delete_note(self, note_id: str) -> DeleteNoteCommand:
        return DeleteNoteCommand(self._receiver, note_id)

    def attach_file(self, note_id: str, file_path: str) -> AttachFileCommand:
        return AttachFileCommand(self._receiver, note_id, file_path)

    def attach_content(self, note_id: str, filename: str, payload: bytes) -> AttachContentCommand:
        return AttachContentCommand(self._receiver, note_id, filename, payload)
