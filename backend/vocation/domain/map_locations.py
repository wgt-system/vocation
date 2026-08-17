from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

ResolutionSource = Literal["manual", "geocoder"]


@dataclass(frozen=True)
class MapLocationResolution:
    work_location_id: str
    latitude: float
    longitude: float
    resolution_source: ResolutionSource
    provider_key: str | None
    resolved_at: datetime
    resolved_query: str
