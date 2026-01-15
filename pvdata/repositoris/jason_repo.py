from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any

from pvdata.domain.presets import PVBuildingPreset
from pvdata.repositories.base import PresetRepository, PresetNotFoundError


class JsonPresetRepository(PresetRepository):
    def __init__(self, json_path: Path):
        self.json_path = json_path
        self._cache: Dict[str, PVBuildingPreset] | None = None

    def _load(self) -> Dict[str, PVBuildingPreset]:
        if self._cache is not None:
            return self._cache

        if not self.json_path.exists():
            self._cache = {}
            return self._cache

        raw = json.loads(self.json_path.read_text(encoding="utf-8"))
        presets: Dict[str, PVBuildingPreset] = {}

        for item in raw.get("presets", []):
            preset = PVBuildingPreset(
                building_id=str(item["building_id"]),
                name=str(item.get("name", item["building_id"])),
                annual_demand_kwh=float(item["annual_demand_kwh"]),
                eta_total=float(item["eta_total"]),
                radiation_kwh_m2=[float(x) for x in item["radiation_kwh_m2"]],
                area_m2=None if item.get("area_m2") in (None, "", "null") else float(item["area_m2"]),
                meta=item.get("meta"),
            )
            preset.validate()
            presets[preset.building_id] = preset

        self._cache = presets
        return presets

    def get(self, building_id: str) -> PVBuildingPreset:
        data = self._load()
        bid = str(building_id)
        if bid not in data:
            raise PresetNotFoundError(f"Kein Preset für building_id={bid}")
        return data[bid]

    def list_ids(self) -> List[str]:
        return sorted(self._load().keys())
