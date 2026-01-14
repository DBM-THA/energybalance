from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from energyapp.models import Building


def gwp_overview(request, building_id):
    building = get_object_or_404(Building, pk=building_id)

    manufacturing = getattr(building, "gwp_manufacturing", None)
    compensation = getattr(building, "gwp_compensation", None)

    manufacturing_url = reverse("gwp_manufacturing_edit", args=[building.id])

    return render(
        request,
        "energyapp/gwp_overview.html",
        {
            "building": building,
            "manufacturing": manufacturing,
            "compensation": compensation,
            "manufacturing_url": manufacturing_url,
        },
    )
