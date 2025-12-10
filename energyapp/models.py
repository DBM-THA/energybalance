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
class GwpManufacturing(models.Model):
    building = models.OneToOneField(
        Building,
        on_delete=models.CASCADE,
        related_name="gwp_manufacturing",
    )

    # GWP Herstellung gesamt [kg CO2] – aus Excel 06
    kg300_new_gwp_total = models.FloatField("KG300 neu: GWP gesamt [kg]", default=0)
    kg300_existing_gwp_total = models.FloatField("KG300 Bestand: GWP gesamt [kg]", default=0)
    kg400_new_gwp_total = models.FloatField("KG400 neu: GWP gesamt [kg]", default=0)
    kg400_existing_gwp_total = models.FloatField("KG400 Bestand: GWP gesamt [kg]", default=0)

    # Nutzungsdauern [a]
    kg300_new_service_life = models.FloatField("KG300 neu: Nutzungsdauer [a]", default=50)
    kg300_existing_service_life = models.FloatField("KG300 Bestand: Nutzungsdauer [a]", default=30)
    kg400_new_service_life = models.FloatField("KG400 neu: Nutzungsdauer [a]", default=25)
    kg400_existing_service_life = models.FloatField("KG400 Bestand: Nutzungsdauer [a]", default=20)

    # abgeleitete Werte (nicht speichern, nur @property)
    @property
    def grey_new_kg300_per_year(self):
        return self.kg300_new_gwp_total / self.kg300_new_service_life if self.kg300_new_service_life else 0

    @property
    def grey_existing_kg300_per_year(self):
        return self.kg300_existing_gwp_total / self.kg300_existing_service_life if self.kg300_existing_service_life else 0

    @property
    def grey_new_kg400_per_year(self):
        return self.kg400_new_gwp_total / self.kg400_new_service_life if self.kg400_new_service_life else 0

    @property
    def grey_existing_kg400_per_year(self):
        return self.kg400_existing_gwp_total / self.kg400_existing_service_life if self.kg400_existing_service_life else 0

    @property
    def manufacturing_total_without_existing(self):
        return self.kg300_new_gwp_total + self.kg400_new_gwp_total

    @property
    def manufacturing_total_with_existing(self):
        return (
            self.kg300_new_gwp_total
            + self.kg400_new_gwp_total
            + self.kg300_existing_gwp_total
            + self.kg400_existing_gwp_total
        )

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

    # Endenergie [kWh/a]
    heat_district_kwh = models.FloatField("Fernwärme [kWh/a]", default=0)
    gas_kwh = models.FloatField("Gas [kWh/a]", default=0)
    electricity_kwh = models.FloatField("Strom [kWh/a]", default=0)

    # Emissionsfaktoren [kg/kWh]
    factor_heat = models.FloatField("Faktor Fernwärme [kg/kWh]", default=0.28)
    factor_gas = models.FloatField("Faktor Gas [kg/kWh]", default=0.201)
    factor_electricity = models.FloatField("Faktor Strom [kg/kWh]", default=0.3538)

    # PV
    pv_yield_kwh = models.FloatField("PV-Ertrag [kWh/a]", default=0)
    pv_factor = models.FloatField("PV-Faktor [kg/kWh]", default=-0.3538)

    # Nutzungs-Emissionen
    @property
    def gwp_heat_district(self):
        return self.heat_district_kwh * self.factor_heat

    @property
    def gwp_gas(self):
        return self.gas_kwh * self.factor_gas

    @property
    def gwp_electricity(self):
        return self.electricity_kwh * self.factor_electricity

    @property
    def gwp_pv(self):
        return self.pv_yield_kwh * self.pv_factor   # i.d.R. negativ

    # Summen wie in Excel 07
    @property
    def sum_without_existing(self):
        return (
            self.gwp_heat_district
            + self.gwp_gas
            + self.gwp_electricity
            + self.manufacturing.grey_new_kg300_per_year
            + self.manufacturing.grey_new_kg400_per_year
        )

    @property
    def sum_with_existing(self):
        return (
            self.sum_without_existing
            + self.manufacturing.grey_existing_kg300_per_year
            + self.manufacturing.grey_existing_kg400_per_year
        )

    @property
    def operation_balance(self):
        # Bilanz Betrieb: nur Nutzung + PV
        return (
            self.gwp_heat_district
            + self.gwp_gas
            + self.gwp_electricity
            + self.gwp_pv
        )

    @property
    def years_to_compensation_without_existing(self):
        if self.operation_balance >= 0:
            return None
        return self.manufacturing.manufacturing_total_without_existing / abs(self.operation_balance)

    @property
    def years_to_compensation_with_existing(self):
        if self.operation_balance >= 0:
            return None
        return self.manufacturing.manufacturing_total_with_existing / abs(self.operation_balance)

# ============================
# GROUP 8: Load Profile
# ============================