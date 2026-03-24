from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol


class LegacyLogTarget(Protocol):
    def write(self, level: int, message: str) -> None:
        ...


class ConsoleLogTarget:
    def __init__(self) -> None:
        self._logger = logging.getLogger("notes-console")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    def write(self, level: int, message: str) -> None:
        self._logger.log(level, message)


class FileLogTarget:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._logger = logging.getLogger("notes-file")
        if not self._logger.handlers:
            handler = logging.FileHandler(path, encoding="utf-8")
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    def write(self, level: int, message: str) -> None:
        self._logger.log(level, message)


class LoggerAdapter:
    def __init__(self, target: LegacyLogTarget) -> None:
        self._target = target

    def info(self, message: str) -> None:
        self._target.write(logging.INFO, message)

    def error(self, message: str) -> None:
        self._target.write(logging.ERROR, message)
