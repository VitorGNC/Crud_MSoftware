"""Cálculo de índices de vegetação (NDVI/EVI) e detecção de anomalias.

Utiliza rasterio para leitura das bandas JP2 do Sentinel-2 e numpy
para o cálculo matricial dos índices.

Fórmulas:
  NDVI = (NIR - Red) / (NIR + Red)          bandas B08 e B04
  EVI  = 2.5 * (NIR - Red) /                bandas B08, B04 e B02
         (NIR + 6*Red - 7.5*Blue + 1)

Valores Sentinel-2 L2A são escalonados por 10.000, portanto
dividimos antes do cálculo.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional
from uuid import uuid4

import numpy as np

from app.models.satellite import Anomaly, NDVIResult, Severity

logger = logging.getLogger(__name__)

# Amostragem espacial para detecção de anomalias.
# 1 ponto a cada STRIDE pixels evita gerar milhões de objetos
# em imagens de 10.000 x 10.000 px.
_ANOMALY_STRIDE = 50
_MAX_ANOMALIES = 200


class NDVICalculator:
    """Classe estática — não mantém estado entre chamadas."""

    # ------------------------------------------------------------------ NDVI

    @staticmethod
    def compute_ndvi(b04_path: Path, b08_path: Path) -> NDVIResult:
        """Calcula o NDVI a partir das bandas Red (B04) e NIR (B08).

        Args:
            b04_path: Caminho do arquivo JP2 da banda B04 (Red, 10m).
            b08_path: Caminho do arquivo JP2 da banda B08 (NIR, 10m).

        Returns:
            NDVIResult com o array NDVI e estatísticas.
        """
        import rasterio

        with rasterio.open(b04_path) as red_ds:
            red = red_ds.read(1).astype(np.float32)
            transform = red_ds.transform
            crs = str(red_ds.crs)

        with rasterio.open(b08_path) as nir_ds:
            nir = nir_ds.read(1).astype(np.float32)

        # Sentinel-2 L2A: valores escalonados por 10.000
        red = red / 10_000.0
        nir = nir / 10_000.0

        denominator = nir + red
        ndvi = np.where(denominator == 0.0, 0.0, (nir - red) / denominator)
        ndvi = ndvi.astype(np.float32)

        image_id = b04_path.stem.split("_B04")[0]

        result = NDVIResult(
            image_id=image_id,
            ndvi_array=ndvi,
            min_value=float(np.nanmin(ndvi)),
            max_value=float(np.nanmax(ndvi)),
            mean_value=float(np.nanmean(ndvi)),
            transform=transform,
            crs=crs,
        )
        logger.info(
            f"NDVI calculado — min={result.min_value:.3f} "
            f"max={result.max_value:.3f} mean={result.mean_value:.3f}"
        )
        return result

    # ------------------------------------------------------------------ EVI

    @staticmethod
    def compute_evi(
        b02_path: Path, b04_path: Path, b08_path: Path
    ) -> NDVIResult:
        """Calcula o EVI (Enhanced Vegetation Index).

        Args:
            b02_path: Banda B02 (Blue, 10m).
            b04_path: Banda B04 (Red, 10m).
            b08_path: Banda B08 (NIR, 10m).

        Returns:
            NDVIResult com o array EVI e estatísticas.
        """
        import rasterio

        with rasterio.open(b04_path) as red_ds:
            red = red_ds.read(1).astype(np.float32) / 10_000.0
            transform = red_ds.transform
            crs = str(red_ds.crs)

        with rasterio.open(b08_path) as nir_ds:
            nir = nir_ds.read(1).astype(np.float32) / 10_000.0

        with rasterio.open(b02_path) as blue_ds:
            blue = blue_ds.read(1).astype(np.float32) / 10_000.0

        denominator = nir + 6.0 * red - 7.5 * blue + 1.0
        evi = np.where(denominator == 0.0, 0.0, 2.5 * (nir - red) / denominator)
        evi = evi.astype(np.float32)

        image_id = b04_path.stem.split("_B04")[0]

        result = NDVIResult(
            image_id=image_id,
            ndvi_array=evi,
            min_value=float(np.nanmin(evi)),
            max_value=float(np.nanmax(evi)),
            mean_value=float(np.nanmean(evi)),
            transform=transform,
            crs=crs,
        )
        logger.info(
            f"EVI calculado — min={result.min_value:.3f} "
            f"max={result.max_value:.3f} mean={result.mean_value:.3f}"
        )
        return result

    # ------------------------------------------------------------------ anomalias

    @staticmethod
    def detect_anomalies(
        result: NDVIResult, threshold: float = 0.3
    ) -> list[Anomaly]:
        """Detecta regiões com NDVI abaixo do limiar.

        Amostra o array em grade (_ANOMALY_STRIDE pixels) para evitar
        gerar centenas de milhares de pontos em imagens grandes.
        Converte coordenadas pixel → WGS84 usando a transformação
        afim e a reprojeção do CRS original.

        Args:
            result: Resultado NDVI/EVI já calculado.
            threshold: Valor de corte (default 0.3 — vegetação esparsa).

        Returns:
            Lista de Anomaly com coordenadas geográficas e severidade.
        """
        from pyproj import Transformer

        transformer = Transformer.from_crs(
            result.crs, "EPSG:4326", always_xy=True
        )

        ndvi = result.ndvi_array
        rows, cols = ndvi.shape
        anomalies: list[Anomaly] = []

        for row in range(0, rows, _ANOMALY_STRIDE):
            for col in range(0, cols, _ANOMALY_STRIDE):
                val = float(ndvi[row, col])
                if val >= threshold:
                    continue

                # Pixel → coordenadas no CRS original (pode ser UTM)
                x, y = result.transform * (col, row)

                # CRS original → WGS84
                lon, lat = transformer.transform(x, y)

                severity = (
                    Severity.HIGH if val < 0.1
                    else Severity.MEDIUM if val < 0.2
                    else Severity.LOW
                )

                anomalies.append(
                    Anomaly(
                        anomaly_id=str(uuid4()),
                        image_id=result.image_id,
                        latitude=lat,
                        longitude=lon,
                        ndvi_value=val,
                        severity=severity,
                    )
                )

                if len(anomalies) >= _MAX_ANOMALIES:
                    logger.info(f"Limite de {_MAX_ANOMALIES} anomalias atingido.")
                    return anomalies

        logger.info(f"{len(anomalies)} anomalia(s) detectada(s).")
        return anomalies

    # ------------------------------------------------------------------ visualização

    @staticmethod
    def to_image(result: NDVIResult, width: int = 400, height: int = 300):
        """Gera uma imagem PIL colorida do array NDVI para exibição na GUI.

        Paleta de cores:
          NDVI < 0  → cinza  (água / nuvem)
          0 – 0.2   → vermelho (solo / falha)
          0.2 – 0.4 → amarelo (vegetação esparsa)
          0.4 – 0.6 → verde claro (vegetação moderada)
          > 0.6     → verde escuro (vegetação densa)
        """
        from PIL import Image

        ndvi = np.clip(result.ndvi_array, -1.0, 1.0)
        h, w = ndvi.shape

        r = np.zeros((h, w), dtype=np.uint8)
        g = np.zeros((h, w), dtype=np.uint8)
        b = np.zeros((h, w), dtype=np.uint8)

        # Cinza — abaixo de 0
        mask_neg = ndvi < 0
        r[mask_neg] = 128
        g[mask_neg] = 128
        b[mask_neg] = 128

        # Vermelho — 0 a 0.2
        mask_low = (ndvi >= 0) & (ndvi < 0.2)
        r[mask_low] = 200
        g[mask_low] = 50
        b[mask_low] = 50

        # Amarelo — 0.2 a 0.4
        mask_med = (ndvi >= 0.2) & (ndvi < 0.4)
        r[mask_med] = 220
        g[mask_med] = 200
        b[mask_med] = 50

        # Verde claro — 0.4 a 0.6
        mask_good = (ndvi >= 0.4) & (ndvi < 0.6)
        r[mask_good] = 100
        g[mask_good] = 200
        b[mask_good] = 80

        # Verde escuro — acima de 0.6
        mask_high = ndvi >= 0.6
        r[mask_high] = 30
        g[mask_high] = 130
        b[mask_high] = 30

        rgb = np.stack([r, g, b], axis=-1)
        img = Image.fromarray(rgb, mode="RGB")
        img = img.resize((width, height), Image.NEAREST)
        return img
