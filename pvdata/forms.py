from django import forms

MONTHS = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

class PVCalcForm(forms.Form):
    annual_demand_kwh = forms.FloatField(label="Endenergiebedarf gesamt (kWh/a)", min_value=0)
    eta_total = forms.FloatField(label="Gesamt-Wirkungsgrad (z.B. 0.14)", min_value=0)

    area_m2 = forms.FloatField(
        label="PV-Fläche (m²) optional (leer lassen = 100% Deckung berechnen)",
        required=False,
        min_value=0
    )

    for i, m in enumerate(MONTHS, start=1):
        locals()[f"rad_{i:02d}"] = forms.FloatField(label=f"Strahlung {m} (kWh/m²)", min_value=0)
