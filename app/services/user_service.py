from __future__ import annotations

from typing import Dict

from app.auth import hash_password, verify_password
from app.models.usuario import Usuario, UsuarioErro
from app.repository.user_repository import UserRepository
from app.utils.logger_adapter import LoggerAdapter


class UserService:
    def __init__(self, repository: UserRepository, logger: LoggerAdapter) -> None:
        self._repository = repository
        self._logger = logger

    def registrar(self, login: str, senha: str, email: str, nome: str, idade: int) -> Usuario:
        if self._repository.exists(login):
            raise UsuarioErro("Login ja utilizado.")
        senha_hash = hash_password(senha)
        usuario = Usuario(
            login=login,
            nome=nome.strip(),
            email=email,
            senha_hash=senha_hash,
            idade=idade,
        )
        self._repository.add(usuario)
        self._logger.info(f"Usuario criado: {login}")
        return usuario

    def autenticar(self, login: str, senha: str) -> Usuario:
        usuario = self._repository.get(login)
        if not usuario or not verify_password(senha, usuario.senha_hash):
            self._logger.error(f"Falha de login para {login}")
            raise UsuarioErro("Credenciais invalidas.")
        self._logger.info(f"Login bem sucedido: {login}")
        return usuario

    def listar(self) -> Dict[str, Usuario]:
        return {usuario.login: usuario for usuario in self._repository.all()}

    def existe_usuario(self, login: str) -> bool:
        return self._repository.exists(login)
