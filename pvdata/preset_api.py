from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .presets import get_pv_preset_by_pk


@require_GET
def pv_preset(request, pk: int):
    preset = get_pv_preset_by_pk(pk)
    return JsonResponse({
        "building_pk": preset.building_pk,
        "name": preset.name,
        "annual_demand_kwh": preset.annual_demand_kwh,
        "eta_total": preset.eta_total,
        "radiation_kwh_m2": preset.radiation_kwh_m2,
        "area_m2": preset.area_m2,
        "meta": preset.meta,
    }, json_dumps_params={"ensure_ascii": False})
