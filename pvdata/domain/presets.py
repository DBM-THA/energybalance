from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

MONTHS = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


@dataclass(frozen=True)
class PVBuildingPreset:
    """
    Preset für PV-Berechnung, gebunden an eine Gebäude-ID.
    Das sind genau die Eingaben, die dein PV-Rechner braucht.
    """
    building_id: str
    name: str

    annual_demand_kwh: float
    eta_total: float
    radiation_kwh_m2: List[float]  # 12 Monatswerte

    # optional: vorhandene PV-Fläche (wenn Preset z.B. 'Ist-Anlage' abbildet)
    area_m2: Optional[float] = None

    # optional: Metadaten (Adresse, Klimaregion, Ausrichtung, etc.)
    meta: Optional[Dict[str, Any]] = None

    def validate(self) -> None:
        if not self.building_id:
            raise ValueError("building_id fehlt")
        if self.annual_demand_kwh <= 0:
            raise ValueError("annual_demand_kwh muss > 0 sein")
        if self.eta_total <= 0 or self.eta_total > 2:
            raise ValueError("eta_total scheint ungültig (erwarte z.B. 0.14)")
        if len(self.radiation_kwh_m2) != 12:
            raise ValueError("radiation_kwh_m2 muss genau 12 Werte enthalten")
        if any(x < 0 for x in self.radiation_kwh_m2):
            raise ValueError("Strahlungswerte dürfen nicht negativ sein")
        if self.area_m2 is not None and self.area_m2 < 0:
            raise ValueError("area_m2 darf nicht negativ sein")
