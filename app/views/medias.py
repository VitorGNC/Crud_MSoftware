"""
<<Boundary>> Uploader (Medias)
Rotas de upload de mídias:
  - fazerUpload            →  POST /login/perfil/medias
  - getMedias              →  GET  /login/perfil/medias
  - deleteMedia            →  DELETE /login/perfil/medias/{id}
"""

from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import (
    get_usuario_atual,
)
from app.database import get_db
from app.service.uploader_controller import UploaderController
from app.models.usuario import (
    UsuarioORM,
)
from app.models.media import MediaResposta

router = APIRouter(tags=["Uploader (Medias)"])


# ==================================================================
# Rotas de Mídia  –  fazerUpload / getMedias / deleteMedia
# ==================================================================


# ------------------------------------------------------------------
# fazerUpload
# ------------------------------------------------------------------
@router.post(
    "/medias",
    response_model=MediaResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Fazer upload de mídia",
)
async def fazer_upload(
    file: UploadFile = File(...),
    usuario: UsuarioORM = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    return await UploaderController(db).upload_media(file, usuario.id)


# ------------------------------------------------------------------
# getMedias
# ------------------------------------------------------------------
@router.get(
    "/medias",
    response_model=List[MediaResposta],
    summary="Listar minhas mídias",
)
def get_medias(
    usuario: UsuarioORM = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    return UploaderController(db).get_medias(usuario.id)


# ------------------------------------------------------------------
# deleteMedia
# ------------------------------------------------------------------
@router.delete(
    "/medias/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover mídia própria",
)
def delete_media(
    media_id: int,
    usuario: UsuarioORM = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    UploaderController(db).delete_media(media_id, usuario.id, is_admin=False)
