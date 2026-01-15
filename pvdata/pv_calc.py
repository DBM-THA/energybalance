from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

MONTHS = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

@dataclass(frozen=True)
class PVSurface:
    name: str
    orientation: str  # "N", "E", "S", "W", "H"
    tilt_deg: float   # 0..90
    area_m2: float    # >=0
    eta: float        # 0..1

@dataclass(frozen=True)
class PVInputs:
    annual_demand_kwh: float
    self_consumption_share: float  # 0..1
    radiation_kwh_m2: List[float]  # len=12
    surfaces: List[PVSurface]


def compute_pv(inputs: PVInputs) -> Dict[str, Any]:
    if len(inputs.radiation_kwh_m2) != 12:
        raise ValueError("radiation_kwh_m2 muss 12 Werte haben (Jan..Dez).")

    monthly_total = []
    for m_idx, month in enumerate(MONTHS):
        rad = float(inputs.radiation_kwh_m2[m_idx])
        prod_month = 0.0
        for s in inputs.surfaces:
            prod_month += rad * float(s.area_m2) * float(s.eta)
        monthly_total.append({
            "month": month,
            "radiation_kwh_m2": rad,
            "production_kwh": round(prod_month, 2),
        })

    annual_production = sum(r["production_kwh"] for r in monthly_total)

    annual_demand = float(inputs.annual_demand_kwh) if inputs.annual_demand_kwh is not None else 0.0
    coverage_ratio = (annual_production / annual_demand) if annual_demand > 0 else 0.0

    self_use_share = float(inputs.self_consumption_share)
    self_use_kwh = annual_production * self_use_share
    surplus_kwh = max(0.0, annual_production - self_use_kwh)

    total_area = sum(float(s.area_m2) for s in inputs.surfaces)

    return {
        "inputs": {
            "annual_demand_kwh": annual_demand,
            "self_consumption_share": self_use_share,
            "total_area_m2": round(total_area, 2),
        },
        "summary": {
            "annual_production_kwh": round(annual_production, 2),
            "coverage_ratio": round(coverage_ratio, 4),
            "self_use_kwh": round(self_use_kwh, 2),
            "surplus_kwh": round(surplus_kwh, 2),
        },
        "monthly": monthly_total,
    }
