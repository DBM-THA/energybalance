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

    # Abgeleitete Bezugsfläche (Excel: NGF_t = BGF * 0,8)
    ngf_t = models.FloatField("NGF_t [m²]", null=True, blank=True)


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
# GROUP 1B: Sheet 01 – Ergebnis Energie (Overrides/Input)
# ============================
class Sheet01EnergyResult(models.Model):
    """
    Speichert NUR die editierbaren Felder aus dem Excel-Sheet
    '01 ERGEBNIS ENERGIE' (Faktoren, Anteile, Deckungsanteile, Kopftexte).
    Berechnete Werte werden NICHT gespeichert.
    """
    building = models.OneToOneField(
        Building,
        on_delete=models.CASCADE,
        related_name="sheet01",
    )

    # Kopf (Excel: '04 LASTGANG'!K12/K13)
    project = models.CharField(max_length=200, blank=True, default="")
    location = models.CharField(max_length=200, blank=True, default="")

    # Endenergie Wärme – Verlustfaktoren (Excel: 0,05 / 0,05 / 0,05 + Solar frei)
    factor_transfer_hw = models.FloatField(default=0.05)      # Übergabe Heiz/Wasser
    factor_distribution_hw = models.FloatField(default=0.05)  # Verteilung Heiz/Wasser
    factor_storage_hw = models.FloatField(default=0.05)       # Speicherung Heiz/Wasser
    factor_solar_generation = models.FloatField(default=0.0)  # "- Erzeugung Solar"

    # Erzeuger-Anteile Wärme (Excel: C46/C47/C48)
    share_wp = models.FloatField(default=1.0)
    share_fw = models.FloatField(default=0.0)
    share_gas = models.FloatField(default=0.0)

    # Endenergie Faktoren (Excel: FW 0,4 / Gas 1,1 / Hilfsenergie 0,03)
    factor_fw_heat = models.FloatField(default=0.4)
    factor_gas_heat = models.FloatField(default=1.1)
    factor_aux_heat = models.FloatField(default=0.03)

    # Primärenergie Faktoren (Excel: FW 0,25 / Gas 1,1 / On-Site -1,8 / Off-Site 1,8)
    pe_factor_fw = models.FloatField(default=0.25)
    pe_factor_gas = models.FloatField(default=1.1)
    pe_factor_on_site = models.FloatField(default=-1.8)
    pe_factor_off_site = models.FloatField(default=1.8)

    # Deckungsanteil PV Eigennutzung (Excel: I78 = 0,7)
    pv_self_use_share = models.FloatField(default=0.7)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sheet01EnergyResult for {self.building.name}"
# ============================
# SHEET 01: Ergebnis Energie (Inputs + Kommentare)
# ============================
class EnergyResultSheet01(models.Model):
    building = models.OneToOneField(
        Building,
        on_delete=models.CASCADE,
        related_name="sheet01_energy",
    )

    # Kopfbereich
    project = models.CharField(max_length=200, blank=True, default="")
    location = models.CharField(max_length=200, blank=True, default="")

    # Eingaben wie Excel (E-Spalte in deinem Sheet)
    # Excel-Eingabe: E39
    E39_transfer_heat_water = models.FloatField(default=0.05)

    # Excel-Eingabe: E40
    E40_distribution_heat_water = models.FloatField(default=0.05)

    # Excel-Eingabe: E41
    E41_storage_heat_water = models.FloatField(default=0.05)

    # Excel-Eingabe: E42 (freie Eingabe)
    E42_solar_generation_factor = models.FloatField(default=0.0)

    # Excel-Eingabe: E47
    E47_factor_fw = models.FloatField(default=0.4)

    # Excel-Eingabe: E48
    E48_factor_gas = models.FloatField(default=1.1)

    # Excel-Eingabe: E49
    E49_aux_heating = models.FloatField(default=0.03)

    # Excel-Eingabe: E51
    E51_air_support = models.FloatField(default=1.0)

    # Excel-Eingabe: E52
    E52_lighting = models.FloatField(default=1.0)

    # Excel-Eingabe: E53
    E53_user_process = models.FloatField(default=1.0)

    # Primärenergie Deckungsanteil On-Site (I78)
    # Excel-Eingabe: I78 (in Excel: 0,7)
    I78_pv_self_share = models.FloatField(default=0.7)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sheet01 – {self.building.name}"

