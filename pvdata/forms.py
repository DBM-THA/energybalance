from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import formset_factory

ORIENTATION_CHOICES = [
    ("S", "Süd"),
    ("E", "Ost"),
    ("W", "West"),
    ("N", "Nord"),
    ("H", "Horizontal/Dach"),
]

class PVMainForm(forms.Form):
    annual_demand_kwh = forms.FloatField(
        label="Endenergiebedarf gesamt [kWh/a]",
        validators=[MinValueValidator(0.0)],
        widget=forms.NumberInput(attrs={"min": "0", "step": "1", "required": True}),
    )

    self_consumption_share = forms.FloatField(
        label="Eigenverbrauchsanteil [0..1]",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        initial=0.7,
        widget=forms.NumberInput(attrs={"min": "0", "max": "1", "step": "0.01", "required": True}),
    )

    rad_01 = forms.FloatField(label="Jan", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))
    rad_02 = forms.FloatField(label="Feb", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))
    rad_03 = forms.FloatField(label="Mrz", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))
    rad_04 = forms.FloatField(label="Apr", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))
    rad_05 = forms.FloatField(label="Mai", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))
    rad_06 = forms.FloatField(label="Jun", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))
    rad_07 = forms.FloatField(label="Jul", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))
    rad_08 = forms.FloatField(label="Aug", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))
    rad_09 = forms.FloatField(label="Sep", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))
    rad_10 = forms.FloatField(label="Okt", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))
    rad_11 = forms.FloatField(label="Nov", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))
    rad_12 = forms.FloatField(label="Dez", validators=[MinValueValidator(0.0)], widget=forms.NumberInput(attrs={"min":"0","step":"1"}))


class PVSurfaceForm(forms.Form):
    name = forms.CharField(
        label="PV-Fläche Name",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "z.B. Süd 90°"}),
    )

    orientation = forms.ChoiceField(
        label="Orientierung",
        choices=ORIENTATION_CHOICES,
        widget=forms.Select(),
    )

    tilt_deg = forms.FloatField(
        label="Neigung [°]",
        validators=[MinValueValidator(0.0), MaxValueValidator(90.0)],
        widget=forms.NumberInput(attrs={"min": "0", "max": "90", "step": "1", "required": True}),
    )

    area_m2 = forms.FloatField(
        label="PV-Fläche [m²]",
        validators=[MinValueValidator(0.0)],
        widget=forms.NumberInput(attrs={"min": "0", "step": "0.1", "required": True}),
    )

    eta = forms.FloatField(
        label="Gesamt-Wirkungsgrad η [0..1]",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        initial=0.14,
        widget=forms.NumberInput(attrs={"min": "0", "max": "1", "step": "0.001", "required": True}),
    )


PVSurfaceFormSet = formset_factory(PVSurfaceForm, extra=3, min_num=1, validate_min=True)

class PVCalcForm(PVMainForm):
    pass

