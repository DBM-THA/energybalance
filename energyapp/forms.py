from .models import Building, SummerProtection
from django import forms

class SimpleBuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = [
            "name",
            "length_ns",
            "width_ow",
            "storeys",
            "room_height",
            "u_wall",
            "u_roof",
            "u_floor",
            "u_window",
            "air_change_rate",
            "degree_days",
            "setpoint_temp",
            "pv_roof_share",
            "pv_specific_yield",
            "pv_self_consumption_share",
        ]


class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = [
            "name",
            "length_ns",
            "width_ow",
            "storeys",
            "room_height",
            "u_wall",
            "u_roof",
            "u_floor",
            "u_window",
            "window_share_n",
            "window_share_e",
            "window_share_s",
            "window_share_w",
            "g_n",
            "g_e",
            "g_s",
            "g_w",
            "person_density",
            "persons",
            "air_change_rate",
            "degree_days",
            "setpoint_temp",
            "pv_roof_share",
            "pv_specific_yield",
            "pv_self_consumption_share",
        ]
        
class SummerProtectionForm(forms.ModelForm):
    class Meta:
        model = SummerProtection
        fields = [
            "name",
            "building",
            "orientation",
            "ngf_m2",
            "window_area_m2",
            "glazing_category",
            "shading_type",
            "climate_region",
            "night_ventilation",
            "passive_cooling",
        ]
        
from .models import SummerProtection

class SummerStep1Form(forms.ModelForm):
    class Meta:
        model = SummerProtection
        fields = [
            "building",
            "orientation",
            "ngf_m2",
            "window_area_m2",
        ]


class SummerStep2Form(forms.ModelForm):
    class Meta:
        model = SummerProtection
        fields = [
            "building",
            "orientation",
            "ngf_m2",
            "window_area_m2",
            "glazing_category",
            "shading_type",
            "climate_region",
            "night_ventilation",
            "passive_cooling",
        ]




from django import forms
from .models import GwpManufacturing, GwpCompensation


class GwpManufacturingForm(forms.ModelForm):
    class Meta:
        model = GwpManufacturing
        fields = [
            "new_components_gwp",
            "existing_components_gwp",
            "service_life_years",
        ]

class GwpCompensationForm(forms.ModelForm):
    class Meta:
        model = GwpCompensation
        fields = [
            "heat_district_regen_kwh",
            "heat_district_avg_kwh",
            "gas_kwh",
            "electricity_kwh",
        ]


# Internal Gains (Excel

class InternalGainsForm(forms.Form):
    # Allgemein
    area_m2 = forms.FloatField(
        label="Bezugsfläche [m²]",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )

    # Schritt 1 – Personen (blaue Excel Felder)
    persons_count = forms.FloatField(
        label="Menge Personen",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    persons_spec_w = forms.FloatField(
        label="spez. Leistung [W/P]",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    persons_h_per_day = forms.FloatField(
        label="Zeit Stunden pro Tag [h/d]",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    persons_days_per_year = forms.FloatField(
        label="Zeit Tage im Jahr [d/a]",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "1"}),
    )

    # Schritt 2 – Geräte (blaue Excel Felder)
    devices_count = forms.FloatField(
        label="Menge Geräte",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    devices_spec_w = forms.FloatField(
        label="spez. Leistung [W/Stk]",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    devices_h_per_day = forms.FloatField(
        label="Zeit Stunden pro Tag [h/d]",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    devices_days_per_year = forms.FloatField(
        label="Zeit Tage im Jahr [d/a]",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "1"}),
    )

    # Schritt 3 – Sonstige Wärmequellen (blaue Excel Felder)
    other_count = forms.FloatField(
        label="Menge sonstige Quellen",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    other_spec_w = forms.FloatField(
        label="Leistung [W]",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    other_h_per_day = forms.FloatField(
        label="Zeit Stunden pro Tag [h/d]",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    other_days_per_year = forms.FloatField(
        label="Zeit Tage im Jahr [d/a]",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "1"}),
    )
#---------------------------------
#Internal Gains
#-----------------------------------
from .models import InternalGains

class InternalGainsForm(forms.ModelForm):
    class Meta:
        model = InternalGains
        fields = [
            "area_m2",
            "persons_count",
            "persons_spec_w",
            "persons_h_per_day",
            "persons_days_per_year",
            "devices_count",
            "devices_spec_w",
            "devices_h_per_day",
            "devices_days_per_year",
            "other_count",
            "other_spec_w",
            "other_h_per_day",
            "other_days_per_year",
        ]