# ============================
# GROUP 2: Envelope Components
# ============================
from django.db import models

class EnvelopeElement(models.Model):
    FLOW_UP = "up"
    FLOW_HORIZONTAL = "horizontal"
    FLOW_DOWN = "down"

    FLOW_CHOICES = [
        (FLOW_UP, "Aufwärts"),
        (FLOW_HORIZONTAL, "Horizontal"),
        (FLOW_DOWN, "Abwärts"),
    ]

    building = models.ForeignKey(
        "Building",
        on_delete=models.CASCADE,
        related_name="envelope_elements",
        null=True,
        blank=True,
    )


    name = models.CharField(max_length=200)

    # Wichtig: Richtung des Wärmestroms als Feld speichern
    heat_flow = models.CharField(
        max_length=20,
        choices=FLOW_CHOICES,
        default=FLOW_HORIZONTAL,
    )

    use_custom_layers = models.BooleanField(
        default=True,
        help_text="Falls deaktiviert, wird ein vorgegebener U-Wert genutzt."
    )

    u_value_external = models.FloatField(
        null=True,
        blank=True,
        help_text="Falls vorhanden, extern vorgegebener U-Wert"
    )

    u_value_calculated = models.FloatField(
        null=True,
        blank=True
    )

    @property
    def rsi(self) -> float:
        # Tabelle: Rsi abhängig von Wärmeflussrichtung
        return {
            self.FLOW_UP: 0.10,
            self.FLOW_HORIZONTAL: 0.13,
            self.FLOW_DOWN: 0.17,
        }.get(self.heat_flow, 0.13)

    @property
    def rse(self) -> float:
        # Tabelle: Rse immer 0.04
        return 0.04

    @property
    def r_fixed(self) -> float:
        return float(self.rsi + self.rse)

    def calculate_u_value(self, R_fixed=0.17):
        """
        U = 1 / (Summe(R_schichten) + Rsi+Rse)
        R_fixed wird aus der View übergeben:
          - Dach: 0.10 + 0.04 = 0.14
          - Wand/Fenster: 0.13 + 0.04 = 0.17
          - Kellerdecke: 0.17 + 0.04 = 0.21
        """

        # Fall: externer U-Wert
        if not self.use_custom_layers:
            self.u_value_calculated = self.u_value_external
            self.save(update_fields=["u_value_calculated"])
            return self.u_value_calculated

        layers = self.layers.all()
        if not layers.exists():
            self.u_value_calculated = None
            self.save(update_fields=["u_value_calculated"])
            return None

        sum_R_layers = 0.0
        for layer in layers:
            if layer.R_value is not None and layer.R_value > 0:
                sum_R_layers += float(layer.R_value)

        total_R = sum_R_layers + float(R_fixed)
        self.u_value_calculated = (1 / total_R) if total_R > 0 else None
        self.save(update_fields=["u_value_calculated"])
        return self.u_value_calculated

    def __str__(self):
        return self.name


class Layer(models.Model):
    TYPE_CHOICES = [
        ("inside", "Innen (R manuell)"),
        ("layer", "Materialschicht (d & λ)"),
        ("outside", "Außen (R manuell)"),
    ]

    element = models.ForeignKey(
        EnvelopeElement,
        on_delete=models.CASCADE,
        related_name="layers"
    )

    layer_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    name = models.CharField(max_length=200)

    thickness = models.FloatField(
        null=True,
        blank=True,
        help_text="d in m (z.B. 0.24 für 24 cm)"
    )

    lambda_value = models.FloatField(
        null=True,
        blank=True,
        help_text="λ in W/mK"
    )

    R_value = models.FloatField(
        null=True,
        blank=True,
        help_text="Widerstand R in m²K/W"
    )

    def save(self, *args, **kwargs):
        # Automatische Berechnung nur für Materialschichten
        if self.layer_type == "layer":
            if (
                self.thickness is not None
                and self.lambda_value is not None
                and self.lambda_value > 0
            ):
                self.R_value = float(self.thickness) / float(self.lambda_value)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.layer_type})"



