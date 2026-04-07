"""Cliente HTTP para a API do Copernicus Data Space Ecosystem (CDSE).

Responsabilidades:
  - Autenticação via OpenID Connect (OAuth2 com grant_type=password)
  - Busca de produtos Sentinel-2 via OData catalogue
  - Download de bandas individuais via Nodes API
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

from app.models.satellite import BoundingBox, SatelliteImage

logger = logging.getLogger(__name__)

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu"
    "/auth/realms/CDSE/protocol/openid-connect/token"
)
CATALOGUE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"


class AuthenticationError(Exception):
    """Credenciais inválidas ou falha na autenticação."""


class CopernicusClient:
    def __init__(self, user: str, password: str) -> None:
        self._user = user
        self._password = password
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "RigTech/1.0"})
        self._token: Optional[str] = None

    # ------------------------------------------------------------------ auth

    def authenticate(self) -> None:
        """Obtém o token Bearer e configura o cabeçalho da sessão.

        Raises:
            AuthenticationError: se as credenciais forem inválidas.
        """
        resp = self._session.post(
            TOKEN_URL,
            data={
                "client_id": "cdse-public",
                "grant_type": "password",
                "username": self._user,
                "password": self._password,
            },
            timeout=30,
        )
        if resp.status_code != 200:
            raise AuthenticationError(
                f"Falha na autenticação ({resp.status_code}): {resp.text[:200]}"
            )
        self._token = resp.json()["access_token"]
        self._session.headers.update({"Authorization": f"Bearer {self._token}"})
        logger.info("Autenticação no Copernicus realizada com sucesso.")

    # ------------------------------------------------------------------ search

    def search(
        self,
        bbox: BoundingBox,
        start_date: datetime,
        end_date: datetime,
        max_cloud: float = 30.0,
        max_results: int = 10,
    ) -> list[SatelliteImage]:
        """Busca produtos Sentinel-2 L2A na área e período informados.

        Args:
            bbox: Bounding box da área de interesse.
            start_date: Data de início da busca.
            end_date: Data de fim da busca.
            max_cloud: Cobertura máxima de nuvens em %.
            max_results: Número máximo de resultados.

        Returns:
            Lista de SatelliteImage encontrados, ordenados por data (mais recente primeiro).
        """
        start = start_date.strftime("%Y-%m-%dT00:00:00.000Z")
        end = end_date.strftime("%Y-%m-%dT23:59:59.999Z")

        filter_query = (
            f"Collection/Name eq 'SENTINEL-2' and "
            f"Attributes/OData.CSC.StringAttribute/any("
            f"att:att/Name eq 'productType' and "
            f"att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and "
            f"Attributes/OData.CSC.DoubleAttribute/any("
            f"att:att/Name eq 'cloudCover' and "
            f"att/OData.CSC.DoubleAttribute/Value le {max_cloud}) and "
            f"ContentDate/Start gt {start} and "
            f"ContentDate/Start lt {end} and "
            f"OData.CSC.Intersects(area=geography'SRID=4326;{bbox.to_wkt()}')"
        )

        resp = self._session.get(
            CATALOGUE_URL,
            params={
                "$filter": filter_query,
                "$top": max_results,
                "$orderby": "ContentDate/Start desc",
            },
            timeout=60,
        )

        if resp.status_code != 200:
            logger.error(f"Erro na busca ({resp.status_code}): {resp.text[:300]}")
            return []

        images: list[SatelliteImage] = []
        for item in resp.json().get("value", []):
            try:
                cloud = next(
                    (
                        a["Value"]
                        for a in item.get("Attributes", [])
                        if a.get("Name") == "cloudCover"
                    ),
                    0.0,
                )
                images.append(
                    SatelliteImage(
                        image_id=item["Id"],
                        product_name=item["Name"],
                        acquisition_date=datetime.fromisoformat(
                            item["ContentDate"]["Start"].replace("Z", "+00:00")
                        ),
                        cloud_cover=float(cloud),
                        bbox=bbox,
                        download_url=(
                            f"https://zipper.dataspace.copernicus.eu/zip"
                            f"?productlist={item['Id']}"
                        ),
                    )
                )
            except (KeyError, ValueError) as exc:
                logger.warning(f"Item ignorado na busca: {exc}")
                continue

        logger.info(f"Busca retornou {len(images)} imagem(s).")
        return images

    # ------------------------------------------------------------------ download

    def download_band(
        self, image_id: str, band: str, dest_dir: Path
    ) -> Optional[Path]:
        """Baixa uma banda específica de um produto Sentinel-2.

        Navega a árvore de Nodes do produto para localizar o arquivo
        JP2 da banda solicitada (resolução 10m) e faz o download.

        Args:
            image_id: ID do produto no CDSE.
            band: Código da banda (ex: 'B04', 'B08').
            dest_dir: Diretório de destino para salvar o arquivo.

        Returns:
            Path do arquivo baixado, ou None em caso de falha.
        """
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / f"{image_id[:20]}_{band}.jp2"

        if dest_file.exists():
            logger.info(f"Banda {band} já existe localmente: {dest_file}")
            return dest_file

        band_url = self._locate_band_url(image_id, band)
        if not band_url:
            logger.error(f"Banda {band} não encontrada no produto {image_id[:20]}.")
            return None

        logger.info(f"Baixando banda {band}...")
        resp = self._session.get(band_url, stream=True, timeout=300)
        if resp.status_code != 200:
            logger.error(f"Falha no download da banda {band} ({resp.status_code}).")
            return None

        with open(dest_file, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)

        logger.info(f"Banda {band} salva em {dest_file}.")
        return dest_file

    # ------------------------------------------------------------------ helpers

    def _locate_band_url(self, image_id: str, band: str) -> Optional[str]:
        """Navega a árvore de Nodes do produto para encontrar a URL de download da banda.

        Estrutura esperada do Sentinel-2 L2A:
          Product.SAFE / GRANULE / L2A_... / IMG_DATA / R10m / *_B??_10m.jp2
        """
        base = f"{CATALOGUE_URL}({image_id})"

        # Nível 1: nós raiz → encontrar "GRANULE"
        roots = self._get_nodes(f"{base}/Nodes")
        granule_entry = next((n for n in roots if n.get("Name") == "GRANULE"), None)
        if not granule_entry:
            return None

        # Nível 2: dentro de GRANULE → nome do tile (ex: L2A_T24LXQ_...)
        granules = self._get_nodes(f"{base}/Nodes('GRANULE')/Nodes")
        if not granules:
            return None
        granule_name = granules[0]["Name"]

        granule_base = f"{base}/Nodes('GRANULE')/Nodes('{granule_name}')"

        # Nível 3: dentro do tile → encontrar "IMG_DATA"
        tile_nodes = self._get_nodes(f"{granule_base}/Nodes")
        img_data = next((n for n in tile_nodes if n.get("Name") == "IMG_DATA"), None)
        if not img_data:
            return None

        img_base = f"{granule_base}/Nodes('IMG_DATA')"

        # Nível 4: dentro de IMG_DATA → encontrar "R10m"
        img_nodes = self._get_nodes(f"{img_base}/Nodes")
        r10m = next((n for n in img_nodes if n.get("Name") == "R10m"), None)
        if not r10m:
            return None

        r10m_base = f"{img_base}/Nodes('R10m')"

        # Nível 5: listar arquivos da resolução 10m → localizar a banda
        band_nodes = self._get_nodes(f"{r10m_base}/Nodes")
        band_file = next(
            (n for n in band_nodes if f"_{band}_10m.jp2" in n.get("Name", "")),
            None,
        )
        if not band_file:
            return None

        return f"{r10m_base}/Nodes('{band_file['Name']}')/$value"

    def _get_nodes(self, url: str) -> list[dict]:
        """Retorna a lista de nós de um endpoint OData Nodes."""
        try:
            resp = self._session.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.json().get("value", [])
        except requests.RequestException as exc:
            logger.warning(f"Erro ao consultar nós: {exc}")
        return []
