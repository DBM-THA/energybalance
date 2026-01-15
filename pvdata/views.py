import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_http_methods

from .forms import PVCalcForm
from .pv_calc import PVInputs, compute_pv
from .presets import get_pv_preset_by_pk

def pv_calculator(request):
    preset = None
    building_pk = request.GET.get("building")

    initial = {}
    if building_pk:
        preset = get_pv_preset_by_pk(int(building_pk))
        initial = {
            "annual_demand_kwh": preset.annual_demand_kwh,
            "eta_total": preset.eta_total,
            "area_m2": preset.area_m2,
        }
        # Monatswerte in rad_01..rad_12
        for i, val in enumerate(preset.radiation_kwh_m2, start=1):
            initial[f"rad_{i:02d}"] = val

    form = PVCalcForm(request.POST or None, initial=initial if request.method != "POST" else None)
    ...


@xframe_options_exempt  # erlaubt Einbettung per iFrame (wenn ihr das nutzt)
@require_http_methods(["GET", "POST"])
def pv_calculator(request):
    result = None
    form = PVCalcForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        radiation = [form.cleaned_data[f"rad_{i:02d}"] for i in range(1, 13)]
        area = form.cleaned_data.get("area_m2") or None

        inputs = PVInputs(
            annual_demand_kwh=form.cleaned_data["annual_demand_kwh"],
            eta_total=form.cleaned_data["eta_total"],
            radiation_kwh_m2=radiation,
            area_m2=area,
        )
        result = compute_pv(inputs)

    return render(request, "pvdata/calculator.html", {"form": form, "result": result})


@require_http_methods(["POST"])
def pv_compute_api(request):
    """
    POST JSON:
    {
      "annual_demand_kwh": 25906,
      "eta_total": 0.140194,
      "area_m2": null,
      "radiation_kwh_m2": [..12..]
    }
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
        inputs = PVInputs(
            annual_demand_kwh=float(payload["annual_demand_kwh"]),
            eta_total=float(payload["eta_total"]),
            radiation_kwh_m2=[float(x) for x in payload["radiation_kwh_m2"]],
            area_m2=None if payload.get("area_m2") in (None, "", "null") else float(payload["area_m2"]),
        )
        return JsonResponse(compute_pv(inputs), json_dumps_params={"ensure_ascii": False})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
