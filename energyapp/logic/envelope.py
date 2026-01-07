from django.shortcuts import render, redirect
from django.forms import modelform_factory, inlineformset_factory
from .models import BuildingPart, Layer


===== Formulare DIREKT HIER =====
BuildingPartForm = modelform_factory(
    BuildingPart,
    fields=[
        "building_part",
        "name",
        "use_custom_layers",
        "u_value_external",
    ]
)

LayerFormSet = inlineformset_factory(
    BuildingPart,
    Layer,
    fields=[
        "layer_type",
        "name",
        "thickness",
        "lambda_value",
        "R_value",
    ],
    extra=3,
    can_delete=True
)


===== View =====
def envelope(request):
    if request.method == "POST":
        form = BuildingPartForm(request.POST)
        formset = LayerFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            part = form.save()
            formset.instance = part
            formset.save()

            # 🔢 U-Wert berechnen
            part.save()

            return redirect("/")  # oder Zielseite

    else:
        form = BuildingPartForm()
        formset = LayerFormSet()

    return render(
        request,
        "envelope.html",
        {
            "form": form,
            "formset": formset,
        }
    )