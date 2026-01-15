from energyapp.models import Building


def calc_heating_demand(building: Building) -> dict:
    # Grundgrößen
    length = building.length_ns      # m
    width = building.width_ow        # m
    storeys = building.storeys
    h_room = building.room_height    # m

    h_building = storeys * h_room

    floor_area = length * width                      # m²

    # BGF = Länge * Breite * Geschosse
    bgf = floor_area * storeys

    # NGF_t = BGF * 0,8
    ngf_t = bgf * 0.8

    roof_area = floor_area                           # m²
    floor_area_ceiling = floor_area                  # m²

    # Fassadenflächen
    facade_n = length * h_building
    facade_s = length * h_building
    facade_e = width * h_building
    facade_w = width * h_building

    # Fensteranteile von % auf Anteil umrechnen
    ws_n = building.window_share_n / 100.0
    ws_e = building.window_share_e / 100.0
    ws_s = building.window_share_s / 100.0
    ws_w = building.window_share_w / 100.0

    # Fensterflächen je Orientierung
    win_n = facade_n * ws_n
    win_s = facade_s * ws_s
    win_e = facade_e * ws_e
    win_w = facade_w * ws_w

    window_area = win_n + win_e + win_s + win_w

    # opake Wandflächen
    opaque_n = facade_n - win_n
    opaque_s = facade_s - win_s
    opaque_e = facade_e - win_e
    opaque_w = facade_w - win_w
    opaque_wall_area = opaque_n + opaque_s + opaque_e + opaque_w

    # Transmissionswärmeverlust-Koeffizient H_T [W/K]
    H_T = (
        building.u_wall * opaque_wall_area
        + building.u_roof * roof_area
        + building.u_floor * floor_area_ceiling
        + building.u_window * window_area
    )

    # Lüftung: H_V = 0.34 * n * V
    V = floor_area * h_room * storeys  # m³
    H_V = 0.34 * building.air_change_rate * V  # W/K

    # Heizgradtage -> Heizstunden
    HDD = building.degree_days  # K*d
    heating_hours = HDD * 24    # h

    # Jahresverluste durch Transmission und Lüftung [kWh/a]
    Q_T = H_T * heating_hours / 1000.0
    Q_V = H_V * heating_hours / 1000.0

    # Innere Gewinne (sehr grob):
    # 80 W/Person, 8 h/Tag belegt
    internal_power_per_person = 80.0  # W
    occupancy_hours = HDD * 8.0 / 1.0  # 8 h pro Heiztag
    Q_I = (
        building.persons
        * internal_power_per_person
        * occupancy_hours
        / 1000.0
    )  # kWh/a

    # Solare Gewinne – sehr einfache Orientierungswerte [kWh/m²*a]
    # Diese Zahlen sind Näherungen, nicht normgerecht.
    sol_k_n = 150.0
    sol_k_e = 300.0
    sol_k_s = 500.0
    sol_k_w = 300.0

    Q_S_n = win_n * building.g_n * sol_k_n
    Q_S_e = win_e * building.g_e * sol_k_e
    Q_S_s = win_s * building.g_s * sol_k_s
    Q_S_w = win_w * building.g_w * sol_k_w

    Q_S = Q_S_n + Q_S_e + Q_S_s + Q_S_w  # kWh/a

    # Heizwärmebedarf nach einfacher Energiebilanz:
    # Q_h = Q_V + Q_T - Q_I - Q_S
    Q_h = Q_V + Q_T - Q_I - Q_S
    if Q_h < 0:
        Q_h = 0.0

    # -------- PV-Bilanz (sehr vereinfacht) --------
    # PV-Fläche = Anteil der Dachfläche
    pv_area = roof_area * (building.pv_roof_share / 100.0)

    # Gesamt-PV-Ertrag [kWh/a]
    Q_PV_total = pv_area * building.pv_specific_yield

    # Eigenverbrauch und Überschuss
    pv_self_frac = building.pv_self_consumption_share / 100.0
    Q_PV_on = Q_PV_total * pv_self_frac      # im Gebäude genutzt
    Q_PV_off = Q_PV_total - Q_PV_on          # Überschuss


    return {
        "floor_area": floor_area,
        "roof_area": roof_area,
        "opaque_wall_area": opaque_wall_area,
        "window_area": window_area,

        "H_T": H_T,
        "H_V": H_V,
        "Q_T": Q_T,
        "Q_V": Q_V,
        "Q_I": Q_I,
        "Q_S": Q_S,
        "Q_h": Q_h,

        "Q_S_n": Q_S_n,
        "Q_S_e": Q_S_e,
        "Q_S_s": Q_S_s,
        "Q_S_w": Q_S_w,

        "Q_S_w": Q_S_w,

        "Q_PV_total": Q_PV_total,
        "Q_PV_on": Q_PV_on,
        "Q_PV_off": Q_PV_off,

        "bgf": bgf,
        "ngf_t": ngf_t,

    }
