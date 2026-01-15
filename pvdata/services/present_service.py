from __future__ import annotations
from dataclasses import dataclass
from typing import List
from pvdata.domain.presets import PVBuildingPreset
from pvdata.repositories.base import PresetRepository


@dataclass
class PresetService:
    repo: PresetRepository

    def get_preset(self, building_id: str) -> PVBuildingPreset:
        preset = self.repo.get(building_id)
        preset.validate()
        return preset

    def list_buildings(self) -> List[str]:
        return self.repo.list_ids()
