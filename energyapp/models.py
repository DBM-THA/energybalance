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
class InternalGains(models.Model):
    dummy = models.CharField(max_length=100)

# ============================
# GROUP 4: Ventilation
# ============================
class Ventilation(models.Model):
    dummy = models.CharField(max_length=100)


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
class GwpManufacturing(models.Model):
    building = models.OneToOneField(
        Building,
        on_delete=models.CASCADE,
        related_name="gwp_manufacturing",
    )


    # USER INPUT (Excel 06, Spalte G)
    new_components_gwp = models.FloatField("Herstellung neue Bauteile [kg]", default=0)
    existing_components_gwp = models.FloatField("Herstellung Bestandsbauteile [kg]", default=0)
    service_life_years = models.FloatField("Nutzungsdauer [a]", default=50)

    # BERECHNET (nicht speichern!)
    @property
    def new_per_year(self):
        return self.new_components_gwp / self.service_life_years if self.service_life_years else 0

    @property
    def existing_per_year(self):
        return self.existing_components_gwp / self.service_life_years if self.service_life_years else 0

# ============================
# GROUP 7: GWP - Kompensation
# ============================
class GwpCompensation(models.Model):
    building = models.OneToOneField(
        Building,
        on_delete=models.CASCADE,
        related_name="gwp_compensation",
    )
    manufacturing = models.OneToOneField(
        GwpManufacturing,
        on_delete=models.CASCADE,
        related_name="compensation",
    )


    # USER INPUT (Excel 07, Spalte G) – Endenergie [kWh/a]
    heat_district_regen_kwh = models.FloatField("Fernwärme regenerativ [kWh/a]", default=0)
    heat_district_avg_kwh   = models.FloatField("Fernwärme durchschnitt [kWh/a]", default=0)
    gas_kwh                 = models.FloatField("Gas [kWh/a]", default=0)
    electricity_kwh         = models.FloatField("Strom [kWh/a]", default=0)

    # Faktoren (nicht in DB speichern – NICHT user input)
    FACTOR_HEAT = 0.28
    FACTOR_GAS = 0.201
    FACTOR_ELECTRICITY = 0.3538

    # --- Nutzungs-Emissionen (wie Excel 07 Schritt 1) ---
    @property
    def gwp_heat_district_regen(self):
        return self.heat_district_regen_kwh * self.FACTOR_HEAT

    @property
    def gwp_heat_district_avg(self):
        return self.heat_district_avg_kwh * self.FACTOR_HEAT

    @property
    def gwp_gas(self):
        return self.gas_kwh * self.FACTOR_GAS

    @property
    def gwp_electricity(self):
        return self.electricity_kwh * self.FACTOR_ELECTRICITY

    # --- Summen (wie Excel 07 "Summe ohne/mit Bestandsbauteilen") ---
    @property
    def sum_without_existing(self):
        return (
            self.gwp_heat_district_regen
            + self.gwp_heat_district_avg
            + self.gwp_gas
            + self.gwp_electricity
            + self.manufacturing.new_per_year
        )

    @property
    def sum_with_existing(self):
        return self.sum_without_existing + self.manufacturing.existing_per_year

# ============================
# GROUP 8: Load Profile
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
