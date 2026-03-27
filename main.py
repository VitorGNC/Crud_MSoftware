"""Ponto de entrada do Notes App baseado em design patterns."""

from __future__ import annotations

from pathlib import Path

from app.interface.interface_strategy import (
    GuiInterfaceStrategy,
    RestApiInterfaceStrategy,
)
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
from app.patterns.observer import LogNoteObserver, NoteEventBus

ACTIVE_STORAGE = "json"  # altere para "mem" durante testes
ACTIVE_LOGGER = "console"  # altere para "file" para persistir logs
ACTIVE_INTERFACE = "api"  # "gui" ou "api"


def bootstrap() -> None:
    NoteEventBus.registrar(LogNoteObserver())

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

    interface_options = {
        "gui": GuiInterfaceStrategy(),
        "api": RestApiInterfaceStrategy(host="127.0.0.1", port=8000),
    }
    strategy = interface_options.get(ACTIVE_INTERFACE, GuiInterfaceStrategy())
    strategy.run(sender, receiver, note_service, user_service)


def main() -> None:
    bootstrap()


if __name__ == "__main__":
    main()
