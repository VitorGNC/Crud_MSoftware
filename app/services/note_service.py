from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from uuid import uuid4

from app.models.note import Note
from app.repository.note_repository import NoteRepository
from app.repository.strategies import StorageStrategy
from app.utils.logger_adapter import LoggerAdapter

UPLOAD_DIR = Path("uploads")


class NoteService:
    def __init__(self, repository: NoteRepository, loggers: Iterable[LoggerAdapter]) -> None:
        self._repository = repository
        self._loggers = list(loggers)
        self._strategies: Dict[str, StorageStrategy] = {}
        UPLOAD_DIR.mkdir(exist_ok=True)

    def register_strategy(self, name: str, strategy: StorageStrategy) -> None:
        self._strategies[name] = strategy

    def available_strategies(self) -> List[str]:
        return list(self._strategies.keys())

    def use_strategy(self, name: str) -> None:
        strategy = self._strategies.get(name)
        if not strategy:
            raise ValueError(f"Estrategia {name} nao cadastrada")
        self._repository.set_strategy(strategy)
        self._log(f"Estrategia de armazenamento ativa: {name}")

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
        note = self._require(note_id)
        source = Path(file_path)
        if not source.exists():
            raise FileNotFoundError(file_path)
        target_name = f"{note.note_id}_{source.name}"
        target = UPLOAD_DIR / target_name
        shutil.copy2(source, target)
        if target_name not in note.attachments:
            note.attachments.append(target_name)
        note.touch()
        self._repository.update(note)
        self._log(f"Arquivo anexado em nota {note.note_id}: {target_name}")
        return note

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
        for logger in self._loggers:
            logger.info(message)
