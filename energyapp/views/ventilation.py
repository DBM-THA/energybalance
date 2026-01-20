from django.shortcuts import render, get_object_or_404
from energyapp.models import Building

def select_building_for_ventilation(request):
    buildings = Building.objects.all()
    return render(
        request,
        "energyapp/select_building.html",
        {"buildings": buildings},
    )


def ventilation_view(request, building_id):
    building = get_object_or_404(Building, pk=building_id)

    total_area = (
        building.ngf_t
        if building.ngf_t
        else building.length_ns * building.width_ow * building.storeys
    )

    context = {
        "building": building,
        "total_area": round(total_area, 2),
    }

    return render(request, "energyapp/ventilation.html", context)
