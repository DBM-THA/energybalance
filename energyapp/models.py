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
# GROUP 5: Lighting & Water
# ============================
class Energy(models.Model):
    building = models.ForeignKey(
        'Building', on_delete=models.CASCADE, related_name='energies'
    )
    room = models.CharField(max_length=100)
    area = models.FloatField("Fläche [m²]")
    esoll = models.FloatField("E_soll [lx]")
    volllast = models.FloatField("Vollast [h/Tag]")
    days = models.FloatField("Nutzungstage [d/a]")
    lm = models.FloatField("Lichtausbeute [lm/W]")

    # Automatisch berechnete Felder
    power = models.FloatField("Leistung [W]", null=True, blank=True)
    hours = models.FloatField("Betriebsstunden [h/a]", null=True, blank=True)
    energy_consumption = models.FloatField("Energiebedarf [kWh/a]", null=True, blank=True)

    def calculate(self):
        if self.lm and self.lm != 0:
            self.power = (self.area * self.esoll) / self.lm
        else:
            self.power = 0
        self.hours = self.volllast * self.days
        self.energy_consumption = self.power * self.hours / 1000
        self.save()
        return self.power, self.hours, self.energy_consumption

    def __str__(self):
        return f"{self.room} ({self.building.name})"


class Water(models.Model):
    building = models.ForeignKey(
        'Building', on_delete=models.CASCADE, related_name='waters'
    )
    room = models.CharField(max_length=100)
    area = models.FloatField("Fläche [m²]")
    persons = models.FloatField("Personen")
    dp = models.FloatField("Bedarf kWh/Pers·d")
    da = models.FloatField("Bedarf Wh/m²·d")

    # Berechnete Felder
    ep = models.FloatField("Personenbedarf [kWh/a]", null=True, blank=True)
    ea = models.FloatField("Flächenbedarf [kWh/a]", null=True, blank=True)
    em = models.FloatField("Mittelwert [kWh/a]", null=True, blank=True)

    def calculate(self):
        self.ep = self.dp * self.persons * 365
        self.ea = self.area * self.da * 365 / 1000
        self.em = (self.ep + self.ea) / 2
        self.save()
        return self.ep, self.ea, self.em

    def __str__(self):
        return f"{self.room} ({self.building.name})"

# ============================
# GROUP 6: PV
# ============================

# ============================
# GROUP 7: GWP
# ============================

# ============================
# GROUP 8: Load Profile
# ============================
