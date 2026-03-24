from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from app.models.note import Note
from app.repository.note_repository import NoteRepository
from app.utils.logger_adapter import LoggerAdapter

UPLOAD_DIR = Path("uploads")


class NoteService:
    def __init__(self, repository: NoteRepository, logger: LoggerAdapter) -> None:
        self._repository = repository
        self._logger = logger
        UPLOAD_DIR.mkdir(exist_ok=True)

    def create_note(self, owner: str, title: str, content: str) -> Note:
        note = Note(
            note_id=str(uuid4()),
            owner=owner,
            title=(title or "Nova nota").strip(),
            content=content.strip(),
        )
        self._repository.create(note)
        self._log(f"Usuario {owner} criou a nota {note.note_id}")
        return note

    def update_note(self, note_id: str, title: str, content: str) -> Note:
        note = self._require(note_id)
        note.title = title.strip() or note.title
        note.content = content.strip()
        note.touch()
        self._repository.update(note)
        self._log(f"Usuario {note.owner} atualizou a nota {note.note_id}")
        return note

    def attach_file(self, note_id: str, file_path: str) -> Note:
        source = Path(file_path)
        if not source.exists():
            raise FileNotFoundError(file_path)
        data = source.read_bytes()
        return self.attach_bytes(note_id, source.name, data)

    def attach_bytes(self, note_id: str, filename: str, payload: bytes) -> Note:
        if not payload:
            raise ValueError("Conteudo do arquivo vazio")
        safe_name = filename or "attachment"
        return self._store_attachment(note_id, safe_name, payload)

    def delete_note(self, note_id: str) -> None:
        note = self._require(note_id)
        self._repository.remove(note.note_id)
        self._log(f"Nota {note.note_id} removida por {note.owner}")

    def list_notes(self, owner: str) -> List[Note]:
        notes = self._repository.list_by_owner(owner)
        notes.sort(key=lambda n: n.updated_at, reverse=True)
        return notes

    def get_note(self, note_id: str) -> Optional[Note]:
        return self._repository.get(note_id)

    def override(self, note: Note) -> Note:
        self._repository.override(note)
        self._log(f"Nota {note.note_id} restaurada via memento")
        return note

    def snapshot(self, note_id: str) -> Optional[Note]:
        note = self._repository.get(note_id)
        return note.clone() if note else None

    def _require(self, note_id: str) -> Note:
        note = self._repository.get(note_id)
        if not note:
            raise ValueError(f"Nota {note_id} nao encontrada")
        return note

    def _log(self, message: str) -> None:
        self._logger.info(message)

    def _store_attachment(self, note_id: str, filename: str, payload: bytes) -> Note:
        note = self._require(note_id)
        base_name = Path(filename).name or "attachment"
        target_name = f"{note.note_id}_{base_name}"
        target = UPLOAD_DIR / target_name
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        if target_name not in note.attachments:
            note.attachments.append(target_name)
        note.touch()
        self._repository.update(note)
        self._log(f"Arquivo anexado em nota {note.note_id}: {target_name}")
        return note
