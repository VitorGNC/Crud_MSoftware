from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum, auto
from typing import Any

from app.utils.logger_adapter import LoggerAdapter


class EventoNota(Enum):
    CRIADA = auto()
    ATUALIZADA = auto()
    REMOVIDA = auto()


class NoteObserver(ABC):
    @abstractmethod
    def notificar(self, evento: EventoNota, dados: dict[str, Any]) -> None: ...


class LogNoteObserver(NoteObserver):
    """Registra cada evento de nota usando o LoggerAdapter do sistema."""

    def __init__(self, logger: LoggerAdapter) -> None:
        self._logger = logger

    def notificar(self, evento: EventoNota, dados: dict[str, Any]) -> None:
        self._logger.info(f"[EVENTO] {evento.name} | {dados}")


class StatisticsObserver(NoteObserver):
    """Contabiliza eventos por tipo para expor métricas de uso."""

    def __init__(self) -> None:
        self._contadores: dict[str, int] = defaultdict(int)

    def notificar(self, evento: EventoNota, dados: dict[str, Any]) -> None:
        self._contadores[evento.name] += 1

    def get_stats(self) -> dict[str, int]:
        return dict(self._contadores)


class NoteEventBus:
    _observadores: list[NoteObserver] = []

    @classmethod
    def registrar(cls, observador: NoteObserver) -> None:
        cls._observadores.append(observador)

    @classmethod
    def desregistrar(cls, observador: NoteObserver) -> None:
        cls._observadores = [o for o in cls._observadores if o is not observador]

    @classmethod
    def emitir(cls, evento: EventoNota, dados: dict[str, Any] | None = None) -> None:
        for obs in cls._observadores:
            obs.notificar(evento, dados or {})

    @classmethod
    def get_stats(cls) -> dict[str, int]:
        """Retorna contadores do StatisticsObserver registrado, se houver."""
        for obs in cls._observadores:
            if isinstance(obs, StatisticsObserver):
                return obs.get_stats()
        return {}
