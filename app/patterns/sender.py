from __future__ import annotations

from app.patterns.command import BaseNoteCommand, CommandInvoker


class CommandSender:
    def __init__(self, invoker: CommandInvoker) -> None:
        self._invoker = invoker

    def dispatch(self, command: BaseNoteCommand):
        return self._invoker.execute(command)

    def undo_last(self) -> bool:
        return self._invoker.undo_last()

    def history_for(self, note_id: str):
        return self._invoker.history_for(note_id)
