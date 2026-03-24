from __future__ import annotations

from typing import Dict, List, Optional

from app.models.usuario import Usuario
from app.repository.strategies import StorageStrategy


class UserRepository:
    def __init__(self, strategy: StorageStrategy) -> None:
        self._strategy = strategy
        self._usuarios: Dict[str, Usuario] = {}
        self._load()

    def _load(self) -> None:
        data = self._strategy.load()
        self._usuarios = {item["login"]: Usuario.from_dict(item) for item in data}

    def _persist(self) -> None:
        payload = [usuario.to_dict() for usuario in self._usuarios.values()]
        self._strategy.persist(payload)

    def set_strategy(self, strategy: StorageStrategy) -> None:
        snapshot = [usuario.to_dict() for usuario in self._usuarios.values()]
        strategy.persist(snapshot)
        self._strategy = strategy
        self._load()

    def add(self, usuario: Usuario) -> Usuario:
        self._usuarios[usuario.login] = usuario
        self._persist()
        return usuario

    def get(self, login: str) -> Optional[Usuario]:
        return self._usuarios.get(login)

    def remove(self, login: str) -> None:
        if login in self._usuarios:
            self._usuarios.pop(login)
            self._persist()

    def all(self) -> List[Usuario]:
        return list(self._usuarios.values())

    def exists(self, login: str) -> bool:
        return login in self._usuarios
