from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from app.auth import hash_password, verify_password
from app.models.usuario import Usuario, UsuarioErro


class UserService:
    def __init__(self, storage_path: Path) -> None:
        self._path = storage_path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("[]", encoding="utf-8")
        self._usuarios: Dict[str, Usuario] = {}
        self._load()

    def _load(self) -> None:
        raw = self._path.read_text(encoding="utf-8")
        if not raw.strip():
            raw = "[]"
        data = json.loads(raw)
        self._usuarios = {item["login"]: Usuario.from_dict(item) for item in data}

    def _persist(self) -> None:
        payload = [usuario.to_dict() for usuario in self._usuarios.values()]
        self._path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def registrar(self, login: str, senha: str, email: str, nome: str, idade: int) -> Usuario:
        if login in self._usuarios:
            raise UsuarioErro("Login ja utilizado.")
        senha_hash = hash_password(senha)
        usuario = Usuario(login=login, nome=nome.strip(), email=email, senha_hash=senha_hash, idade=idade)
        self._usuarios[usuario.login] = usuario
        self._persist()
        return usuario

    def autenticar(self, login: str, senha: str) -> Usuario:
        usuario = self._usuarios.get(login)
        if not usuario or not verify_password(senha, usuario.senha_hash):
            raise UsuarioErro("Credenciais invalidas.")
        return usuario

    def listar(self) -> Dict[str, Usuario]:
        return dict(self._usuarios)

    def existe_usuario(self, login: str) -> bool:
        return login in self._usuarios
