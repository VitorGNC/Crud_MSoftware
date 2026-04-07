from __future__ import annotations

from typing import Dict, List, Optional

from app.models.talhao import Talhao
from app.repository.strategies import StorageStrategy


class TalhaoRepository:
    def __init__(self, strategy: StorageStrategy) -> None:
        self._strategy = strategy
        self._talhoes: Dict[str, Talhao] = {}
        self._load()

    def _load(self) -> None:
        for record in self._strategy.load():
            t = Talhao.from_dict(record)
            self._talhoes[t.talhao_id] = t

    def _persist(self) -> None:
        self._strategy.persist([t.to_dict() for t in self._talhoes.values()])

    def create(self, talhao: Talhao) -> None:
        self._talhoes[talhao.talhao_id] = talhao
        self._persist()

    def get(self, talhao_id: str) -> Optional[Talhao]:
        return self._talhoes.get(talhao_id)

    def list_all(self) -> List[Talhao]:
        return list(self._talhoes.values())

    def update(self, talhao: Talhao) -> None:
        if talhao.talhao_id not in self._talhoes:
            raise KeyError(f"Talhao {talhao.talhao_id} nao encontrado.")
        self._talhoes[talhao.talhao_id] = talhao
        self._persist()

    def remove(self, talhao_id: str) -> None:
        if talhao_id not in self._talhoes:
            raise KeyError(f"Talhao {talhao_id} nao encontrado.")
        del self._talhoes[talhao_id]
        self._persist()
