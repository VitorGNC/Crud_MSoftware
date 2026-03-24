from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.patterns.memento import NoteCaretaker, NoteMemento
from app.patterns.receiver import NoteReceiver


class BaseNoteCommand(ABC):
    def __init__(self, receiver: NoteReceiver) -> None:
        self.receiver = receiver

    def snapshot(self) -> Optional[NoteMemento]:
        return None

    @abstractmethod
    def execute(self):
        ...

    def undo(self, memento: Optional[NoteMemento]):
        return None


class CreateNoteCommand(BaseNoteCommand):
    def __init__(self, receiver: NoteReceiver, owner: str, title: str, content: str) -> None:
        super().__init__(receiver)
        self.owner = owner
        self.title = title
        self.content = content
        self._created_id: Optional[str] = None

    def execute(self):
        note = self.receiver.create(self.owner, self.title, self.content)
        self._created_id = note.note_id
        return note

    def undo(self, memento: Optional[NoteMemento]):
        if self._created_id:
            self.receiver.delete(self._created_id)


class UpdateNoteCommand(BaseNoteCommand):
    def __init__(self, receiver: NoteReceiver, note_id: str, title: str, content: str) -> None:
        super().__init__(receiver)
        self.note_id = note_id
        self.title = title
        self.content = content

    def snapshot(self) -> Optional[NoteMemento]:
        return self.receiver.snapshot(self.note_id)

    def execute(self):
        return self.receiver.update(self.note_id, self.title, self.content)

    def undo(self, memento: Optional[NoteMemento]):
        if memento:
            return self.receiver.restore(memento)


class AttachFileCommand(BaseNoteCommand):
    def __init__(self, receiver: NoteReceiver, note_id: str, file_path: str) -> None:
        super().__init__(receiver)
        self.note_id = note_id
        self.file_path = file_path

    def snapshot(self) -> Optional[NoteMemento]:
        return self.receiver.snapshot(self.note_id)

    def execute(self):
        return self.receiver.attach(self.note_id, self.file_path)

    def undo(self, memento: Optional[NoteMemento]):
        if memento:
            return self.receiver.restore(memento)


class DeleteNoteCommand(BaseNoteCommand):
    def __init__(self, receiver: NoteReceiver, note_id: str) -> None:
        super().__init__(receiver)
        self.note_id = note_id

    def snapshot(self) -> Optional[NoteMemento]:
        return self.receiver.snapshot(self.note_id)

    def execute(self):
        self.receiver.delete(self.note_id)

    def undo(self, memento: Optional[NoteMemento]):
        if memento:
            return self.receiver.restore(memento)


class CommandInvoker:
    def __init__(self, caretaker: NoteCaretaker) -> None:
        self._caretaker = caretaker
        self._history: List[Tuple[BaseNoteCommand, Optional[NoteMemento]]] = []

    def execute(self, command: BaseNoteCommand):
        memento = command.snapshot()
        if memento:
            self._caretaker.push(memento)
        result = command.execute()
        self._history.append((command, memento))
        return result

    def undo_last(self) -> bool:
        if not self._history:
            return False
        command, stored_memento = self._history.pop()
        memento = stored_memento
        if stored_memento:
            popped = self._caretaker.pop()
            if popped:
                _, candidate = popped
                memento = candidate
        command.undo(memento)
        return True

    def history_for(self, note_id: str):
        return self._caretaker.history_for(note_id)
