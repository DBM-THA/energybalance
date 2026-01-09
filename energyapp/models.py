from django.db import models

# ============================
# GROUP 1: Building Data
# ============================
class Building(models.Model):
    name = models.CharField(max_length=100)

    # Geometrie
    length_ns = models.FloatField("Länge Nord/Süd [m]")
    width_ow = models.FloatField("Breite Ost/West [m]")
    storeys = models.IntegerField("Geschosse")
    room_height = models.FloatField("Raumhöhe [m]")

    # U-Werte
    u_wall = models.FloatField("U-Wert Außenwand [W/m²K]")
    u_roof = models.FloatField("U-Wert Dach [W/m²K]")
    u_floor = models.FloatField("U-Wert Kellerdecke [W/m²K]")
    u_window = models.FloatField("U-Wert Fenster [W/m²K]")

    # Fensteranteile je Fassade (in % der Fassadenfläche)
    window_share_n = models.FloatField("Fensteranteil Nord [%]", default=50)
    window_share_e = models.FloatField("Fensteranteil Ost [%]", default=50)
    window_share_s = models.FloatField("Fensteranteil Süd [%]", default=50)
    window_share_w = models.FloatField("Fensteranteil West [%]", default=50)

    # Solare Gewinne – g-Werte je Orientierung
    g_n = models.FloatField("g-Wert Nord", default=0.6)
    g_e = models.FloatField("g-Wert Ost", default=0.6)
    g_s = models.FloatField("g-Wert Süd", default=0.6)
    g_w = models.FloatField("g-Wert West", default=0.6)

    # Innere Gewinne
    person_density = models.FloatField("Personendichte [m²/Person]", default=20)
    persons = models.IntegerField("Personen", default=24)

    # Lüftung
    air_change_rate = models.FloatField(
        "Luftwechselrate n [1/h]", default=0.5
    )

    # Klimadaten (vereinfacht)
    degree_days = models.FloatField(
        "Heizgradtage HDD [K*d]", default=3000
    )

    # PV-Eingabedaten
    pv_roof_share = models.FloatField(
        "PV-Anteil Dachfläche [%]", default=50
    )
    pv_specific_yield = models.FloatField(
        "PV-spezifischer Ertrag [kWh/m²*a]", default=180
    )
    pv_self_consumption_share = models.FloatField(
        "PV-Eigenverbrauchsanteil [%]", default=70
    )

    # Komfort
    setpoint_temp = models.FloatField("Solltemperatur [°C]")

    # --- Berechnungsergebnisse (werden automatisch gefüllt) ---
    result_Q_T = models.FloatField(null=True, blank=True)
    result_Q_V = models.FloatField(null=True, blank=True)
    result_Q_I = models.FloatField(null=True, blank=True)
    result_Q_S = models.FloatField(null=True, blank=True)
    result_Q_h = models.FloatField(null=True, blank=True)

    result_H_T = models.FloatField(null=True, blank=True)
    result_H_V = models.FloatField(null=True, blank=True)

    result_floor_area = models.FloatField(null=True, blank=True)
    result_roof_area = models.FloatField(null=True, blank=True)
    result_opaque_wall_area = models.FloatField(null=True, blank=True)
    result_window_area = models.FloatField(null=True, blank=True)

    result_Q_S_n = models.FloatField(null=True, blank=True)
    result_Q_S_e = models.FloatField(null=True, blank=True)
    result_Q_S_s = models.FloatField(null=True, blank=True)
    result_Q_S_w = models.FloatField(null=True, blank=True)

    result_Q_PV_total = models.FloatField(null=True, blank=True)
    result_Q_PV_on = models.FloatField(null=True, blank=True)
    result_Q_PV_off = models.FloatField(null=True, blank=True)


    def __str__(self):
        return self.name


