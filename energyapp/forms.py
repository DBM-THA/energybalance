from .models import Building, SummerProtection, Sheet01EnergyResult, EnergyResultSheet01
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
class Sheet01EnergyResultForm(forms.ModelForm):
    class Meta:
        model = Sheet01EnergyResult
        fields = [
            # Kopf
            "project",
            "location",

            # Endenergie Wärme – Verlustfaktoren
            "factor_transfer_hw",
            "factor_distribution_hw",
            "factor_storage_hw",
            "factor_solar_generation",

            # Erzeuger-Anteile Wärme
            "share_wp",
            "share_fw",
            "share_gas",

            # Endenergie Faktoren
            "factor_fw_heat",
            "factor_gas_heat",
            "factor_aux_heat",

            # Primärenergie Faktoren
            "pe_factor_fw",
            "pe_factor_gas",
            "pe_factor_on_site",
            "pe_factor_off_site",

            # PV Deckungsanteil
            "pv_self_use_share",
        ]
        widgets = {
            "project": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "location": forms.TextInput(attrs={"class": "form-control form-control-sm"}),

            # Zahlenfelder etwas kompakter
            "factor_transfer_hw": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),
            "factor_distribution_hw": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),
            "factor_storage_hw": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),
            "factor_solar_generation": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),

            "share_wp": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01", "min": "0"}),
            "share_fw": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01", "min": "0"}),
            "share_gas": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01", "min": "0"}),

            "factor_fw_heat": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),
            "factor_gas_heat": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),
            "factor_aux_heat": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),

            "pe_factor_fw": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),
            "pe_factor_gas": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),
            "pe_factor_on_site": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),
            "pe_factor_off_site": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),

            "pv_self_use_share": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01", "min": "0", "max": "1"}),
        }
class EnergyResultSheet01Form(forms.ModelForm):
    class Meta:
        model = EnergyResultSheet01
        fields = [
            "project",
            "location",
            "E39_transfer_heat_water",
            "E40_distribution_heat_water",
            "E41_storage_heat_water",
            "E42_solar_generation_factor",
            "E47_factor_fw",
            "E48_factor_gas",
            "E49_aux_heating",
            "E51_air_support",
            "E52_lighting",
            "E53_user_process",
            "I78_pv_self_share",
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

