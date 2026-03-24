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
from app.repository.user_repository import UserRepository
from app.services.note_service import NoteService
from app.services.user_service import UserService
from app.utils.logger_adapter import ConsoleLogTarget, FileLogTarget, LoggerAdapter

ACTIVE_STORAGE = "json"  # altere para "mem" durante testes
ACTIVE_LOGGER = "console"  # altere para "file" para persistir logs


def bootstrap_app() -> NotesAppGUI:
    caretaker = NoteCaretaker()

    note_storage_options = {
        "json": JsonStorageStrategy(Path("data/notes.json")),
        "mem": InMemoryStorageStrategy(),
    }
    user_storage_options = {
        "json": JsonStorageStrategy(Path("data/usuarios.json")),
        "mem": InMemoryStorageStrategy(),
    }
    logger_options = {
        "console": LoggerAdapter(ConsoleLogTarget()),
        "file": LoggerAdapter(FileLogTarget(Path("logs/app.log"))),
    }
    interface_options = {
        "gui": NotesAppGUI,
        "api": None,  # Futuramente, podemos adicionar uma interface RESTful
        # "cli": NotesAppCLI,  # Futuramente, podemos adicionar uma interface de linha de comando
    }

    note_strategy = note_storage_options.get(
        ACTIVE_STORAGE, note_storage_options["json"]
    )
    user_strategy = user_storage_options.get(
        ACTIVE_STORAGE, user_storage_options["json"]
    )
    note_repository = NoteRepository(note_strategy)
    user_repository = UserRepository(user_strategy)

    logger_adapter = logger_options.get(ACTIVE_LOGGER, logger_options["console"])
    note_service = NoteService(note_repository, logger_adapter)
    user_service = UserService(user_repository, logger_adapter)

    receiver = NoteReceiver(note_service)
    invoker = CommandInvoker(caretaker)
    sender = CommandSender(invoker)

    return NotesAppGUI(sender, receiver, note_service, user_service)


def main() -> None:
    app = bootstrap_app()
    app.run()


if __name__ == "__main__":
    main()