# ============================
# GROUP 2: Envelope Components
# ============================
class EnvelopeElement(models.Model):
    """
    Bauteil (Wand, Dach, Boden etc.)
    Kann entweder
      - einen extern gegebenen U-Wert haben ODER
      - über Schichten selbst berechnet werden
    """
    name = models.CharField(max_length=200)
    use_custom_layers = models.BooleanField(
        default=True,
        help_text="Falls deaktiviert, wird ein vorgegebener U-Wert genutzt."
    )
    u_value_external = models.FloatField(
        null=True, blank=True,
        help_text="Falls vorhanden, extern vorgegebener U-Wert"
    )
    u_value_calculated = models.FloatField(null=True, blank=True)

    def calculate_u_value(self):
        """Berechnet U = 1 / Summe(R) falls Schichten benutzt werden."""
        if not self.use_custom_layers:
            self.u_value_calculated = self.u_value_external
            self.save()
            return self.u_value_calculated

        layers = self.layers.all()
        if not layers:
            return None

        total_R = sum([layer.R_value for layer in layers])
        if total_R > 0:
            self.u_value_calculated = 1 / total_R
        else:
            self.u_value_calculated = None

        self.save()
        return self.u_value_calculated

    def __str__(self):
        return self.name


class Layer(models.Model):
    """
    Eine einzelne Schicht eines Bauteils
    Arten:
        - inside : innere Schicht (nur R)
        - layer  : normale Schicht (d & lambda → R)
        - outside: äußere Schicht (nur R)
    """
    TYPE_CHOICES = [
        ("inside", "Innen"),
        ("layer", "Materialschicht"),
        ("outside", "Außen"),
    ]

    element = models.ForeignKey(
        EnvelopeElement,
        on_delete=models.CASCADE,
        related_name="layers"
    )
    layer_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=200)
    thickness = models.FloatField(null=True, blank=True, help_text="d in m")
    lambda_value = models.FloatField(null=True, blank=True, help_text="λ in W/mK")
    R_value = models.FloatField(null=True, blank=True, help_text="Widerstand R")

    def save(self, *args, **kwargs):
        # R = d / λ nur für normale Schichten
        if self.layer_type == "layer":
            if self.thickness and self.lambda_value:
                self.R_value = self.thickness / self.lambda_value

        # innere/äußere Schichten: R wird extern eingegeben
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.layer_type})"

# ============================
# GROUP 3: Internal Gains
# ============================

# ============================
# GROUP 4: Ventilation
# ============================

# ============================
# GROUP 5: Lighting & Water
# ============================

# ============================
# GROUP 6: GWP - Herstellung
# ============================
from django.db import models
from django.core.validators import MinValueValidator


class GwpManufacturing(models.Model):
    building = models.OneToOneField(
        "Building",
        on_delete=models.CASCADE,
        related_name="gwp_manufacturing",
    )

    # USER INPUT (getrennt nach Kostengruppe)
    kg300_new = models.FloatField("KG300 neue Bauteile [kg]", default=0, validators=[MinValueValidator(0)])
    kg400_new = models.FloatField("KG400 neue Bauteile [kg]", default=0, validators=[MinValueValidator(0)])

    kg300_existing = models.FloatField("KG300 Bestandsbauteile [kg]", default=0, validators=[MinValueValidator(0)])
    kg400_existing = models.FloatField("KG400 Bestandsbauteile [kg]", default=0, validators=[MinValueValidator(0)])

    service_life_years = models.FloatField("Nutzungsdauer [a]", default=50, validators=[MinValueValidator(1)])

    # BERECHNET (nicht speichern)
    @property
    def new_components_gwp(self):
        return (self.kg300_new or 0) + (self.kg400_new or 0)

    @property
    def existing_components_gwp(self):
        return (self.kg300_existing or 0) + (self.kg400_existing or 0)

    @property
    def total_gwp(self):
        return self.new_components_gwp + self.existing_components_gwp

    @property
    def new_per_year(self):
        return self.new_components_gwp / self.service_life_years if self.service_life_years else 0

    @property
    def existing_per_year(self):
        return self.existing_components_gwp / self.service_life_years if self.service_life_years else 0

    @property
    def total_per_year(self):
        return self.total_gwp / self.service_life_years if self.service_life_years else 0

    def __str__(self):
        return f"GWP Herstellung ({self.building})"



