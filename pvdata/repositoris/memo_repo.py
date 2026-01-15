from __future__ import annotations
from typing import Dict, List
from pvdata.domain.presets import PVBuildingPreset
from pvdata.repositories.base import PresetRepository, PresetNotFoundError


class InMemoryPresetRepository(PresetRepository):
    def __init__(self, presets: Dict[str, PVBuildingPreset]):
        self.presets = presets

    def get(self, building_id: str) -> PVBuildingPreset:
        bid = str(building_id)
        if bid not in self.presets:
            raise PresetNotFoundError(f"Kein Preset für building_id={bid}")
        return self.presets[bid]

    def list_ids(self) -> List[str]:
        return sorted(self.presets.keys())
