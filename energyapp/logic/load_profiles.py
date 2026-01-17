import math


class EnergyCalculator:

    def __init__(self, building):
        self.b = building
        # Monatsdaten (aus deinem Excel Blatt 03)
        self.months = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
        self.days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.temp_ambient = [-1.2, 0.4, 4.3, 8.2, 13.7, 16.4, 18.0, 17.8, 13.1, 8.7, 3.0, -0.2]

        # Strahlungsdaten Würzburg [W/m² Mittelwert]
        self.rad_data = {
            'N': [17, 22, 40, 55, 83, 89, 86, 70, 51, 32, 17, 10],
            'O': [35, 36, 74, 89, 146, 130, 137, 121, 88, 60, 28, 18],
            'S': [70, 55, 92, 93, 123, 115, 120, 119, 107, 92, 43, 34],
            'W': [25, 29, 56, 72, 112, 114, 112, 97, 71, 47, 22, 18]
        }

    def calculate(self):
        # --- 1. GEOMETRIE BERECHNEN ---
        floor_area = self.b.length_ns * self.b.width_ow
        roof_area = floor_area
        total_height = self.b.storeys * self.b.room_height

        # Brutto-Fassadenflächen
        area_fac_ns = self.b.width_ow * total_height
        area_fac_ow = self.b.length_ns * total_height

        # Fensterflächen (Netto)
        aw_n = area_fac_ns * (self.b.window_share_n / 100)
        aw_s = area_fac_ns * (self.b.window_share_s / 100)
        aw_e = area_fac_ow * (self.b.window_share_e / 100)
        aw_w = area_fac_ow * (self.b.window_share_w / 100)
        total_window_area = aw_n + aw_s + aw_e + aw_w

        # Opake Wandflächen
        opaque_wall_area = (2 * area_fac_ns + 2 * area_fac_ow) - total_window_area

        # --- 2. WÄRMEVERLUSTE (H-WERTE) ---
        # Transmission H_T
        h_t = (opaque_wall_area * self.b.u_wall +
               roof_area * self.b.u_roof +
               floor_area * self.b.u_floor * 0.6 +  # fx=0.6 für Boden
               total_window_area * self.b.u_window)

        # Lüftung H_V (Volumen * Luftwechsel * 0.34)
        volume = floor_area * total_height
        h_v = volume * self.b.air_change_rate * 0.34

        # --- 3. MONATS-BILANZ (Blatt 03 & 04) ---
        monthly_results = []
        annual_q_h = 0

        for i, month in enumerate(self.months):
            hours = self.days[i] * 24
            delta_t = max(0, self.b.setpoint_temp - self.temp_ambient[i])

            # Verluste Q_loss
            q_loss = (h_t + h_v) * delta_t * hours / 1000  # kWh

            # Solare Gewinne Q_s (Faktor 0.7 für Verschattung/Rahmen)
            q_s = (aw_n * self.rad_data['N'][i] * self.b.g_n +
                   aw_s * self.rad_data['S'][i] * self.b.g_s +
                   aw_e * self.rad_data['O'][i] * self.b.g_e +
                   aw_w * self.rad_data['W'][i] * self.b.g_w) * 0.7 * hours / 1000

            # Interne Gewinne Q_i (70W pro Person)
            q_i = (self.b.persons * 70 * hours) / 1000

            # Heizwärmebedarf Q_h (Ausnutzungsgrad eta vereinfacht 0.95)
            q_h = max(0, q_loss - 0.95 * (q_s + q_i))
            annual_q_h += q_h

            monthly_results.append({
                'month': month,
                'temp': self.temp_ambient[i],
                'q_loss': round(q_loss, 1),
                'q_gain': round(q_s + q_i, 1),
                'q_h': round(q_h, 1)
            })

        return {
            'monthly_data': monthly_results,
            'annual_heating_demand': round(annual_q_h, 1),
            'specific_demand': round(annual_q_h / (floor_area * self.b.storeys), 1),
            'h_t': round(h_t, 1),
            'h_v': round(h_v, 1),
            'geometry': {
                'ngf': round(floor_area * self.b.storeys, 1),
                'bri': round(volume, 1),
                'window_area': round(total_window_area, 1)
            }
        }