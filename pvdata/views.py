from django.shortcuts import render
from .forms import PVCalcForm, PVMainForm, PVSurfaceFormSet
from .pv_calc import PVInputs, PVSurface, compute_pv

def pv_details(request):
    result = None

    # Hauptformular
    main_form = PVCalcForm(request.POST or None)

    # Formset für Flächen
    surface_formset = PVSurfaceFormSet(request.POST or None)

    if request.method == "POST" and main_form.is_valid() and surface_formset.is_valid():
        cd = main_form.cleaned_data

        radiation = [
            cd["rad_01"], cd["rad_02"], cd["rad_03"], cd["rad_04"],
            cd["rad_05"], cd["rad_06"], cd["rad_07"], cd["rad_08"],
            cd["rad_09"], cd["rad_10"], cd["rad_11"], cd["rad_12"],
        ]

        surfaces = []
        for f in surface_formset.cleaned_data:
            if not f:
                continue
            surfaces.append(PVSurface(
                name=f.get("name") or "",
                orientation=f["orientation"],
                tilt_deg=f["tilt_deg"],
                area_m2=f["area_m2"],
                eta=f["eta"],
            ))

        inputs = PVInputs(
            annual_demand_kwh=cd["annual_demand_kwh"],
            self_consumption_share=cd["self_consumption_share"],
            radiation_kwh_m2=radiation,
            surfaces=surfaces,
        )

        result = compute_pv(inputs)

    return render(request, "energyapp/pv_details.html", {
        "main_form": main_form,
        "surface_formset": surface_formset,
        "result": result,
    })
