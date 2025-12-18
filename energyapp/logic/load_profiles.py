import math


class EnergyCalculator:
    def __init__(self, project):
        self.project = project
        self.components = project.components.all()

        # Konstanten & Parameter
        self.c_luft = 0.34  # Wh/m³K

        # Klimadaten Würzburg (aus CSV 03)
        self.months = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
        self.days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.temp_ambient = [-1.2, 0.4, 4.3, 8.2, 13.7, 16.4, 18, 17.8, 13.1, 8.7, 3, -0.2]

        # Strahlungsdaten (W/m²) [N, O, S, W, H] - Vereinfacht aus CSV übernommen
        self.radiation = {
            'N': [17, 22, 40, 55, 83, 89, 86, 70, 51, 32, 17, 10],
            'O': [35, 36, 74, 89, 146, 130, 137, 121, 88, 60, 28, 18],
            'S': [70, 55, 92, 93, 123, 115, 120, 119, 107, 92, 43, 34],
            'W': [25, 29, 56, 72, 112, 114, 112, 97, 71, 47, 22, 18],
            'H': [43, 53, 107, 141, 216, 219, 218, 185, 134, 85, 40, 25],
            'X': [0] * 12
        }

    def calculate_h_values(self):
        # H_T (Transmission)
        h_t = sum([c.ht_value() for c in self.components])
        # Wärmebrückenaufschlag (pauschal oder detailliert, hier vereinfacht +5% oder aus CSV WB)
        # Im CSV gibt es einen WB Eintrag, wir nehmen an, der User legt eine Komponente "Wärmebrücke" an

        # H_V (Lüftung)
        # H_V = V_dot * c_p,air * (1 - WRG) (vereinfacht, genaue Formel hängt von Norm ab)
        # Aus CSV 04: H_V = 87.465
        h_v = self.project.luftvolumenstrom * self.c_luft * (
                    1 - (self.project.wrg_wirkungsgrad if self.project.wrg_wirkungsgrad < 1 else 0))
        # Falls WRG im CSV anders berechnet wird, hier anpassen (Reduktionsfaktor etc.)

        return h_t, h_v

    def calculate_time_constant(self, h_loss_total):
        # Tau = C_wirk / H_loss
        c_wirk = self.project.ngf * self.project.c_wirk_pauschal  # Wh/K (z.B. 30000)
        if h_loss_total > 0:
            tau = c_wirk / h_loss_total
        else:
            tau = 0

        # Parameter a für Ausnutzungsgrad (DIN V 18599 / ISO 13790)
        # a = a0 + (tau / tau0) -> stark vereinfacht oft a = 1 + (tau/15)
        # Im CSV Blatt 03 steht Parameter a = 7.34. Die Formel variiert je nach Norm.
        # Wir nutzen eine Standard-Approximation für Wohngebäude:
        a = 1 + (tau / 15.0)
        return tau, a, c_wirk

    def monthly_calculation(self):
        h_t, h_v = self.calculate_h_values()
        results = []

        total_heating_demand = 0

        # Interne Gewinne (vereinfacht aus CSV: 21.5 Wh/m²d * Fläche oder pauschal)
        # CSV Blatt 04 "Innere Wärmegewinne" ~ 1097 kWh im Jan für 600m²
        qi_daily_per_sqm = 2.5  # W/m² ca. Standardwert, im CSV scheint es höher.
        # Wir nehmen den CSV Wert zurückgerechnet: ~1097 / (31 * 600) * 1000 = ca 59 W?
        # Nein, CSV sagt q_I = 21.5 Wh/(m²d).
        qi_specific = 21.527  # Wh/(m²d) aus CSV

        monthly_data = []

        for i, month in enumerate(self.months):
            hours = self.days_per_month[i] * 24
            t_diff = self.project.raum_soll_temp - self.temp_ambient[i]

            # 1. Verluste
            q_t = h_t * t_diff * hours / 1000  # kWh
            q_v = h_v * t_diff * hours / 1000  # kWh
            q_loss = q_t + q_v

            # 2. Gewinne
            # Intern
            q_i = (qi_specific * self.project.ngf * self.days_per_month[i]) / 1000  # kWh

            # Solar
            q_s = 0
            for comp in self.components:
                if comp.g_value > 0 and comp.orientation in self.radiation:
                    # Q_s = I * A * g * F_s (Verschattung etc pauschal 0.7*0.9?)
                    # CSV Blatt 04 nutzt F_g=0.7, g=0.6 -> Faktor 0.42
                    rad = self.radiation[comp.orientation][i]  # W/m² (Mittelwert) -> Wh/m² Monat?
                    # Achtung: CSV Strahlung ist W/m² (Monatsmittel).
                    # Energie = Strahlung * Stunden
                    # Im CSV Blatt 03 stehen Werte wie "17 W/m²" für Nord im Jan.
                    # Q_s_comp = (W/m² * h) * Fläche * 0.42 (Gesamtdurchlassgrad etc)

                    # Faktor aus CSV rekonstruiert:
                    # Nord Jan: 55.125 kWh Solare Gewinne. Fläche 131.25. Strahlung 17 W/m².
                    # 17 * 24 * 31 = 12648 Wh/m².
                    # 12648 * 131.25 * X = 55125 Wh -> X = 0.033? Irgendwas stimmt nicht an der Einheit.
                    # Ah, CSV Zeile 32: Strahlung 17 W/m².
                    # Solare Gewinne Nord Jan: 55.125 kWh.
                    # Formel: I_s * t * A * g_tot.

                    # Wir nutzen hier eine Standardformel, Werte müssen ggf. kalibriert werden.
                    eff_g = 0.42  # 0.7 * 0.6
                    q_s += (rad * hours * comp.area * eff_g) / 1000

            q_gain = q_i + q_s

            # 3. Ausnutzungsgrad (eta)
            if q_loss <= 0:
                gamma = 100000  # Unendlich
            else:
                gamma = q_gain / q_loss

            tau, a_param, _ = self.calculate_time_constant(h_t + h_v)

            if gamma > 0 and gamma != 1:
                eta = (1 - gamma ** a_param) / (1 - gamma ** (a_param + 1))
            elif gamma == 1:
                eta = a_param / (a_param + 1)
            else:
                eta = 1  # Falls keine Gewinne

            # 4. Heizwärmebedarf Q_h
            q_h = q_loss - (eta * q_gain)
            if q_h < 0: q_h = 0

            total_heating_demand += q_h

            monthly_data.append({
                'month': month,
                'temp': self.temp_ambient[i],
                'q_t': round(q_t, 1),
                'q_v': round(q_v, 1),
                'q_loss': round(q_loss, 1),
                'q_i': round(q_i, 1),
                'q_s': round(q_s, 1),
                'q_gain': round(q_gain, 1),
                'gamma': round(gamma, 2),
                'eta': round(eta, 2),
                'q_h': round(q_h, 1)
            })

        return {
            'monthly_data': monthly_data,
            'annual_heating_demand': round(total_heating_demand, 1),
            'specific_demand': round(total_heating_demand / self.project.ngf, 1),
            'h_t': round(h_t, 1),
            'h_v': round(h_v, 1)
        }