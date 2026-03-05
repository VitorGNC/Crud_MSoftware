from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.database import Base


# =============================================================================
# ORM  –  <<Entity>> Media
# =============================================================================
class MediaORM(Base):
    """
    <<Entity>> Media
    Atributos: url, fileName, size, mimetype, userId
    """
    __tablename__ = "medias"

    id: int           = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url: str          = Column(String(500), nullable=False)
    file_name: str    = Column(String(255), nullable=False)
    size: int         = Column(Integer, nullable=False)
    mimetype: str     = Column(String(100), nullable=False)
    user_id: int      = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("UsuarioORM", back_populates="medias")


# =============================================================================
# Pydantic Schemas  –  Media
# =============================================================================
class MediaResposta(BaseModel):
    id: int
    url: str
    file_name: str
    size: int
    mimetype: str
    user_id: int

    model_config = {"from_attributes": True}
