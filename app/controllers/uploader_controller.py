import os
import uuid
from typing import List

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.media import MediaORM

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_MIMETYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "video/mp4", "video/quicktime", "video/x-msvideo",
    "audio/mpeg", "audio/ogg", "audio/wav",
    "application/pdf",
}


# =============================================================================
# <<Control>> UploaderController
# =============================================================================
class UploaderController:
    """
    Controla upload, listagem e remoção de mídias.
    Expõe: uploadMedia(), getMedias(), deleteMedia().
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # uploadMedia()
    # ------------------------------------------------------------------
    async def upload_media(self, file: UploadFile, user_id: int) -> MediaORM:
        """Salva o arquivo em disco e registra os metadados no banco."""
        if file.content_type not in ALLOWED_MIMETYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Tipo de arquivo não permitido: {file.content_type}",
            )

        extension = os.path.splitext(file.filename or "")[-1]
        unique_name = f"{uuid.uuid4().hex}{extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        media = MediaORM(
            url=f"/{UPLOAD_DIR}/{unique_name}",
            file_name=file.filename or unique_name,
            size=len(contents),
            mimetype=file.content_type,
            user_id=user_id,
        )
        self._db.add(media)
        self._db.commit()
        self._db.refresh(media)
        return media

    # ------------------------------------------------------------------
    # getMedias()
    # ------------------------------------------------------------------
    def get_medias(self, user_id: int) -> List[MediaORM]:
        """Lista todas as mídias de um usuário."""
        return (
            self._db.query(MediaORM)
            .filter(MediaORM.user_id == user_id)
            .all()
        )

    def get_todas_medias(self) -> List[MediaORM]:
        """Lista todas as mídias (uso administrativo)."""
        return self._db.query(MediaORM).all()

    # ------------------------------------------------------------------
    # deleteMedia()
    # ------------------------------------------------------------------
    def delete_media(self, media_id: int, user_id: int, is_admin: bool = False) -> None:
        """Remove uma mídia do banco e do disco."""
        media = self._db.query(MediaORM).filter(MediaORM.id == media_id).first()
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mídia não encontrada.",
            )
        if not is_admin and media.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para remover essa mídia.",
            )

        file_path = media.url.lstrip("/")
        if os.path.exists(file_path):
            os.remove(file_path)

        self._db.delete(media)
        self._db.commit()
