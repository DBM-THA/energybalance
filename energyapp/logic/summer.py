from ..models import SummerProtection

# Fc-Tabelle nach DIN / Excel (nur die von euch genutzten Zeilen)
FC_TABLE = {
    ("none", "solar"): 1.00,
    ("none", "triple"): 1.00,
    ("none", "double"): 1.00,

    ("internal", "solar"): 0.65,
    ("internal", "triple"): 0.70,
    ("internal", "double"): 0.65,

    ("roller_closed", "solar"): 0.35,
    ("roller_closed", "triple"): 0.30,
    ("roller_closed", "double"): 0.30,

    ("jalousie_45", "solar"): 0.30,
    ("jalousie_45", "triple"): 0.25,
    ("jalousie_45", "double"): 0.25,

    ("awning", "solar"): 0.30,
    ("awning", "triple"): 0.25,
    ("awning", "double"): 0.25,

    ("overhang", "solar"): 0.55,
    ("overhang", "triple"): 0.50,
    ("overhang", "double"): 0.50,
}


def calc_summer_overheating(sp: SummerProtection) -> dict:
    """
    Sommerlicher Wärmeschutz – Excel-Logik
    Schritt 1: Fensterflächenanteil
    Schritt 2: S_vorh
    Schritt 3: S_zul
    """

    # --- Inputs ---
    ngf = sp.ngf_m2
    a_win = sp.window_area_m2
    orientation = sp.orientation

    building = sp.building
    g_map = {
        "N": building.g_n,
        "E": building.g_e,
        "S": building.g_s,
        "W": building.g_w,
    }
    g = g_map.get(orientation, building.g_s)

    fc = FC_TABLE.get((sp.shading_type, sp.glazing_category), 1.0)

    # --- Schritt 1 ---
    window_share = (a_win / ngf) if ngf > 0 else 0.0

    # --- Schritt 2 ---
    a_g_fc = a_win * g * fc
    s_vorh = (a_g_fc / ngf) if ngf > 0 else 0.0

    # --- Schritt 3 (vereinfachte, saubere Basis wie Excel) ---
    climate_base = {
        "A": 0.050,
        "B": 0.061,
        "C": 0.070,
    }
    s1 = climate_base.get(sp.climate_region, 0.061)

    # Beispiel-Korrektur Fensterflächenanteil (wie euer Excel-Beispiel)
    s2_1 = -0.006 if window_share >= 0.316 else 0.0

    s_zul = s1 + s2_1

    # --- Ergebnis ---
    ok = s_vorh <= s_zul

    return {
        "orientation": orientation,
        "ngf_m2": round(ngf, 2),
        "window_area_m2": round(a_win, 2),
        "window_share": round(window_share, 4),
        "g_value": round(g, 3),
        "Fc": round(fc, 3),
        "A_g_Fc": round(a_g_fc, 3),
        "S_vorh": round(s_vorh, 3),
        "S_zul": round(s_zul, 3),
        "ok": ok,
    }
