from django.shortcuts import render, redirect
from django.urls import reverse

from ..models import SummerProtection, Building
from ..forms import SummerStep1Form, SummerStep2Form
from ..logic.summer import calc_summer_overheating

WINDOW_SHARE_THRESHOLD = 0.10  # 10%


def _get_or_create_default_instance():
    building = Building.objects.first()
    if building is None:
        return None, None

    instance, _ = SummerProtection.objects.get_or_create(
        id=1,
        defaults={"name": "Default summer scenario", "building": building},
    )

    if instance.building_id is None:
        instance.building = building
        instance.save()

    return instance, building


def summer_step1(request):
    instance, building = _get_or_create_default_instance()
    if instance is None:
        return render(request, "energyapp/summer_step1.html", {"form": None, "result": None})

    result = request.session.get("summer_step1_result")

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
            request.session["summer_step1_result"] = result

            if needs_proof:
                return redirect(reverse("summer_step2"))
            return redirect(reverse("summer_step1"))
    else:
        form = SummerStep1Form(instance=instance)

    return render(request, "energyapp/summer_step1.html", {"form": form, "result": result})


def summer_step2(request):
    instance, building = _get_or_create_default_instance()
    if instance is None:
        return render(request, "energyapp/summer_step2.html", {"form": None, "result": None, "step1": None})

    step1 = request.session.get("summer_step1_result")
    if not step1:
        return redirect(reverse("summer_step1"))

    result = request.session.get("summer_step2_result")

    if request.method == "POST":
        form = SummerStep2Form(request.POST, instance=instance)
        if form.is_valid():
            sp = form.save()
            result = calc_summer_overheating(sp)
            request.session["summer_step2_result"] = result
            return redirect(reverse("summer_step2"))
    else:
        form = SummerStep2Form(instance=instance)

    return render(request, "energyapp/summer_step2.html", {"form": form, "result": result, "step1": step1})
