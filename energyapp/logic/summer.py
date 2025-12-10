from energyapp.models import SummerProtection

# Vereinfachte konstante Strahlungsstärke im Sommer [W/m²]
SUMMER_SOLAR_INTENSITY = 500.0


def calc_summer_overheating(sp: SummerProtection) -> dict:
    """
    Calculate a simple summer overheating indicator in W/m²
    plus some intermediate values.

    Formula (very simplified):
        A_win = sum of window areas
        Q_solar = A_win * g * Fc * I_summer
        Q_internal = q_int * A_floor
        indicator = (Q_solar + Q_internal) / A_floor
    """

    # --- Grundgrößen / Geometrie ---
    floor_area = sp.floor_area   # m², im Model definiert

    # Fensterflächen je Orientierung
    win_n = sp.window_area_north
    win_s = sp.window_area_south
    win_e = sp.window_area_east
    win_w = sp.window_area_west

    window_area_total = win_n + win_s + win_e + win_w  # m²

    # --- Optische Eigenschaften ---
    g_value = sp.g_value
    Fc = sp.shading_factor

    # --- Innere Lasten ---
    q_int = sp.internal_gains_density  # W/m²

    # --- Solare Gewinne (W) ---
    # sehr vereinfachte Annahme: gleiche Strahlungsstärke für alle Orientierungen
    Q_solar = window_area_total * g_value * Fc * SUMMER_SOLAR_INTENSITY  # W

    # --- Innere Gewinne (W) ---
    Q_internal = q_int * floor_area  # W

    # --- Kennwert in W/m² ---
    if floor_area > 0:
        indicator = (Q_solar + Q_internal) / floor_area
    else:
        indicator = 0.0

    # auto_indicator im Model aktualisieren
    sp.auto_indicator = indicator
    sp.save()

    # Effective indicator (Override oder Auto)
    if sp.override_indicator is not None:
        effective_indicator = sp.override_indicator
    else:
        effective_indicator = sp.auto_indicator

    # --- Rating bestimmen ---
    rating = classify_indicator(effective_indicator)

    return {
        "floor_area": floor_area,
        "window_area_total": window_area_total,
        "win_n": win_n,
        "win_s": win_s,
        "win_e": win_e,
        "win_w": win_w,
        "g_value": g_value,
        "shading_factor": Fc,
        "q_int": q_int,
        "Q_solar_W": Q_solar,
        "Q_internal_W": Q_internal,
        "auto_indicator_W_m2": indicator,
        "effective_indicator_W_m2": effective_indicator,
        "rating": rating,
    }


def classify_indicator(indicator: float) -> str:
    """
    Simple verbal rating for the overheating indicator.
    Thresholds can be tuned later.
    """
    if indicator < 10:
        return "low overheating risk"
    elif indicator < 20:
        return "medium overheating risk"
    return "high overheating risk"
