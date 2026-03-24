"""Ponto de entrada do Notes App baseado em design patterns."""

from __future__ import annotations

from pathlib import Path

from app.interface.gui import NotesAppGUI
from app.patterns.command import CommandInvoker
from app.patterns.memento import NoteCaretaker
from app.patterns.receiver import NoteReceiver
from app.patterns.sender import CommandSender
from app.repository.note_repository import NoteRepository
from app.repository.strategies import InMemoryStorageStrategy, JsonStorageStrategy
from app.services.note_service import NoteService
from app.services.user_service import UserService
from app.utils.logger_adapter import ConsoleLogTarget, FileLogTarget, LoggerAdapter


def bootstrap_app() -> NotesAppGUI:
    caretaker = NoteCaretaker()
    notes_json = JsonStorageStrategy(Path("data/notes.json"))
    repository = NoteRepository(notes_json)

    console_logger = LoggerAdapter(ConsoleLogTarget())
    file_logger = LoggerAdapter(FileLogTarget(Path("logs/app.log")))
    note_service = NoteService(repository, [console_logger, file_logger])
    note_service.register_strategy("json", notes_json)
    note_service.register_strategy("mem", InMemoryStorageStrategy())

    receiver = NoteReceiver(note_service)
    invoker = CommandInvoker(caretaker)
    sender = CommandSender(invoker)

    user_service = UserService(Path("data/usuarios.json"))
    return NotesAppGUI(sender, receiver, note_service, user_service)


def main() -> None:
    app = bootstrap_app()
    app.run()


if __name__ == "__main__":
    main()
