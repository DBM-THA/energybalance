from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from energyapp.models import Building, GwpManufacturing


@login_required
def gwp_manufacturing_edit(request, building_id):
    building = get_object_or_404(Building, pk=building_id)
    manufacturing, _ = GwpManufacturing.objects.get_or_create(building=building)

    if request.method == "POST":
        manufacturing.kg300_new = float(request.POST.get("kg300_new") or 0)
        manufacturing.kg400_new = float(request.POST.get("kg400_new") or 0)
        manufacturing.kg300_existing = float(request.POST.get("kg300_existing") or 0)
        manufacturing.kg400_existing = float(request.POST.get("kg400_existing") or 0)
        manufacturing.service_life_years = float(request.POST.get("service_life_years") or 50)

        # Sicherheit: keine 0
        if manufacturing.service_life_years <= 0:
            manufacturing.service_life_years = 1

        manufacturing.save()
        return redirect("gwp_overview", building_id=building.id)

    return render(
        request,
        "energyapp/gwp_manufacturing_form.html",
        {"building": building, "manufacturing": manufacturing},
    )
