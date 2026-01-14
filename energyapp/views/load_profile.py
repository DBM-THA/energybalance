"""
from django.shortcuts import render, get_object_or_404
from .models import EnergyProject
from .utils import EnergyCalculator


def project_detail_view(request, project_id):
    project = get_object_or_404(EnergyProject, pk=project_id)

    # Berechnung starten
    calc = EnergyCalculator(project)
    results = calc.monthly_calculation()

    context = {
        'project': project,
        'results': results,
        'monthly_data': results['monthly_data'],
    }
    return render(request, 'energy/results.html', context)

# energyapp/views/load_profile.py
from django.shortcuts import render, get_object_or_404
from energyapp.models import Building  # Passe den Pfad zu deinem Building-Model an
from energyapp.logic.load_profiles import EnergyCalculator


def energy_balance_view(request, pk):
    # Gebäude laden
    building = get_object_or_404(Building, pk=pk)

    # Berechnung über die Logic-Datei ausführen
    calc = EnergyCalculator(building)
    results = calc.calculate()  # Hier wird die oben definierte Funktion aufgerufen

    context = {
        'project': building,
        'results': results,
        'monthly_data': results['monthly_data'],
        # 'components' wird für die Lastgang-Tabelle (04) benötigt
        'components': results['components']
    }

    return render(request, 'energy/results.html', context)

#alt
from django.shortcuts import render, get_object_or_404, redirect
from energyapp.models import Building
from energyapp.logic.load_profiles import EnergyCalculator

def energy_balance_view(request, pk):
    # 1. Gebäude laden
    building = get_object_or_404(Building, pk=pk)

    # 2. Speichern-Logik (wenn der Button geklickt wurde)
    if request.method == 'POST':
        building.ngf = float(request.POST.get('ngf', building.ngf))
        building.luftwechselrate = float(request.POST.get('luftwechselrate', building.luftwechselrate))
        building.raum_soll_temp = float(request.POST.get('raum_soll_temp', building.raum_soll_temp))
        building.wrg_wirkungsgrad = float(request.POST.get('wrg_wirkungsgrad', building.wrg_wirkungsgrad))
        building.save()
        # Nach dem Speichern Seite neu laden, um die neuen Ergebnisse zu sehen
        return redirect('energy_balance', pk=pk)

    # 3. Berechnungen durchführen (mit den aktuellen Werten)
    calc = EnergyCalculator(building)
    results = calc.calculate()

    context = {
        'project': building,
        'results': results,
        'monthly_data': results.get('monthly_data', [])
    }
    return render(request, 'energyapp/load_profile.html', context)
"""



from django.shortcuts import render, get_object_or_404, redirect
from energyapp.models import Building
from energyapp.logic.load_profiles import EnergyCalculator


def energy_balance_view(request, pk):
    building = get_object_or_404(Building, pk=pk)

    if request.method == 'POST':
        # Geometrie & U-Werte aus Formular speichern
        for field in ['length_ns', 'width_ow', 'storeys', 'room_height',
                      'u_wall', 'u_roof', 'u_floor', 'u_window',
                      'air_change_rate', 'setpoint_temp']:
            setattr(building, field, float(request.POST.get(field, getattr(building, field))))

        building.save()
        return redirect('energy_balance', pk=pk)

    # Berechnung ausführen
    calc = EnergyCalculator(building)
    results = calc.calculate()

    return render(request, 'energyapp/load_profile.html', {
        'project': building,
        'results': results
    })


