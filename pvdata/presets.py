from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from energyapp.models import Building  # eure bestehende Infrastruktur


@dataclass(frozen=True)
class PVPreset:
    building_pk: int
    name: str
    annual_demand_kwh: float
    eta_total: float
    radiation_kwh_m2: List[float]   # 12 Werte
    area_m2: Optional[float] = None
    meta: Optional[Dict[str, Any]] = None


DEFAULT_RADIATION = [70, 65, 85, 110, 135, 150, 155, 140, 110, 90, 60, 50]
DEFAULT_ETA_TOTAL = 0.14


def get_pv_preset_by_pk(building_pk: int) -> PVPreset:
    """
    Minimaler Preset-Builder aus eurer DB.
    Später ersetzt/erweitert ihr Mapping + Monatswerte etc.
    """
    b = Building.objects.get(pk=building_pk)

    # Dachfläche grob (vereinfacht) aus length_ns * width_ow
    roof_area = float(b.length_ns) * float(b.width_ow)
    pv_area = roof_area * (float(b.pv_roof_share) / 100.0)

    # annual_demand_kwh:
    # aktuell habt ihr kein eindeutiges Strombedarfs-Feld.
    # Wir nutzen hier als Start: result_Q_h (falls existiert), ansonsten 1.0,
    # damit das Preset nicht kaputt geht.
    annual_demand = getattr(b, "result_Q_h", None)
    if annual_demand is None or float(annual_demand) <= 0:
        annual_demand = 1.0

    meta = {
        "roof_area_m2": roof_area,
        "pv_roof_share_pct": b.pv_roof_share,
        "pv_specific_yield_kwh_m2a": b.pv_specific_yield,
        "pv_self_consumption_share_pct": b.pv_self_consumption_share,
    }

    return PVPreset(
        building_pk=b.pk,
        name=b.name,
        annual_demand_kwh=float(annual_demand),
        eta_total=DEFAULT_ETA_TOTAL,
        radiation_kwh_m2=DEFAULT_RADIATION,
        area_m2=float(pv_area),
        meta=meta,
    )
