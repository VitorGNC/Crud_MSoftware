from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any


class EventoNota(Enum):
    CRIADA = auto()
    ATUALIZADA = auto()
    REMOVIDA = auto()


class NoteObserver(ABC):
    @abstractmethod
    def notificar(self, evento: EventoNota, dados: dict[str, Any]) -> None: ...


class LogNoteObserver(NoteObserver):
    def notificar(self, evento: EventoNota, dados: dict[str, Any]) -> None:
        print(f"[EVENTO] {evento.name} | {dados}")


class NoteEventBus:
    _observadores: list[NoteObserver] = []

    @classmethod
    def registrar(cls, observador: NoteObserver) -> None:
        cls._observadores.append(observador)

    @classmethod
    def emitir(cls, evento: EventoNota, dados: dict[str, Any] | None = None) -> None:
        for obs in cls._observadores:
            obs.notificar(evento, dados or {})
