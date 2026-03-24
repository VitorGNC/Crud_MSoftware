"""Entidades de usuario para o Notes App."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


class UsuarioErro(ValueError):
    """Erro de validacao para usuarios."""


LOGIN_MAX = 12


def _validar_login(login: str) -> str:
    login = (login or "").strip()
    if not login:
        raise UsuarioErro("Login nao pode ser vazio.")
    if len(login) > LOGIN_MAX:
        raise UsuarioErro(f"Login deve ter no maximo {LOGIN_MAX} caracteres.")
    if any(ch.isdigit() for ch in login):
        raise UsuarioErro("Login nao pode conter numeros.")
    return login


def _validar_email(email: str) -> str:
    email = (email or "").strip().lower()
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise UsuarioErro("Email invalido.")
    dominio = email.split("@", maxsplit=1)[1]
    if "." not in dominio:
        raise UsuarioErro("Email invalido.")
    return email


def _validar_idade(idade: int) -> int:
    if idade < 0 or idade > 150:
        raise UsuarioErro("Idade invalida.")
    return idade


@dataclass
class Usuario:
    login: str
    nome: str
    email: str
    senha_hash: str
    idade: int
    is_admin: bool = False
    ativo: bool = True
    criado_em: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        self.login = _validar_login(self.login)
        self.email = _validar_email(self.email)
        self.idade = _validar_idade(self.idade)

    def atualizar_dados(self, nome: str | None = None, email: str | None = None, idade: int | None = None) -> None:
        if nome:
            self.nome = nome.strip()
        if email:
            self.email = _validar_email(email)
        if idade is not None:
            self.idade = _validar_idade(idade)

    def desativar(self) -> None:
        self.ativo = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "login": self.login,
            "nome": self.nome,
            "email": self.email,
            "senha_hash": self.senha_hash,
            "idade": self.idade,
            "is_admin": self.is_admin,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> Usuario:
        data = dict(payload)
        data["criado_em"] = datetime.fromisoformat(payload["criado_em"]) if "criado_em" in payload else datetime.utcnow()
        return cls(**data)
    ativo: bool

    model_config = {"from_attributes": True}


class AlterarPermissaoSchema(BaseModel):
    is_admin: bool
