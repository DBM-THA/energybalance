from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from energyapp.models import Building, GwpManufacturing, GwpCompensation
from energyapp.forms import GwpManufacturingForm



def gwp_overview(request, building_id):
    building = get_object_or_404(Building, pk=building_id)
    manufacturing = getattr(building, "gwp_manufacturing", None)
    compensation = getattr(building, "gwp_compensation", None)

    return render(
        request,
        "energyapp/gwp_overview.html",
        {
            "building": building,
            "manufacturing": manufacturing,
            "compensation": compensation,
        },
    )


def gwp_manufacturing_edit(request, building_id):
    building = get_object_or_404(Building, pk=building_id)
    instance = GwpManufacturing.objects.get_or_create(building=building)[0]

    if request.method == "POST":
        form = GwpManufacturingForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect("gwp_overview", building_id=building.id)
    else:
        form = GwpManufacturingForm(instance=instance)

    return render(
        request,
        "energyapp/gwp_manufacturing_form.html",
        {"building": building, "form": form},
    )