# ============================
# GROUP 3: Internal Gains
# ============================
class InternalGains(models.Model):
    dummy = models.CharField(max_length=100)

# ============================
# GROUP 4: Ventilation
# ============================

# ----------------------------
# 4A: Nutzungskategorien (Stammdaten)
# ----------------------------
class VentilationUsageCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    std_persons = models.FloatField("Standard Personen", default=0)
    std_air_change = models.FloatField("Standard Luftwechsel [1/h]", default=0)
    std_hours_per_day = models.FloatField("Standard h/Tag", default=0)
    std_days_per_year = models.FloatField("Standard Tage/Jahr", default=0)

    def __str__(self):
        return self.name


# ----------------------------
# 4B: Lüftungs-Szenario (Kopfbereich)
# ----------------------------
class VentilationScenario(models.Model):
    building = models.OneToOneField(
        'Building',
        on_delete=models.CASCADE,
        related_name="ventilation",
    )

    total_area = models.FloatField("Gesamtfläche [m²]")
    electricity_price = models.FloatField("Strompreis [€/kWh]", default=0.40)

    # optionale Ergebnis-Speicherung
    result_volume_flow = models.FloatField(null=True, blank=True)  # m³/h
    result_power_kw = models.FloatField(null=True, blank=True)     # kW
    result_energy_kwh = models.FloatField(null=True, blank=True)   # kWh/a
    result_costs_eur = models.FloatField(null=True, blank=True)    # €/a

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lüftung – {self.building.name}"


# ----------------------------
# 4C: Einzelne Nutzungslinien (UI-Zeilen)
# ----------------------------
class VentilationUsageShare(models.Model):
    scenario = models.ForeignKey(
        VentilationScenario,
        on_delete=models.CASCADE,
        related_name="usages",
    )

    category = models.ForeignKey(
        VentilationUsageCategory,
        on_delete=models.PROTECT,
        related_name="usage_shares",
    )

    share_percent = models.FloatField("Anteil [%]")
    persons = models.FloatField("Personen")
    air_change_rate = models.FloatField("Luftwechsel [1/h]")
    hours_per_day = models.FloatField("Betriebsstunden [h/Tag]")
    days_per_year = models.FloatField("Betriebstage [d/a]")

    # optionale Ergebniswerte pro Nutzung
    result_volume_flow = models.FloatField(null=True, blank=True)  # m³/h
    result_power_kw = models.FloatField(null=True, blank=True)
    result_energy_kwh = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.category.name} – {self.share_percent}%"



# ============================
# GROUP 5: Lighting & Water
# ============================
class Lighting(models.Model):
    dummy = models.CharField(max_length=100)

class Water(models.Model):
    dummy = models.CharField(max_length=100)

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
from django.db import models
# Übergangsklasse wird mit buildíngclass verknüpft

class EnergyProject(models.Model):
    name = models.CharField(max_length=200, default="Machbarkeitsstudie")
    standort = models.CharField(max_length=100, default="Würzburg")

    # Geometrie & Allgemeine Daten (aus Blatt 04)
    bgf = models.FloatField(verbose_name="BGF R", help_text="m²")
    bri = models.FloatField(verbose_name="BRI", help_text="m³")
    ngf = models.FloatField(verbose_name="Nutzfläche (NGF)", help_text="m²")

    # Lüftung (aus Blatt 04)
    luftwechselrate = models.FloatField(default=0.49, help_text="1/h")
    wrg_wirkungsgrad = models.FloatField(default=0.75, verbose_name="Wirkungsgrad WRG")
    luftvolumenstrom = models.FloatField(help_text="m³/h", blank=True, null=True)

    # Klimadaten & Physik (aus Blatt 03)
    raum_soll_temp = models.FloatField(default=20.0, verbose_name="Raum-Soll-Temperatur")
    c_wirk_pauschal = models.FloatField(default=50, verbose_name="Speicherfähigkeit Wh/m²K")

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatische Berechnung Volumenstrom falls leer
        if not self.luftvolumenstrom:
            # Vereinfachte Annahme analog Excel
            self.luftvolumenstrom = self.bri * 0.8 * self.luftwechselrate  # V_netto * n
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BuildingComponent(models.Model):
    ORIENTATION_CHOICES = [
        ('N', 'Nord'),
        ('O', 'Ost'),
        ('S', 'Süd'),
        ('W', 'West'),
        ('H', 'Horizontal/Dach'),
        ('X', 'Keine/Erde'),
    ]

    project = models.ForeignKey(EnergyProject, on_delete=models.CASCADE, related_name='components')
    name = models.CharField(max_length=100)  # z.B. "Massive Außenwand Süd"
    area = models.FloatField(verbose_name="Fläche m²")
    u_value = models.FloatField(verbose_name="U-Wert W/m²K")
    fx_factor = models.FloatField(default=1.0, verbose_name="Temperaturkorrekturfaktor Fx")
    orientation = models.CharField(max_length=1, choices=ORIENTATION_CHOICES, default='X')
    g_value = models.FloatField(default=0.0, verbose_name="g-Wert (nur Fenster)", blank=True)

    def ht_value(self):
        return self.area * self.u_value * self.fx_factor
