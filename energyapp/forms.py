from .models import Building
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

from django import forms
from .models import GwpManufacturing, GwpCompensation


class GwpManufacturingForm(forms.ModelForm):
    class Meta:
        model = GwpManufacturing
        fields = [
            "kg300_new_gwp_total",
            "kg300_existing_gwp_total",
            "kg400_new_gwp_total",
            "kg400_existing_gwp_total",
            "kg300_new_service_life",
            "kg300_existing_service_life",
            "kg400_new_service_life",
            "kg400_existing_service_life",
        ]


class GwpCompensationForm(forms.ModelForm):
    class Meta:
        model = GwpCompensation
        fields = [
            "heat_district_kwh",
            "gas_kwh",
            "electricity_kwh",
            "factor_heat",
            "factor_gas",
            "factor_electricity",
            "pv_yield_kwh",
            "pv_factor",
        ]
