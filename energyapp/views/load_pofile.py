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