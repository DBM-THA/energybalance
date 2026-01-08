from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from energyapp.models import Building, GwpCompensation, GwpManufacturing
from energyapp.forms import GwpCompensationForm



def gwp_compensation_edit(request, building_id):
    building = get_object_or_404(Building, pk=building_id)
    manufacturing = getattr(building, "gwp_manufacturing", None)

    if manufacturing is None:
        return redirect("gwp_manufacturing_edit", building_id=building.id)

    instance, _ = GwpCompensation.objects.get_or_create(
        building=building, defaults={"manufacturing": manufacturing}
    )

    if request.method == "POST":
        form = GwpCompensationForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect("gwp_overview", building_id=building.id)
    else:
        form = GwpCompensationForm(instance=instance)

    return render(
        request,
        "energyapp/gwp_compensation_form.html",
        {"building": building, "form": form},
    )
