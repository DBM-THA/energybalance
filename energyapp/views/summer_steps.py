from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from ..models import SummerProtection, Building
from ..forms import SummerStep1Form, SummerStep2Form
from ..logic.summer import calc_summer_overheating

WINDOW_SHARE_THRESHOLD = 0.10  # 10%


def _get_or_create_instance_for_building(building: Building):
    instance, _ = SummerProtection.objects.get_or_create(
        building=building,
        defaults={"name": "Default summer scenario"},
    )
    return instance


def summer_step1(request, pk):
    building = get_object_or_404(Building, pk=pk)
    instance = _get_or_create_instance_for_building(building)

    result = request.session.get(f"summer_step1_result_{pk}")

    if request.method == "POST":
        form = SummerStep1Form(request.POST, instance=instance)
        if form.is_valid():
            sp = form.save()

            ngf = float(sp.ngf_m2 or 0.0)
            awin = float(sp.window_area_m2 or 0.0)

            share = (awin / ngf) if ngf > 0 else 0.0
            share_pct = share * 100.0
            threshold_pct = WINDOW_SHARE_THRESHOLD * 100.0

            needs_proof = share >= WINDOW_SHARE_THRESHOLD

            result = {
                "ngf_m2": round(ngf, 2),
                "window_area_m2": round(awin, 2),
                "window_share_pct": round(share_pct, 1),
                "threshold_pct": round(threshold_pct, 1),
                "needs_proof": needs_proof,
            }
            request.session[f"summer_step1_result_{pk}"] = result

            if needs_proof:
                return redirect(reverse("summer_step2", kwargs={"pk": pk}))
            return redirect(reverse("summer_step1", kwargs={"pk": pk}))
    else:
        form = SummerStep1Form(instance=instance)

    return render(
        request,
        "energyapp/summer_step1.html",
        {"form": form, "result": result, "building": building},
    )


def summer_step2(request, pk):
    building = get_object_or_404(Building, pk=pk)
    instance = _get_or_create_instance_for_building(building)

    step1 = request.session.get(f"summer_step1_result_{pk}")
    if not step1:
        return redirect(reverse("summer_step1", kwargs={"pk": pk}))

    result = request.session.get(f"summer_step2_result_{pk}")

    if request.method == "POST":
        form = SummerStep2Form(request.POST, instance=instance)
        if form.is_valid():
            sp = form.save()
            result = calc_summer_overheating(sp)
            request.session[f"summer_step2_result_{pk}"] = result
            return redirect(reverse("summer_step2", kwargs={"pk": pk}))
    else:
        form = SummerStep2Form(instance=instance)

    return render(
        request,
        "energyapp/summer_step2.html",
        {"form": form, "result": result, "step1": step1, "building": building},
    )
