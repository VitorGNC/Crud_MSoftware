"""Repositório para persistência de imagens de satélite, resultados NDVI e anomalias."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np

from app.models.satellite import Anomaly, NDVIResult, SatelliteImage

logger = logging.getLogger(__name__)


class SatelliteRepository:
    """Persiste metadados em JSON e arrays numpy em arquivos .npy.

    Estrutura em disco:
        base_dir/
          images.json          ← lista de SatelliteImage
          anomalies.json       ← lista de Anomaly
          ndvi/
            {image_id}.npy     ← array NDVI/EVI
            {image_id}.json    ← metadados NDVIResult (sem o array)
    """

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._ndvi_dir = base_dir / "ndvi"
        self._images_file = base_dir / "images.json"
        self._anomalies_file = base_dir / "anomalies.json"

        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._ndvi_dir.mkdir(parents=True, exist_ok=True)

        for f in (self._images_file, self._anomalies_file):
            if not f.exists():
                f.write_text("[]", encoding="utf-8")

    # ------------------------------------------------------------------ imagens

    def save_image(self, image: SatelliteImage) -> None:
        images = self._load_json(self._images_file)
        images = [i for i in images if i["image_id"] != image.image_id]
        images.append(image.to_dict())
        self._save_json(self._images_file, images)

    def list_images(self) -> list[SatelliteImage]:
        return [
            SatelliteImage.from_dict(d) for d in self._load_json(self._images_file)
        ]

    def get_image(self, image_id: str) -> Optional[SatelliteImage]:
        for d in self._load_json(self._images_file):
            if d["image_id"] == image_id:
                return SatelliteImage.from_dict(d)
        return None

    # ------------------------------------------------------------------ ndvi

    def save_result(self, result: NDVIResult) -> None:
        """Salva metadados em JSON e array em .npy."""
        meta_path = self._ndvi_dir / f"{result.image_id}.json"
        npy_path = self._ndvi_dir / f"{result.image_id}.npy"

        meta_path.write_text(
            json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        np.save(str(npy_path), result.ndvi_array)
        logger.info(f"NDVIResult salvo: {result.image_id}")

    def get_result(self, image_id: str) -> Optional[NDVIResult]:
        meta_path = self._ndvi_dir / f"{image_id}.json"
        npy_path = self._ndvi_dir / f"{image_id}.npy"

        if not meta_path.exists() or not npy_path.exists():
            return None

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        ndvi_array = np.load(str(npy_path))

        # transform e crs não são serializados — retornados sem eles
        # (suficiente para exibição; reanálise requer download das bandas)
        from datetime import datetime

        return NDVIResult(
            image_id=meta["image_id"],
            ndvi_array=ndvi_array,
            min_value=meta["min_value"],
            max_value=meta["max_value"],
            mean_value=meta["mean_value"],
            transform=None,
            crs=meta["crs"],
            computed_at=datetime.fromisoformat(meta["computed_at"]),
        )

    # ------------------------------------------------------------------ anomalias

    def save_anomalies(self, anomalies: list[Anomaly]) -> None:
        existing = self._load_json(self._anomalies_file)
        if anomalies:
            image_id = anomalies[0].image_id
            existing = [a for a in existing if a["image_id"] != image_id]
        existing.extend(a.to_dict() for a in anomalies)
        self._save_json(self._anomalies_file, existing)

    def list_anomalies(self, image_id: Optional[str] = None) -> list[Anomaly]:
        all_anomalies = [
            Anomaly.from_dict(d) for d in self._load_json(self._anomalies_file)
        ]
        if image_id:
            return [a for a in all_anomalies if a.image_id == image_id]
        return all_anomalies

    # ------------------------------------------------------------------ helpers

    def _load_json(self, path: Path) -> list:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_json(self, path: Path, data: list) -> None:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
