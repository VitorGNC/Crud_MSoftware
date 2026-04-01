from __future__ import annotations

import hashlib
import secrets


def _validar_senha(senha: str) -> None:
    if len(senha) < 8:
        raise ValueError("Senha deve ter no minimo 8 caracteres.")
    if senha.lower() == senha or senha.upper() == senha:
        raise ValueError("Senha deve possuir letras maiusculas e minusculas.")
    if not any(ch.isdigit() for ch in senha):
        raise ValueError("Senha precisa de numeros.")
    especiais = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
    if not any(ch in especiais for ch in senha):
        raise ValueError("Senha precisa de caractere especial.")


def hash_password(senha: str) -> str:
    _validar_senha(senha)
    salt = secrets.token_hex(8)
    digest = hashlib.sha256(f"{salt}:{senha}".encode()).hexdigest()
    return f"{salt}${digest}"


def verify_password(senha: str, registro: str) -> bool:
    try:
        salt, stored = registro.split("$", maxsplit=1)
    except ValueError:
        return False
    digest = hashlib.sha256(f"{salt}:{senha}".encode()).hexdigest()
    return secrets.compare_digest(digest, stored)
