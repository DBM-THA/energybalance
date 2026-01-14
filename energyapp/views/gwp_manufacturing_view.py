from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from energyapp.models import Building, GwpManufacturing
from energyapp.forms import GwpManufacturingForm

@login_required
def gwp_manufacturing_edit(request, building_id):
    building = get_object_or_404(Building, pk=building_id)

    manufacturing, _ = GwpManufacturing.objects.get_or_create(building=building)

    if request.method == "POST":
        form = GwpManufacturingForm(request.POST, instance=manufacturing)
        if form.is_valid():
            form.save()
            return redirect("gwp_overview", building_id=building.id)
    else:
        form = GwpManufacturingForm(instance=manufacturing)

    return render(
        request,
        "energyapp/gwp_manufacturing_form.html",
        {"building": building, "manufacturing": manufacturing, "form": form},
    )
