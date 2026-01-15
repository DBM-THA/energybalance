from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional

from energyapp.models import Building, EnergyResultSheet01


def _safe_div(a: float, b: float) -> float:
    if b in (0, None):
        return 0.0
    return a / b


def _num(x: Optional[float]) -> float:
    return float(x) if x is not None else 0.0


@dataclass
class ExternalSources:
    """
    Hier bündeln wir Werte, die in Excel aus anderen Sheets kommen.
    Stand heute sind viele dieser Sheets bei dir noch nicht in Django abgebildet.
    Deshalb: Default 0 + eindeutige Kommentare (Excel-Quelle).
    """
    # Excel-Quelle: ='03 MONATSBILANZ'!O76
    heating_kwh_a: float = 0.0

    # Excel-Quelle: ='12 LICHT UND WASSER'!L56
    dhw_kwh_a: float = 0.0

    # Excel-Quelle: ='11 LUFTFÖRDERUNG'!E97
    ventilation_kwh_a: float = 0.0

    # Excel-Quelle: ='12 LICHT UND WASSER'!L36
    lighting_kwh_a: float = 0.0

    # Excel-Quelle: ='10 INNERE WÄRMEQUELLEN'!N49
    user_process_kwh_a: float = 0.0

    # Excel-Quelle: ='05 PHOTOVOLTAIK'!Q111
    pv_total_kwh_a: float = 0.0

    # Excel-Quelle: NGF_t (Name Manager) -> ='00 GEBÄUDEDATEN'!F40 (bei dir: Nutzfläche)
    ngf_m2: float = 0.0

    # Excel-Quelle: '00 GEBÄUDEDATEN'!F136 (Systemtyp) / F137 (Arbeitszahl WP)
    heating_system: str = ""
    wp_cop: float = 0.0


def build_external_sources(building: Building) -> ExternalSources:
    """
    Minimal sinnvolle Zuordnung zu deinem aktuellen Datenmodell:
    - Heizwärmebedarf: building.result_Q_h (kommt aus deiner calc_heating_demand)
    - PV: building.result_Q_PV_total
    Alles andere ist aktuell nicht im Modell: bleibt 0.
    """

    # Excel: NGF_t (Name Manager) -> bei uns: building.ngf_t
    ngf = _num(getattr(building, "ngf_t", None))
    if ngf <= 0:
        # Fallback für Altbestand ohne ngf_t
        ngf = _num(building.result_floor_area)

    return ExternalSources(
        # Excel-Quelle: ='03 MONATSBILANZ'!O76
        heating_kwh_a=_num(building.result_Q_h),

        # Excel-Quelle: ='05 PHOTOVOLTAIK'!Q111
        pv_total_kwh_a=_num(building.result_Q_PV_total),

        # Excel-Quelle: NGF_t (Name Manager) -> ='00 GEBÄUDEDATEN'!F40
        ngf_m2=ngf,

        # noch nicht abgebildet -> 0
        dhw_kwh_a=0.0,
        ventilation_kwh_a=0.0,
        lighting_kwh_a=0.0,
        user_process_kwh_a=0.0,

        heating_system="",
        wp_cop=0.0,
    )


