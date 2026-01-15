from dataclasses import dataclass
from typing import List, Dict, Any

MONTHS = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

@dataclass
class PVInputs:
    annual_demand_kwh: float
    eta_total: float
    radiation_kwh_m2: List[float]   # 12 Monatswerte (kWh/m²)
    area_m2: float | None = None    # optional


def compute_area_for_100pct(annual_demand_kwh: float, eta_total: float, radiation_kwh_m2: List[float]) -> float:
    denom = eta_total * sum(radiation_kwh_m2)
    if denom <= 0:
        raise ValueError("eta_total * Summe(Strahlung) muss > 0 sein.")
    return annual_demand_kwh / denom


def compute_pv(inputs: PVInputs) -> Dict[str, Any]:
    if len(inputs.radiation_kwh_m2) != 12:
        raise ValueError("Es werden genau 12 Monatswerte benötigt.")

    if inputs.annual_demand_kwh <= 0:
        raise ValueError("Endenergiebedarf muss > 0 sein.")

    # Schutz gegen typische Eingabefehler: 14 statt 0.14
    if inputs.eta_total <= 0 or inputs.eta_total > 2:
        raise ValueError("Gesamt-Wirkungsgrad scheint ungültig. Erwartet z.B. 0.14")

    area_source = "user"
    area = inputs.area_m2
    if area is None:
        area = compute_area_for_100pct(inputs.annual_demand_kwh, inputs.eta_total, inputs.radiation_kwh_m2)
        area_source = "computed_100pct"

    monthly = []
    for month, g in zip(MONTHS, inputs.radiation_kwh_m2):
        prod = area * g * inputs.eta_total
        monthly.append({"month": month, "radiation_kwh_m2": g, "production_kwh": prod})

    annual_production = sum(m["production_kwh"] for m in monthly)
    coverage_ratio = annual_production / inputs.annual_demand_kwh

    return {
        "inputs": {
            "annual_demand_kwh": inputs.annual_demand_kwh,
            "eta_total": inputs.eta_total,
            "area_m2": area,
            "area_source": area_source,
        },
        "summary": {
            "annual_production_kwh": annual_production,
            "coverage_ratio": coverage_ratio,
        },
        "monthly": monthly,
    }
