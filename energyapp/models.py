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
# GROUP 6: PV
# ============================

# ============================
# GROUP 7: GWP
# ============================

# ============================
# GROUP 8: Load Profile
# ============================

# ============================
# GROUP 10: Sommerlicher Wärmeschutz
# ============================

class SummerProtection(models.Model):

    name = models.CharField(
        max_length=200,
        help_text="Name des Szenarios (z.B. 'Standard Sommerfall')."
    )

    # Geometrie
    floor_area = models.FloatField(
        default=1.0,
        help_text="Grundfläche des Raums / der Zone in m²."
    )
    window_area_north = models.FloatField(
        default=0.0,
        help_text="Fensterfläche Nord in m²."
    )
    window_area_south = models.FloatField(
        default=0.0,
        help_text="Fensterfläche Süd in m²."
    )
    window_area_east = models.FloatField(
        default=0.0,
        help_text="Fensterfläche Ost in m²."
    )
    window_area_west = models.FloatField(
        default=0.0,
        help_text="Fensterfläche West in m²."
    )

    # Optische Eigenschaften
    g_value = models.FloatField(
        default=0.6,
        help_text="Gesamtenergiedurchlassgrad g der Verglasung (-)."
    )
    shading_factor = models.FloatField(
        default=1.0,
        help_text="Verschattungsfaktor Fc (0–1, 1 = kein Sonnenschutz)."
    )

    # Innere Lasten (vereinfachte spezifische Last)
    internal_gains_density = models.FloatField(
        default=5.0,
        help_text="Innere Lasten q_int in W/m² (Personen, Geräte etc.)."
    )

    # Klima (Infofelder)
    outdoor_temp_peak = models.FloatField(
        default=30.0,
        help_text="Sommerliche Außentemperatur-Spitze in °C (nur Info)."
    )
    set_temp = models.FloatField(
        default=26.0,
        help_text="Gewünschte Raumtemperatur in °C (nur Info)."
    )

    # Ergebnisse
    auto_indicator = models.FloatField(
        default=0.0,
        help_text="Automatisch berechneter Kennwert in W/m²."
    )
    override_indicator = models.FloatField(
        null=True,
        blank=True,
        help_text="Optionaler Override-Wert in W/m²."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ---- Logik-Helfer ----

    def calculate_auto_indicator(self, I_summer: float = 500.0) -> float:
        """
        Berechnet den vereinfachten Überhitzungskennwert in W/m².

        Formel:
            A_win   = Summe Fensterflächen
            Q_S     = A_win * g * Fc * I_summer
            Q_I     = q_int * A_floor
            Kennwert = (Q_S + Q_I) / A_floor
        """
        a_win = (
            self.window_area_north
            + self.window_area_south
            + self.window_area_east
            + self.window_area_west
        )

        # Solare Gewinne (W)
        Q_s = a_win * self.g_value * self.shading_factor * I_summer

        # Innere Gewinne (W)
        Q_i = self.internal_gains_density * self.floor_area

        if self.floor_area > 0:
            indicator = (Q_s + Q_i) / self.floor_area
        else:
            indicator = 0.0

        self.auto_indicator = indicator
        self.save()
        return indicator

    @property
    def effective_indicator(self) -> float:
        """
        Wert, der für andere Module benutzt werden soll:
        Override, falls gesetzt, sonst auto_indicator.
        """
        if self.override_indicator is not None:
            return self.override_indicator
        return self.auto_indicator

    @property
    def rating(self) -> str:
        """
        Einfache verbale Einstufung des Kennwertes.
        """
        value = self.effective_indicator
        if value < 10:
            return "geringes Überhitzungsrisiko"
        elif value < 20:
            return "mittleres Überhitzungsrisiko"
        return "hohes Überhitzungsrisiko"

    def __str__(self):
        return f"Sommerlicher Wärmeschutz: {self.name}"
