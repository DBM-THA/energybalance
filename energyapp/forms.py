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


from django import forms
from .models import GwpManufacturing

class GwpManufacturingForm(forms.ModelForm):
    class Meta:
        model = GwpManufacturing
        fields = [
            "kg300_new",
            "kg300_existing",
            "kg400_new",
            "kg400_existing",
            "service_life_years",
        ]
        widgets = {
            "kg300_new": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "kg300_existing": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "kg400_new": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "kg400_existing": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "service_life_years": forms.NumberInput(attrs={"step": "1", "min": "1"}),
        }



from django import forms
from .models import GwpCompensation


class GwpCompensationForm(forms.ModelForm):
    class Meta:
        model = GwpCompensation
        fields = [
            "heat_district_regen_kwh",
            "heat_district_avg_kwh",
            "gas_kwh",
            "electricity_kwh",
            "factor_heat_regen",
            "factor_heat_avg",
            "factor_gas",
            "factor_electricity",
        ]



