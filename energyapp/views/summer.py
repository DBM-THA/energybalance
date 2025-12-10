from django.shortcuts import render, redirect
from django.urls import reverse

from ..models import SummerProtection
from ..forms import SummerProtectionForm
from ..logic.summer import calc_summer_overheating


def summer_view(request):
    """
    Simple view for the summer overheating module.
    Uses a single SummerProtection instance (id=1) as default scenario.
    """

    # Ein einzelnes Standard-Szenario verwenden
    instance, created = SummerProtection.objects.get_or_create(
        id=1,
        defaults={"name": "Default summer scenario"},
    )

    if request.method == "POST":
        form = SummerProtectionForm(request.POST, instance=instance)
        if form.is_valid():
            sp = form.save()
            # Logic aufrufen → Berechnung & Dict mit Ergebnissen
            result = calc_summer_overheating(sp)
            # Nach POST redirect, damit kein Doppel-Submit
            request.session["summer_result"] = result
            return redirect(reverse("summer"))
    else:
        form = SummerProtectionForm(instance=instance)
        # Falls schon etwas gerechnet wurde, Ergebnis aus Session holen
        result = request.session.get("summer_result", None)
        if result is None:
            # einmal initial berechnen
            result = calc_summer_overheating(instance)
            request.session["summer_result"] = result

    context = {
        "form": form,
        "result": result,
    }
    return render(request, "energyapp/summer.html", context)
