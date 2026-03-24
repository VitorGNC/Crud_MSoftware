from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Protocol


class StorageStrategy(Protocol):
    def load(self) -> List[Dict[str, Any]]:
        ...

    def persist(self, data: List[Dict[str, Any]]) -> None:
        ...


class JsonStorageStrategy:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("[]", encoding="utf-8")

    def load(self) -> List[Dict[str, Any]]:
        raw = self._path.read_text(encoding="utf-8") or "[]"
        return json.loads(raw)

    def persist(self, data: List[Dict[str, Any]]) -> None:
        self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class InMemoryStorageStrategy:
    def __init__(self) -> None:
        self._store: List[Dict[str, Any]] = []

    def load(self) -> List[Dict[str, Any]]:
        return deepcopy(self._store)

    def persist(self, data: List[Dict[str, Any]]) -> None:
        self._store = deepcopy(data)