def calculate_sheet01(building: Building, sheet: EnergyResultSheet01) -> Dict[str, Any]:
    """
    Gibt ein Dict zurück, das du 1:1 als `calc.*` im Template nutzt.
    Benennung orientiert sich an deinen Excel-Zellen (F22, G22, ...).
    """
    ext = build_external_sources(building)

    NGF_t = _num(ext.ngf_m2)

    # =========================
    # Nutzenergie (F22..F29)
    # =========================
    # Heizwärme
    # Excel-Quelle: ='03 MONATSBILANZ'!O76
    F22 = _num(ext.heating_kwh_a)
    # Excel-Quelle: ='03 MONATSBILANZ'!O77 (im Excel schon spezifisch)
    # Wir berechnen es hier als Näherung: F22 / NGF_t
    G22 = _safe_div(F22, NGF_t)

    # Heizwärme Beleuchtung (Excel: 0 / 0 / Vergleich 5)
    F23 = 0.0
    G23 = 0.0

    # Trinkwarmwasser
    # Excel-Quelle: ='12 LICHT UND WASSER'!L56
    F24 = _num(ext.dhw_kwh_a)
    # Excel-Formel: ='12 LICHT UND WASSER'!L56/'04 LASTGANG'!E21
    # Kommentar: in Excel ist E21 sehr wahrscheinlich NGF_t oder Bezugsfläche -> wir verwenden NGF_t
    G24 = _safe_div(F24, NGF_t)

    # Luftförderung
    # Excel-Quelle: ='11 LUFTFÖRDERUNG'!E97
    F25 = _num(ext.ventilation_kwh_a)
    # Excel-Formel: ='11 LUFTFÖRDERUNG'!E97/'04 LASTGANG'!E21 -> hier: / NGF_t
    G25 = _safe_div(F25, NGF_t)

    # Kälte
    F26 = 0.0
    G26 = 0.0

    # Beleuchtung
    # Excel-Quelle: ='12 LICHT UND WASSER'!L36
    F27 = _num(ext.lighting_kwh_a)
    # Excel-Formel: ='12 LICHT UND WASSER'!L36/'04 LASTGANG'!E21 -> / NGF_t
    G27 = _safe_div(F27, NGF_t)

    # Sonstiges
    F28 = 0.0
    G28 = 0.0

    # Nutzer (Prozess)
    # Excel-Quelle: ='10 INNERE WÄRMEQUELLEN'!N49
    F29 = _num(ext.user_process_kwh_a)
    # Excel-Quelle: ='10 INNERE WÄRMEQUELLEN'!O49 -> wir berechnen: / NGF_t
    G29 = _safe_div(F29, NGF_t)

    # Nutzenergiebedarf
    # Excel-Formel: =SUM(F22:F29)
    F30 = F22 + F23 + F24 + F25 + F26 + F27 + F28 + F29
    # Excel-Formel: =SUM(G22:G29)
    G30 = G22 + G23 + G24 + G25 + G26 + G27 + G28 + G29

    # =========================
    # Endenergie Wärme (F38..F42)
    # =========================
    # Heizwärme s.o
    # Excel-Formel: =E38*(F22) ; E38 = 1
    F38 = 1.0 * F22
    # Excel-Formel: =F38/NGF_t
    G38 = _safe_div(F38, NGF_t)

    # Übergabe Heiz/Wasser
    # Excel-Formel: =F22*$E39
    F39 = F22 * _num(sheet.E39_transfer_heat_water)
    G39 = _safe_div(F39, NGF_t)

    # Verteilung Heiz/Wasser
    # Excel-Formel: =E40*(F22+F39)
    F40 = _num(sheet.E40_distribution_heat_water) * (F22 + F39)
    G40 = _safe_div(F40, NGF_t)

    # Speicherung Heiz/Wasser
    # Excel-Formel: =E41*(F22+F39+F40)
    F41 = _num(sheet.E41_storage_heat_water) * (F22 + F39 + F40)
    G41 = _safe_div(F41, NGF_t)

    # - Erzeugung Solar
    # Excel-Formel: =-F22*$E42
    F42 = -F22 * _num(sheet.E42_solar_generation_factor)
    G42 = _safe_div(F42, NGF_t)

    # Erzeugernutzwärmeabgabe
    # Excel-Formel: =SUM(F38:F42)
    F43 = F38 + F39 + F40 + F41 + F42
    # Excel-Formel: =SUM(G38:G42)
    G43 = G38 + G39 + G40 + G41 + G42

    # =========================
    # Endenergie (F46..F53)
    # Hier fehlen dir aktuell Systemtyp + COP im Modell.
    # Wir setzen die Schalter C46/C47/C48 vorerst auf 0.
    # =========================
    # Excel-Formeln:
    # C46 =IF(OR('00 GEBÄUDEDATEN'!F136="Luft/Wasser Wärmepumpe"; '00 GEBÄUDEDATEN'!F136="Wasser/Wasser Wärmepumpe");1;0)
    # E46 =IFERROR(1/'00 GEBÄUDEDATEN'!F137;0)
    # F46 =$F$43*$E46*C46
    C46 = 0.0
    E46 = 0.0
    F46 = F43 * E46 * C46
    G46 = _safe_div(F46, NGF_t)

    # Fernwärme
    # C47 =IF('00 GEBÄUDEDATEN'!F136="Fernwärme";1;0)
    C47 = 0.0
    E47 = _num(sheet.E47_factor_fw)
    F47 = F43 * E47 * C47
    G47 = _safe_div(F47, NGF_t)

    # Gas
    # C48 =IF('00 GEBÄUDEDATEN'!F136="Gasheizung";1;0)
    C48 = 0.0
    E48 = _num(sheet.E48_factor_gas)
    F48 = F43 * E48 * C48
    G48 = _safe_div(F48, NGF_t)

    # Hilfsenergie Heizung
    # Excel-Formel: =$F$43*$E49
    F49 = F43 * _num(sheet.E49_aux_heating)
    G49 = _safe_div(F49, NGF_t)

    # Trinkwarmwasser
    # Excel-Formel: =F24
    F50 = F24
    G50 = _safe_div(F50, NGF_t)

    # Luftförderung
    # Excel-Formel: =F25*$E51
    F51 = F25 * _num(sheet.E51_air_support)
    G51 = _safe_div(F51, NGF_t)

    # Beleuchtung
    # Excel-Formel: =F27*$E52
    F52 = F27 * _num(sheet.E52_lighting)
    G52 = _safe_div(F52, NGF_t)

    # Nutzer (Prozess)
    # Excel-Formel: =F29*$E53
    F53 = F29 * _num(sheet.E53_user_process)
    G53 = _safe_div(F53, NGF_t)

    # Endenergiebedarf
    # Excel-Formel: =SUM(F46:F53)
    F54 = F46 + F47 + F48 + F49 + F50 + F51 + F52 + F53
    # Excel-Formel: =SUM(G46:G53)
    G54 = G46 + G47 + G48 + G49 + G50 + G51 + G52 + G53

    # =========================
    # Endenergie Strom (F59..F66)
    # =========================
    # Excel: E59 = C46 ; F59 = E59*F46
    E59 = C46
    F59 = E59 * F46
    G59 = _safe_div(F59, NGF_t)

    # FW / Gas sind Strom = 0
    F60 = 0.0
    G60 = 0.0
    F61 = 0.0
    G61 = 0.0

    # Hilfsenergie Heizung: =F49
    F62 = F49
    G62 = _safe_div(F62, NGF_t)

    # Trinkwarmwasser (wenn El.): =E63*F50 ; E63=1
    F63 = 1.0 * F50
    G63 = _safe_div(F63, NGF_t)

    # Luftförderung / Beleuchtung / Nutzer
    F64 = F51
    G64 = _safe_div(F64, NGF_t)

    F65 = F52
    G65 = _safe_div(F65, NGF_t)

    F66 = F53
    G66 = _safe_div(F66, NGF_t)

    # Endenergiebedarf Strom: =SUM(F59:F66) / =SUM(G59:G66)
    F67 = F59 + F60 + F61 + F62 + F63 + F64 + F65 + F66
    G67 = G59 + G60 + G61 + G62 + G63 + G64 + G65 + G66

    # =========================
    # Primärenergie (F75..F79)
    # =========================
    # Wärme Solar: =$F$42*E75  (E75=0 in Excel)
    F75 = 0.0
    G75 = _safe_div(F75, NGF_t)

    # Wärme Fernwärme: =F47*E76 (E76=0,25)
    F76 = F47 * 0.25
    G76 = _safe_div(F76, NGF_t)

    # Wärme Gas: =F48*E77 (E77=1,1)
    F77 = F48 * 1.1
    G77 = _safe_div(F77, NGF_t)

    # Strom (On-Site)
    # Excel-Quelle: '05 PHOTOVOLTAIK'!Q111 und F68/I78/E78 etc.
    # Dein Excel referenziert F68 – das ist in deiner Tabelle "Endenergiebedarf Strom" (F67 hier).
    # Wir verwenden: F68 ~ F67 (Endenergiebedarf Strom kWh/a) als Näherung.
    F68_like = F67

    pv_total = _num(ext.pv_total_kwh_a)  # '05 PHOTOVOLTAIK'!Q111
    I78 = _num(sheet.I78_pv_self_share)  # Deckungsanteil
    E78 = -1.8

    # Excel-Formel:
    # =IF(PV_total > F68; F68*I78*E78; PV_total*I78*E78)
    base_on = F68_like if pv_total > F68_like else pv_total
    F78 = base_on * I78 * E78
    G78 = _safe_div(F78, NGF_t)

    # Strom (Off-Site): =$F$68*I79*E79 ; E79=1,8 ; I79=1-I75-I76
    # I75/I76 bei dir kommen aus PV-Aufteilung; noch nicht modelliert -> wir setzen I79 = 1 - I78 als pragmatisches Default
    I79 = max(0.0, 1.0 - I78)
    E79 = 1.8
    F79 = F68_like * I79 * E79
    G79 = _safe_div(F79, NGF_t)

    # Primärenergiebedarf: =SUM(F75:F79), =SUM(G75:G79)
    F80 = F75 + F76 + F77 + F78 + F79
    G80 = G75 + G76 + G77 + G78 + G79

    # Überschuss Strom (On-Site):
    # Excel-Formel: ='05 PHOTOVOLTAIK'!Q111-'01 ERGEBNIS ENERGIE'!F78/E78
    # Hinweis: F78/E78 gibt den kWh/a-Anteil zurück (weil E78=-1,8), passt als Rückrechnung.
    F87 = pv_total - _safe_div(F78, E78) if E78 != 0 else pv_total
    G87 = _safe_div(F87, NGF_t)

    return {
        # Nutzenergie
        "F22": round(F22, 3), "G22": round(G22, 3),
        "F24": round(F24, 3), "G24": round(G24, 3),
        "F25": round(F25, 3), "G25": round(G25, 3),
        "F27": round(F27, 3), "G27": round(G27, 3),
        "F29": round(F29, 3), "G29": round(G29, 3),
        "F30": round(F30, 3), "G30": round(G30, 3),

        # Endenergie Wärme
        "F38": round(F38, 3), "G38": round(G38, 3),
        "F39": round(F39, 3), "G39": round(G39, 3),
        "F40": round(F40, 3), "G40": round(G40, 3),
        "F41": round(F41, 3), "G41": round(G41, 3),
        "F42": round(F42, 3), "G42": round(G42, 3),
        "F43": round(F43, 3), "G43": round(G43, 3),

        # Endenergie gesamt
        "E46": round(E46, 3), "F46": round(F46, 3), "G46": round(G46, 3),
        "F47": round(F47, 3), "G47": round(G47, 3),
        "F48": round(F48, 3), "G48": round(G48, 3),
        "F49": round(F49, 3), "G49": round(G49, 3),
        "F50": round(F50, 3), "G50": round(G50, 3),
        "F51": round(F51, 3), "G51": round(G51, 3),
        "F52": round(F52, 3), "G52": round(G52, 3),
        "F53": round(F53, 3), "G53": round(G53, 3),
        "F54": round(F54, 3), "G54": round(G54, 3),

        # Endenergie Strom
        "E59": round(E59, 3),
        "F59": round(F59, 3), "G59": round(G59, 3),
        "F60": round(F60, 3), "G60": round(G60, 3),
        "F61": round(F61, 3), "G61": round(G61, 3),
        "F62": round(F62, 3), "G62": round(G62, 3),
        "F63": round(F63, 3), "G63": round(G63, 3),
        "F64": round(F64, 3), "G64": round(G64, 3),
        "F65": round(F65, 3), "G65": round(G65, 3),
        "F66": round(F66, 3), "G66": round(G66, 3),
        "F67": round(F67, 3), "G67": round(G67, 3),

        # Primärenergie
        "F75": round(F75, 3), "G75": round(G75, 3),
        "F76": round(F76, 3), "G76": round(G76, 3),
        "F77": round(F77, 3), "G77": round(G77, 3),
        "F78": round(F78, 3), "G78": round(G78, 3),
        "F79": round(F79, 3), "G79": round(G79, 3),
        "F80": round(F80, 3), "G80": round(G80, 3),

        # Deckungsanteil Off-Site als Info
        "I79": f"{round(I79 * 100, 1)}%",

        # Überschuss
        "F87": round(F87, 3), "G87": round(G87, 3),
    }
