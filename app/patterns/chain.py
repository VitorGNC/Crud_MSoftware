"""Chain of Responsibility para validação de anexos.

Alinhado ao RF06 (upload de imagens) e RNF004 (segurança):
cada elo valida um aspecto do arquivo e passa ao próximo ou rejeita.

Cadeia padrão: ContentValidator → SizeValidator → FormatValidator
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

ALLOWED_EXTENSIONS = {
    ".txt", ".pdf", ".png", ".jpg", ".jpeg",
    ".tif", ".tiff", ".zip", ".shp", ".geojson",
}


class AttachmentValidator(ABC):
    """Elo base da cadeia."""

    def __init__(self) -> None:
        self._next: AttachmentValidator | None = None

    def set_next(self, handler: AttachmentValidator) -> AttachmentValidator:
        self._next = handler
        return handler

    def handle(self, filename: str, payload: bytes) -> None:
        self.validate(filename, payload)
        if self._next:
            self._next.handle(filename, payload)

    @abstractmethod
    def validate(self, filename: str, payload: bytes) -> None: ...


class ContentValidator(AttachmentValidator):
    """Rejeita payloads vazios."""

    def validate(self, filename: str, payload: bytes) -> None:
        if not payload:
            raise ValueError("Conteudo do arquivo vazio.")


class SizeValidator(AttachmentValidator):
    """Rejeita arquivos acima do limite configurado."""

    def __init__(self, max_bytes: int) -> None:
        super().__init__()
        self._max_bytes = max_bytes

    def validate(self, filename: str, payload: bytes) -> None:
        if len(payload) > self._max_bytes:
            limit_mb = self._max_bytes // (1024 * 1024)
            raise ValueError(f"Arquivo excede o limite de {limit_mb} MB.")


class FormatValidator(AttachmentValidator):
    """Rejeita extensões não permitidas."""

    def validate(self, filename: str, payload: bytes) -> None:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Formato '{ext}' nao permitido. "
                f"Extensoes aceitas: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )


def build_attachment_chain(max_bytes: int) -> AttachmentValidator:
    """Monta e retorna a cadeia padrão de validação."""
    head = ContentValidator()
    head.set_next(SizeValidator(max_bytes)).set_next(FormatValidator())
    return head
