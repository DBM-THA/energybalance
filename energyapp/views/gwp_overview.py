from django.shortcuts import render, get_object_or_404

from energyapp.models import Building, GwpManufacturing, GwpCompensation


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
        }
    )
