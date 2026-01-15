from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from pvdata.domain.presets import PVBuildingPreset


class PresetNotFoundError(KeyError):
    pass


class PresetRepository(ABC):
    @abstractmethod
    def get(self, building_id: str) -> PVBuildingPreset:
        """Liefert Preset oder wirft PresetNotFoundError."""
        raise NotImplementedError

    @abstractmethod
    def list_ids(self) -> List[str]:
        """Für Dropdowns/Autocomplete."""
        raise NotImplementedError

    def try_get(self, building_id: str) -> Optional[PVBuildingPreset]:
        try:
            return self.get(building_id)
        except PresetNotFoundError:
            return None
