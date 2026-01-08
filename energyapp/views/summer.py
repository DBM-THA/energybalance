from django.shortcuts import render, redirect
from django.urls import reverse

from ..models import SummerProtection, Building
from ..forms import SummerProtectionForm
from ..logic.summer import calc_summer_overheating


def summer_view(request):
    building = Building.objects.first()

    if building is None:
        return render(
            request,
            "energyapp/summer.html",
            {"form": None, "result": None},
        )

    instance, _ = SummerProtection.objects.get_or_create(
        id=1,
        defaults={
            "name": "Default summer scenario",
            "building": building,
        },
    )

    if request.method == "POST":
        form = SummerProtectionForm(request.POST, instance=instance)
        if form.is_valid():
            sp = form.save()
            result = calc_summer_overheating(sp)
            request.session["summer_result"] = result
            return redirect(reverse("summer"))
    else:
        form = SummerProtectionForm(instance=instance)
        result = request.session.get("summer_result")

    return render(
        request,
        "energyapp/summer.html",
        {
            "form": form,
            "result": result,
        },
    )
from django.shortcuts import render

def fc_info(request):
    return render(request, "energyapp/fc_info.html")

