from django.shortcuts import render, get_object_or_404, redirect

from energyapp.models import Building, GwpCompensation
from energyapp.forms import GwpCompensationForm


def _pick_attr(obj, candidates, default=0.0):
    """
    Nimmt den ersten existierenden Attributnamen aus candidates.
    Gibt default zurück, wenn nichts existiert oder Wert None ist.
    """
    for name in candidates:
        if hasattr(obj, name):
            val = getattr(obj, name)
            if val is None:
                return float(default)
            try:
                return float(val)
            except (TypeError, ValueError):
                return float(default)
    return float(default)


def _find_form_field(form, keywords):
    """
    Sucht in form.fields nach einem Feld, dessen Name alle keywords enthält.
    Beispiel keywords=["fern", "regen"] findet z.B. "fernwaerme_regenerativ_kwh_a".
    """
    kws = [k.lower() for k in keywords]
    for field_name in form.fields.keys():
        lower = field_name.lower()
        if all(k in lower for k in kws):
            return field_name
    return None


def gwp_compensation_edit(request, building_id):
    building = get_object_or_404(Building, pk=building_id)
    manufacturing = getattr(building, "gwp_manufacturing", None)

    # optional: erst Kompensation erlauben, wenn Herstellung existiert
    if manufacturing is None:
        return redirect("gwp_manufacturing_edit", building_id=building.id)

    instance, _ = GwpCompensation.objects.get_or_create(building=building)

    # =========================================================
    # 1) AUTO-WERTE aus "anderen Gruppen" holen (robuste Suche)
    # =========================================================
    # Diese Funktion sucht nach typischen Feldnamen am Building.
    # Wenn eure echten Felder existieren, werden sie automatisch verwendet.
    # Falls nicht, bleibt es bei 0.0.

    auto_fw_regen_kwh_a = _pick_attr(
        building,
        [
            # häufige Kandidaten
            "fernwaerme_regenerativ_kwh_a",
            "fernwaerme_regenerativ",
            "district_heat_renewable_kwh_a",
            "district_heating_renewable_kwh_a",
            "fw_regen_kwh_a",
            "fw_regenerativ_kwh_a",
            # manchmal in Ergebnissen/summary gespeichert
            "heat_district_renewable_kwh_a",
            "q_fernwaerme_regen",
        ],
        default=0.0,
    )

    auto_fw_avg_kwh_a = _pick_attr(
        building,
        [
            "fernwaerme_durchschnitt_kwh_a",
            "fernwaerme_durchschnitt",
            "district_heat_average_kwh_a",
            "district_heating_average_kwh_a",
            "fw_avg_kwh_a",
            "fw_durchschnitt_kwh_a",
            "heat_district_average_kwh_a",
            "q_fernwaerme_avg",
        ],
        default=0.0,
    )

    # CO2-Faktoren: Default wie bei euch im UI/Screenshot
    auto_co2_fw_regen = _pick_attr(
        building,
        [
            "co2_factor_fernwaerme_regenerativ",
            "co2_fernwaerme_regenerativ",
            "co2_factor_district_heat_renewable",
        ],
        default=0.0,
    )

    auto_co2_fw_avg = _pick_attr(
        building,
        [
            "co2_factor_fernwaerme_durchschnitt",
            "co2_fernwaerme_durchschnitt",
            "co2_factor_district_heat_average",
        ],
        default=0.28,  # bei euch steht 0,28
    )

    # =========================================================
    # 2) Ziel-Felder im Form automatisch finden (ohne Raten!)
    # =========================================================
    # Wir erzeugen ein leeres Form, um Feldnamen zu sehen.
    probe_form = GwpCompensationForm(instance=instance)

    FIELD_FW_REGEN_KWH = _find_form_field(probe_form, ["fern", "regen"])  # kWh/a
    FIELD_FW_AVG_KWH = _find_form_field(probe_form, ["fern", "durch"])    # kWh/a

    FIELD_CO2_FW_REGEN = _find_form_field(probe_form, ["co2", "fern", "regen"]) or _find_form_field(probe_form, ["faktor", "fern", "regen"])
    FIELD_CO2_FW_AVG = _find_form_field(probe_form, ["co2", "fern", "durch"]) or _find_form_field(probe_form, ["faktor", "fern", "durch"])

    # =========================================================
    # 3) Form Handling
    #    ✅ editierbar: wir setzen NUR initial (GET) und speichern User-Input (POST)
    #    ✅ initial nur wenn Wert noch 0/leer (damit User-Änderungen bleiben)
    # =========================================================
    if request.method == "POST":
        form = GwpCompensationForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect("gwp_overview", building_id=building.id)
    else:
        initial = {}

        # Nur vorbelegen, wenn die Felder existieren + instance dort noch leer/0 ist
        if FIELD_FW_REGEN_KWH and (getattr(instance, FIELD_FW_REGEN_KWH, 0) or 0) == 0:
            initial[FIELD_FW_REGEN_KWH] = auto_fw_regen_kwh_a

        if FIELD_FW_AVG_KWH and (getattr(instance, FIELD_FW_AVG_KWH, 0) or 0) == 0:
            initial[FIELD_FW_AVG_KWH] = auto_fw_avg_kwh_a

        if FIELD_CO2_FW_REGEN and (getattr(instance, FIELD_CO2_FW_REGEN, 0) or 0) == 0:
            initial[FIELD_CO2_FW_REGEN] = auto_co2_fw_regen

        if FIELD_CO2_FW_AVG and (getattr(instance, FIELD_CO2_FW_AVG, 0) or 0) == 0:
            initial[FIELD_CO2_FW_AVG] = auto_co2_fw_avg

        form = GwpCompensationForm(instance=instance, initial=initial)

    return render(
        request,
        "energyapp/gwp_compensation_form.html",
        {"building": building, "form": form},
    )
