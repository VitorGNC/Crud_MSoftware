"""Modelos de domínio para análise de imagens de satélite (RF01)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class Severity(Enum):
    LOW = "low"        # 0.2 <= NDVI < 0.3
    MEDIUM = "medium"  # 0.1 <= NDVI < 0.2
    HIGH = "high"      # NDVI < 0.1


@dataclass
class BoundingBox:
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float

    def to_wkt(self) -> str:
        """Retorna a geometria em formato WKT POLYGON para uso na API OData."""
        return (
            f"POLYGON(("
            f"{self.min_lon} {self.min_lat},"
            f"{self.max_lon} {self.min_lat},"
            f"{self.max_lon} {self.max_lat},"
            f"{self.min_lon} {self.max_lat},"
            f"{self.min_lon} {self.min_lat}"
            f"))"
        )

    def center(self) -> tuple[float, float]:
        """Retorna (lat, lon) do centro do bounding box."""
        return (self.min_lat + self.max_lat) / 2, (self.min_lon + self.max_lon) / 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_lat": self.min_lat,
            "min_lon": self.min_lon,
            "max_lat": self.max_lat,
            "max_lon": self.max_lon,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BoundingBox:
        return cls(
            min_lat=data["min_lat"],
            min_lon=data["min_lon"],
            max_lat=data["max_lat"],
            max_lon=data["max_lon"],
        )


@dataclass
class SatelliteImage:
    image_id: str
    product_name: str
    acquisition_date: datetime
    cloud_cover: float
    bbox: BoundingBox
    download_url: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_id": self.image_id,
            "product_name": self.product_name,
            "acquisition_date": self.acquisition_date.isoformat(),
            "cloud_cover": self.cloud_cover,
            "bbox": self.bbox.to_dict(),
            "download_url": self.download_url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SatelliteImage:
        return cls(
            image_id=data["image_id"],
            product_name=data["product_name"],
            acquisition_date=datetime.fromisoformat(data["acquisition_date"]),
            cloud_cover=data["cloud_cover"],
            bbox=BoundingBox.from_dict(data["bbox"]),
            download_url=data["download_url"],
        )

    def label(self) -> str:
        """Rótulo legível para exibição na GUI."""
        return (
            f"{self.product_name[:30]}  |  "
            f"{self.acquisition_date.strftime('%d/%m/%Y')}  |  "
            f"Nuvens: {self.cloud_cover:.1f}%"
        )


@dataclass
class NDVIResult:
    image_id: str
    ndvi_array: Any          # numpy ndarray
    min_value: float
    max_value: float
    mean_value: float
    transform: Any           # rasterio Affine transform
    crs: str                 # CRS original das bandas (ex: EPSG:32724)
    computed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa metadados (sem o array, salvo separado como .npy)."""
        return {
            "image_id": self.image_id,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "mean_value": self.mean_value,
            "crs": self.crs,
            "computed_at": self.computed_at.isoformat(),
        }


@dataclass
class Anomaly:
    anomaly_id: str
    image_id: str
    latitude: float
    longitude: float
    ndvi_value: float
    severity: Severity
    detected_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anomaly_id": self.anomaly_id,
            "image_id": self.image_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "ndvi_value": self.ndvi_value,
            "severity": self.severity.value,
            "detected_at": self.detected_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Anomaly:
        return cls(
            anomaly_id=data["anomaly_id"],
            image_id=data["image_id"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            ndvi_value=data["ndvi_value"],
            severity=Severity(data["severity"]),
            detected_at=datetime.fromisoformat(data["detected_at"]),
        )

    def label(self) -> str:
        sev_map = {"low": "BAIXA", "medium": "MEDIA", "high": "ALTA"}
        sev = sev_map.get(self.severity.value, self.severity.value)
        return (
            f"[{sev}] NDVI={self.ndvi_value:.3f}  "
            f"Lat={self.latitude:.5f}  Lon={self.longitude:.5f}"
        )
