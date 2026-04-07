"""Serviço de análise de imagens de satélite Sentinel-2 (RF01).

Orquestra:
  1. Autenticação no Copernicus Data Space
  2. Busca de imagens disponíveis para uma área e período
  3. Download das bandas necessárias (B04 Red, B08 NIR)
  4. Cálculo do NDVI com NDVICalculator
  5. Detecção de anomalias e emissão de eventos via SatelliteEventBus
  6. Persistência de resultados via SatelliteRepository
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from app.models.satellite import Anomaly, BoundingBox, NDVIResult, SatelliteImage
from app.patterns.observer import EventoSatelite, SatelliteEventBus
from app.repository.satellite_repository import SatelliteRepository
from app.utils.copernicus_client import AuthenticationError, CopernicusClient
from app.utils.logger_adapter import LoggerAdapter
from app.utils.ndvi_calculator import NDVICalculator

_BANDS_DIR = Path("data/satellite/bands")


class SatelliteService:
    def __init__(
        self,
        repository: SatelliteRepository,
        logger: LoggerAdapter,
    ) -> None:
        self._repository = repository
        self._logger = logger
        self._client: Optional[CopernicusClient] = None

    # ------------------------------------------------------------------ auth

    def configure_credentials(self, user: str, password: str) -> None:
        """Instancia e autentica o cliente Copernicus.

        Raises:
            AuthenticationError: se as credenciais forem inválidas.
        """
        client = CopernicusClient(user, password)
        client.authenticate()
        self._client = client
        self._log("Credenciais Copernicus configuradas com sucesso.")

    @property
    def is_authenticated(self) -> bool:
        return self._client is not None

    # ------------------------------------------------------------------ busca

    def search_images(
        self,
        bbox: BoundingBox,
        start_date: datetime,
        end_date: datetime,
        max_cloud: float = 30.0,
    ) -> list[SatelliteImage]:
        """Busca imagens Sentinel-2 disponíveis para a área e período.

        Raises:
            RuntimeError: se não houver credenciais configuradas.
        """
        self._require_auth()
        images = self._client.search(bbox, start_date, end_date, max_cloud)

        for img in images:
            self._repository.save_image(img)

        SatelliteEventBus.emitir(
            EventoSatelite.BUSCA_REALIZADA,
            {"quantidade": len(images), "bbox": bbox.to_dict()},
        )
        self._log(f"Busca retornou {len(images)} imagem(s).")
        return images

    # ------------------------------------------------------------------ processamento

    def process_image(
        self, image_id: str, index: str = "ndvi"
    ) -> NDVIResult:
        """Baixa as bandas de uma imagem e calcula NDVI ou EVI.

        Args:
            image_id: ID do produto no CDSE.
            index: 'ndvi' (padrão) ou 'evi'.

        Returns:
            NDVIResult com o array calculado.

        Raises:
            RuntimeError: se o download das bandas falhar.
        """
        self._require_auth()

        self._log(f"Baixando bandas da imagem {image_id[:20]}...")
        b04 = self._client.download_band(image_id, "B04", _BANDS_DIR)
        b08 = self._client.download_band(image_id, "B08", _BANDS_DIR)

        if not b04 or not b08:
            raise RuntimeError(
                f"Falha ao baixar bandas da imagem {image_id[:20]}. "
                "Verifique as credenciais e a disponibilidade do produto."
            )

        self._log(f"Calculando {index.upper()}...")
        if index == "evi":
            b02 = self._client.download_band(image_id, "B02", _BANDS_DIR)
            if not b02:
                raise RuntimeError("Falha ao baixar banda B02 para EVI.")
            result = NDVICalculator.compute_evi(b02, b04, b08)
        else:
            result = NDVICalculator.compute_ndvi(b04, b08)

        self._repository.save_result(result)

        SatelliteEventBus.emitir(
            EventoSatelite.NDVI_CALCULADO,
            {
                "image_id": image_id,
                "mean": result.mean_value,
                "index": index.upper(),
            },
        )
        self._log(
            f"{index.upper()} calculado — média={result.mean_value:.3f}"
        )
        return result

    # ------------------------------------------------------------------ anomalias

    def detect_anomalies(
        self, result: NDVIResult, threshold: float = 0.3
    ) -> list[Anomaly]:
        """Detecta e persiste anomalias no resultado NDVI/EVI.

        Emite EventoSatelite.ANOMALIA_DETECTADA para cada anomalia de
        severidade ALTA, permitindo que observers (ex: GUI) exibam alertas.

        Args:
            result: Resultado NDVI/EVI já calculado.
            threshold: Limiar NDVI (default 0.3).

        Returns:
            Lista de anomalias detectadas.
        """
        anomalies = NDVICalculator.detect_anomalies(result, threshold)
        self._repository.save_anomalies(anomalies)

        for anomaly in anomalies:
            SatelliteEventBus.emitir(
                EventoSatelite.ANOMALIA_DETECTADA,
                anomaly.to_dict(),
            )

        self._log(
            f"{len(anomalies)} anomalia(s) detectada(s) "
            f"(limiar NDVI < {threshold})."
        )
        return anomalies

    # ------------------------------------------------------------------ acesso a dados

    def get_result(self, image_id: str) -> Optional[NDVIResult]:
        return self._repository.get_result(image_id)

    def list_images(self) -> list[SatelliteImage]:
        return self._repository.list_images()

    def list_anomalies(self, image_id: Optional[str] = None) -> list[Anomaly]:
        return self._repository.list_anomalies(image_id)

    # ------------------------------------------------------------------ helpers

    def _require_auth(self) -> None:
        if not self._client:
            raise RuntimeError(
                "Credenciais não configuradas. "
                "Chame configure_credentials() antes de usar o serviço."
            )

    def _log(self, message: str) -> None:
        self._logger.info(f"[SatelliteService] {message}")