# ============================
# ============================

# ============================
# GROUP 10: Summer Protection (Sommerlicher Wärmeschutz)
# ============================
class SummerProtection(models.Model):
    name = models.CharField(
        max_length=100,
        default="Sommerlicher Wärmeschutz",
        help_text="Name des Szenarios (z.B. 'Standard Sommerfall').",
    )

    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="summer_protections",
    )

    # ----------------------------
    # Critical room (Excel Schritt 1 & 2)
    # ----------------------------
    ORIENTATION_CHOICES = [
        ("N", "Nord"),
        ("E", "Ost"),
        ("S", "Süd"),
        ("W", "West"),
    ]
    orientation = models.CharField(
        "Fassadenorientierung (kritischer Raum)",
        max_length=1,
        choices=ORIENTATION_CHOICES,
        default="S",
    )

    ngf_m2 = models.FloatField(
        "Nettogrundfläche Raum (NGF) [m²]",
        default=30.0,
    )

    window_area_m2 = models.FloatField(
        "Fensterfläche (kritischer Raum) [m²]",
        default=0.0,
    )

    # ----------------------------
    # Fixed categories for Fc lookup (your table)
    # ----------------------------
    GLAZING_CATEGORY_CHOICES = [
        ("double", "zweifach"),
        ("triple", "dreifach"),
        ("solar", "Sonnenschutzglas (g ≤ 0.40)"),
    ]
    glazing_category = models.CharField(
        "Verglasungskategorie",
        max_length=20,
        choices=GLAZING_CATEGORY_CHOICES,
        default="double",
    )

    SHADING_TYPE_CHOICES = [
        ("none", "ohne Sonnenschutz"),                      # Zeile 1
        ("internal", "innenliegend / zwischen Scheiben"),   # Zeile 2
        ("roller_closed", "Rollladen geschlossen"),         # 3.1
        ("jalousie_45", "Jalousie 45°"),                    # 3.2.1
        ("awning", "Markise"),                              # 3.3
        ("overhang", "Vordach / Überhang"),                 # 3.4
    ]
    shading_type = models.CharField(
        "Sonnenschutztyp (kritischer Raum)",
        max_length=30,
        choices=SHADING_TYPE_CHOICES,
        default="none",
    )

    # ----------------------------
    # Step 3 inputs (Excel)
    # ----------------------------
    CLIMATE_REGION_CHOICES = [
        ("A", "Klimaregion A"),
        ("B", "Klimaregion B"),
        ("C", "Klimaregion C"),
    ]
    climate_region = models.CharField(
        "Klimaregion",
        max_length=1,
        choices=CLIMATE_REGION_CHOICES,
        default="B",
    )

    NIGHT_VENT_CHOICES = [
        ("none", "keine"),
        ("slight", "erhöht leicht"),
        ("strong", "erhöht stark"),
    ]
    night_ventilation = models.CharField(
        "Nachtlüftung",
        max_length=10,
        choices=NIGHT_VENT_CHOICES,
        default="none",
    )

    passive_cooling = models.BooleanField(
        "Passive Kühlung vorhanden",
        default=False,
    )

    def __str__(self):
        return f"{self.name} ({self.orientation}) – {self.building.name}"
