from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.template.loader import select_template


from energyapp.models import Building

@login_required
def gwp_overview(request, building_id):
    building = get_object_or_404(Building, pk=building_id)
    print("VIEW NAME:", request.resolver_match.view_name)
    tmpl = select_template(["energyapp/gwp_overview.html"])
    print("TEMPLATE USED:", tmpl.template.name)
    print("TEMPLATE ORIGIN:", getattr(tmpl.template, "origin", None))

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
        }
    )
