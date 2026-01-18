# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Building, Energy, Water
from .forms import EnergyForm, WaterForm
from .berechnungen import calc_energy, calc_water


def lighting_water_edit(request, building_id):
    building = get_object_or_404(Building, pk=building_id)

    # =========================================================
    # 1) Forms vorbereiten
    # =========================================================
    if request.method == "POST":
        e_form = EnergyForm(request.POST)
        w_form = WaterForm(request.POST)

        if e_form.is_valid() and w_form.is_valid():
            energy_instance = e_form.save(commit=False)
            water_instance = w_form.save(commit=False)

            # Gebäude zuweisen
            energy_instance.building = building
            water_instance.building = building

            # Berechnungen durchführen
            energy_instance.calculate()
            water_instance.calculate()

            energy_instance.save()
            water_instance.save()

            return redirect("lighting_water_edit", building_id=building.id)

    else:
        e_form = EnergyForm()
        w_form = WaterForm()

    # =========================================================
    # 2) Berechnungen für alle Räume abrufen
    # =========================================================
    energy_results = calc_energy(building)
    water_results = calc_water(building)

    # =========================================================
    # 3) Template rendern
    # =========================================================
    context = {
        "building": building,
        "form": e_form,
        "w_form": w_form,
        "energy_results": energy_results,
        "water_results": water_results,
    }
    return render(request, "lighting_water.html", context)