# ============================
# GROUP 7: GWP - Kompensation
# ============================
from django.db import models
from django.core.validators import MinValueValidator


class GwpCompensation(models.Model):
    building = models.OneToOneField(
        "Building",
        on_delete=models.CASCADE,
        related_name="gwp_compensation",
    )

    # =========================
    # USER INPUT (Excel 07) – Endenergie [kWh/a]
    # =========================
    heat_district_regen_kwh = models.FloatField(
        "Fernwärme regenerativ [kWh/a]",
        default=0,
        validators=[MinValueValidator(0)],
    )
    heat_district_avg_kwh = models.FloatField(
        "Fernwärme durchschnitt [kWh/a]",
        default=0,
        validators=[MinValueValidator(0)],
    )
    gas_kwh = models.FloatField(
        "Gas [kWh/a]",
        default=0,
        validators=[MinValueValidator(0)],
    )
    electricity_kwh = models.FloatField(
        "Strom [kWh/a]",
        default=0,
        validators=[MinValueValidator(0)],
    )

    # =========================
    # CO2-FAKTOREN (kg/kWh)
    # =========================
    factor_heat_regen = models.FloatField(
        "CO₂-Faktor Fernwärme regenerativ [kg/kWh]",
        default=0.0,
        validators=[MinValueValidator(0)],
    )
    factor_heat_avg = models.FloatField(
        "CO₂-Faktor Fernwärme durchschnitt [kg/kWh]",
        default=0.28,
        validators=[MinValueValidator(0)],
    )
    factor_gas = models.FloatField(
        "CO₂-Faktor Gas [kg/kWh]",
        default=0.201,
        validators=[MinValueValidator(0)],
    )
    factor_electricity = models.FloatField(
        "CO₂-Faktor Strom [kg/kWh]",
        default=0.3538,
        validators=[MinValueValidator(0)],
    )

    # =========================
    # HELPERS
    # =========================
    @property
    def manufacturing(self):
        """
        Holt Manufacturing über das Building (OneToOne: building.gwp_manufacturing).
        Gibt None zurück, wenn noch keine Manufacturing-Daten existieren.
        """
        return getattr(self.building, "gwp_manufacturing", None)

    # =========================
    # BERECHNUNGEN (Excel 07 Schritt 1)
    # =========================
    @property
    def gwp_heat_district_regen(self):
        return self.heat_district_regen_kwh * self.factor_heat_regen

    @property
    def gwp_heat_district_avg(self):
        return self.heat_district_avg_kwh * self.factor_heat_avg

    @property
    def gwp_gas(self):
        return self.gas_kwh * self.factor_gas

    @property
    def gwp_electricity(self):
        return self.electricity_kwh * self.factor_electricity

    @property
    def operation_total_per_year(self):
        """Summe Nutzung (ohne Herstellung) pro Jahr"""
        return (
            self.gwp_heat_district_regen
            + self.gwp_heat_district_avg
            + self.gwp_gas
            + self.gwp_electricity
        )

    # =========================
    # SUMMEN WIE IM EXCEL (ohne/mit Bestandsbauteilen)
    # =========================
    @property
    def sum_without_existing(self):
        """
        Nutzung + Herstellung neu pro Jahr
        (Excel: Summe ohne Bestandsbauteile)
        """
        m = self.manufacturing
        new_per_year = m.new_per_year if m else 0
        return self.operation_total_per_year + new_per_year

    @property
    def sum_with_existing(self):
        """
        Nutzung + Herstellung neu + Herstellung Bestand pro Jahr
        (Excel: Summe mit Bestandsbauteilen)
        """
        m = self.manufacturing
        existing_per_year = m.existing_per_year if m else 0
        return self.sum_without_existing + existing_per_year

    def __str__(self):
        return f"GwpCompensation(Building={self.building_id})"

# ============================
# GROUP 8: Load Profile
# ============================
