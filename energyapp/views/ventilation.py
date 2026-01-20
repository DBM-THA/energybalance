from django.shortcuts import render, get_object_or_404
from energyapp.models import Building


def select_building_for_ventilation(request):
    """
    Einstieg: Liste aller Gebäude anzeigen, damit der Nutzer ein Gebäude auswählt.
    URL: /ventilation/
    Template: energyapp/ventilation_select_building.html
    """
    buildings = Building.objects.all().order_by("name")
    return render(
        request,
        "energyapp/ventilation_select_building.html",
        {"buildings": buildings},
    )


def ventilation_view(request, building_id: int):
    """
    Detail: Ventilationsrechner für ein konkretes Gebäude.
    URL: /ventilation/<building_id>/
    Template: energyapp/ventilation.html
    Übergibt total_area an das Template.
    """
    building = get_object_or_404(Building, pk=building_id)

    # Fläche: bevorzugt NGF_t, sonst aus Geometrie ableiten
    total_area = (
        building.ngf_t
        if building.ngf_t is not None
        else (building.length_ns * building.width_ow * building.storeys)
    )

    context = {
        "building": building,
        "total_area": round(total_area, 2),
    }
    return render(request, "energyapp/ventilation.html", context)
