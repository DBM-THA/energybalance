import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from tkinter import messagebox
import db_manager as db

# --- KONFIGURATION ---
COL_WIDTHS = {
    "typ": 25,
    "prozent": 8,
    "pers": 8,
    "lw": 8,
    "h": 8,
    "d": 8,
    "del": 5
}

# Standard-Vorschläge für die Dropdowns (Du kannst trotzdem eigene Werte tippen!)
VALUES_LW = ["0.0", "0.2", "0.5", "0.7", "1.0", "1.2", "1.5", "2.0", "4.0"]
VALUES_H = ["4", "6", "8", "10", "12", "16", "24"]
VALUES_D = ["180", "200", "220", "250", "300", "365"]
VALUES_PERS = ["0", "1", "2", "3", "4", "5", "10", "15", "20", "25", "30", "40", "50", "100"]


class ZoneRow:
    """Repräsentiert eine einzelne Zeile (Zone)"""

    def __init__(self, parent_frame, row_index, app_reference):
        self.id = row_index
        self.app = app_reference

        self.frame = ttk.Frame(parent_frame)
        self.frame.pack(fill=X, pady=2)

        # 1. Dropdown (Typ)
        self.combo_typ = ttk.Combobox(self.frame, values=db.get_kategorien_names(), state="readonly",
                                      width=COL_WIDTHS["typ"], bootstyle="primary")
        self.combo_typ.grid(row=0, column=0, padx=5)
        self.combo_typ.bind("<<ComboboxSelected>>", self.on_type_selected)

        # 2. Prozent Dropdown (Smart & Editierbar)
        p_frame = ttk.Frame(self.frame)
        p_frame.grid(row=0, column=1, padx=5)

        # Prozent lassen wir readonly, damit die 100% Logik sicher bleibt.
        # Wenn du hier auch tippen willst, sag Bescheid - ist aber komplexer mit der Summenprüfung.
        self.combo_percent = ttk.Combobox(p_frame, state="readonly", width=COL_WIDTHS["prozent"] - 3, justify=CENTER)
        self.combo_percent.pack(side=LEFT)
        self.combo_percent.set("0")
        self.combo_percent.bind("<<ComboboxSelected>>", self.on_percent_change)
        self.combo_percent.bind("<Button-1>", self.update_percent_options)
        ttk.Label(p_frame, text="%").pack(side=LEFT)

        # 3. Parameter als Dropdowns
        # WICHTIG: state="normal" erlaubt Auswahl UND freies Tippen!
        self.combo_pers = self._add_combo(2, COL_WIDTHS["pers"], VALUES_PERS, state="normal")
        self.combo_lw = self._add_combo(3, COL_WIDTHS["lw"], VALUES_LW, state="normal")
        self.combo_h = self._add_combo(4, COL_WIDTHS["h"], VALUES_H, state="normal")
        self.combo_d = self._add_combo(5, COL_WIDTHS["d"], VALUES_D, state="normal")

        # 4. Löschen Button
        self.btn_del = ttk.Button(self.frame, text="×", command=lambda: self.app.delete_row(self),
                                  bootstyle="danger-outline", width=COL_WIDTHS["del"])
        self.btn_del.grid(row=0, column=6, padx=10)

    def _add_combo(self, col_idx, width, values, state="normal"):
        cb = ttk.Combobox(self.frame, values=values, state=state, width=width, justify=CENTER)
        cb.set(values[0])
        cb.grid(row=0, column=col_idx, padx=5)
        return cb

    def update_percent_options(self, event=None):
        """Berechnet dynamisch, welche Prozentwerte noch erlaubt sind."""
        current_used = self.app.get_total_percent(exclude_row=self)
        remaining = 100 - current_used
        values = [str(x) for x in range(0, int(remaining) + 1, 5)]
        if int(remaining) % 5 != 0:
            values.append(str(int(remaining)))
        values.sort(key=int)
        self.combo_percent['values'] = values

    def on_percent_change(self, event):
        self.app.check_percent_label()

    def on_type_selected(self, event):
        name = self.combo_typ.get()
        data = db.get_kategorie_defaults(name)
        if data:
            self.combo_pers.set(str(data[0]))
            self.combo_lw.set(str(data[1]))
            self.combo_h.set(str(int(data[2])))
            self.combo_d.set(str(int(data[3])))
        self.app.check_percent_label()

    def get_values(self):
        def gf(val_str):
            try:
                return float(val_str.replace(",", "."))
            except:
                return 0.0

        # Prozent holen
        try:
            p_val = float(self.combo_percent.get())
        except:
            p_val = 0.0

        return {
            "typ": self.combo_typ.get(),
            "percent": p_val,
            "pers": gf(self.combo_pers.get()),
            "lw": gf(self.combo_lw.get()),
            "h": gf(self.combo_h.get()),
            "d": gf(self.combo_d.get())
        }

    def destroy(self):
        self.frame.destroy()


class VentilationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lüftungs-Mix Rechner V5.0 (Flexible & Safe)")
        self.root.geometry("1150x800")

        db.init_db()

        # --- OBERER BEREICH ---
        top_frame = ttk.Labelframe(root, text="Projektdaten", padding=20, bootstyle="info")
        top_frame.pack(fill=X, padx=20, pady=10)

        ttk.Label(top_frame, text="Gesamtfläche (m²):").pack(side=LEFT)
        self.entry_total_area = ttk.Entry(top_frame, width=10)
        self.entry_total_area.insert(0, "1000")
        self.entry_total_area.pack(side=LEFT, padx=10)

        ttk.Label(top_frame, text="Strompreis (€/kWh):").pack(side=LEFT, padx=(20, 0))
        self.entry_price = ttk.Entry(top_frame, width=8)
        self.entry_price.insert(0, "0.40")
        self.entry_price.pack(side=LEFT, padx=10)

        # --- HEADER ---
        header_frame = ttk.Frame(root, padding=(30, 5, 20, 0))
        header_frame.pack(fill=X)

        def add_head(text, col, width):
            lbl = ttk.Label(header_frame, text=text, font=("Helvetica", 9, "bold"), width=width, anchor="center")
            if col == 0: lbl.config(anchor="w")
            lbl.grid(row=0, column=col, padx=5)

        add_head("Nutzungsart", 0, COL_WIDTHS["typ"] + 3)
        add_head("Anteil %", 1, COL_WIDTHS["prozent"])
        add_head("Pers.", 2, COL_WIDTHS["pers"])
        add_head("Luftwechsel", 3, COL_WIDTHS["lw"])
        add_head("h / Tag", 4, COL_WIDTHS["h"])
        add_head("Tage / Jahr", 5, COL_WIDTHS["d"])
        add_head("Löschen", 6, COL_WIDTHS["del"])

        ttk.Separator(root, orient=HORIZONTAL).pack(fill=X, padx=20, pady=5)

        # --- SCROLL BEREICH ---
        self.scroll_container = ScrolledFrame(root, autohide=False)
        self.scroll_container.pack(fill=BOTH, expand=YES, padx=20, pady=5)

        self.rows = []

        # --- BUTTONS ---
        action_frame = ttk.Frame(root, padding=20)
        action_frame.pack(fill=X)

        ttk.Button(action_frame, text="+ Nutzung hinzufügen", command=self.add_row, bootstyle="primary").pack(side=LEFT)
        self.lbl_total_percent = ttk.Label(action_frame, text="Summe: 0%", font=("Helvetica", 12, "bold"),
                                           bootstyle="secondary")
        self.lbl_total_percent.pack(side=LEFT, padx=20)

        # --- ERGEBNIS BEREICH ---
        result_frame = ttk.Labelframe(root, text="Ergebnis Berechnung", padding=20, bootstyle="success")
        result_frame.pack(fill=X, padx=20, pady=(0, 20))

        self.res_luft = ttk.Label(result_frame, text="0 m³/h", font=("Helvetica", 18, "bold"))
        self.res_luft.grid(row=0, column=0, padx=20)
        ttk.Label(result_frame, text="Gesamt Frischluft").grid(row=1, column=0)

        self.res_kw = ttk.Label(result_frame, text="0.0 kW", font=("Helvetica", 18, "bold"))
        self.res_kw.grid(row=0, column=1, padx=20)
        ttk.Label(result_frame, text="Gesamt Leistung").grid(row=1, column=1)

        self.res_kwh = ttk.Label(result_frame, text="0 kWh/a", font=("Helvetica", 18, "bold"))
        self.res_kwh.grid(row=0, column=2, padx=20)
        ttk.Label(result_frame, text="Gesamt Energie").grid(row=1, column=2)

        self.res_euro = ttk.Label(result_frame, text="0 €", font=("Helvetica", 24, "bold"), bootstyle="danger")
        self.res_euro.grid(row=0, column=3, padx=40)
        ttk.Label(result_frame, text="Jahreskosten").grid(row=1, column=3)

        self.btn_calc = ttk.Button(result_frame, text="JETZT BERECHNEN", command=self.calculate, bootstyle="secondary",
                                   width=25)
        self.btn_calc.grid(row=0, column=4, rowspan=2, padx=40)

        self.add_row()

    def add_row(self):
        row = ZoneRow(self.scroll_container, len(self.rows), self)
        self.rows.append(row)
        self.check_percent_label()

    def delete_row(self, row_obj):
        if len(self.rows) > 1:
            self.rows.remove(row_obj)
            row_obj.destroy()
            self.check_percent_label()
        else:
            messagebox.showwarning("Info", "Mindestens eine Zeile wird benötigt.")

    def get_total_percent(self, exclude_row=None):
        total = 0.0
        for r in self.rows:
            if r == exclude_row:
                continue
            vals = r.get_values()
            total += vals["percent"]
        return total

    def check_percent_label(self):
        total = self.get_total_percent(exclude_row=None)

        self.lbl_total_percent.config(text=f"Summe: {total:.0f}%")

        if total == 100:
            self.lbl_total_percent.config(bootstyle="success")
            self.btn_calc.config(bootstyle="success", state="normal")
        else:
            self.lbl_total_percent.config(bootstyle="danger")
            self.btn_calc.config(bootstyle="secondary")

    def calculate(self):
        # 1. PRÜFUNG: 100% Summe
        total_percent = self.get_total_percent()
        if abs(total_percent - 100.0) > 0.1:
            messagebox.showerror("Fehler",
                                 f"Die Summe der Anteile muss exakt 100% sein.\nAktuell: {total_percent:.0f}%")
            return

        try:
            total_area = float(self.entry_total_area.get().replace(",", "."))
            price = float(self.entry_price.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Fehler", "Bitte gültige Gesamtfläche und Preis eingeben.")
            return

        sum_V = 0.0
        sum_kW = 0.0
        sum_kWh = 0.0

        vp, eta_total, DPZu, DPAbl = 25, 0.8 * 0.9 * 0.99, 1200, 750

        # 2. PRÜFUNG: Plausibilität der Werte
        for i, r in enumerate(self.rows):
            v = r.get_values()

            # Nur prüfen wenn die Zeile auch aktiv ist (Prozent > 0)
            if v["percent"] > 0:
                # Regel: Tage max 365
                if v["d"] > 365:
                    messagebox.showerror("Ungültiger Wert",
                                         f"Fehler in Zeile {i + 1} ({v['typ']}):\n\nTage pro Jahr dürfen maximal 365 sein.")
                    return  # Abbruch

                # Regel: Stunden max 24
                if v["h"] > 24:
                    messagebox.showerror("Ungültiger Wert",
                                         f"Fehler in Zeile {i + 1} ({v['typ']}):\n\nStunden pro Tag dürfen maximal 24 sein.")
                    return

                # Regel: Keine negativen Werte
                if v["h"] < 0 or v["d"] < 0 or v["pers"] < 0 or v["lw"] < 0:
                    messagebox.showerror("Ungültiger Wert",
                                         f"Fehler in Zeile {i + 1}:\n\nBitte keine negativen Zahlen eingeben.")
                    return

                # --- BERECHNUNG ---
                part_area = total_area * (v["percent"] / 100.0)
                V_pers = v["pers"] * vp
                V_flaeche = part_area * (v["lw"] * 1.2)

                V_part = max(V_pers, V_flaeche)

                Q_zu = (DPZu * V_part / 3600) / eta_total
                Q_ab = (DPAbl * V_part / 3600) / eta_total
                Q_part_kw = (Q_zu + Q_ab) / 1000

                E_part = Q_part_kw * v["h"] * v["d"]

                sum_V += V_part
                sum_kW += Q_part_kw
                sum_kWh += E_part

        total_cost = sum_kWh * price

        self.res_luft.config(text=f"{sum_V:,.0f} m³/h".replace(",", "."))
        self.res_kw.config(text=f"{sum_kW:,.2f} kW")
        self.res_kwh.config(text=f"{sum_kWh:,.0f} kWh/a".replace(",", "."))
        self.res_euro.config(text=f"{total_cost:,.2f} €")


if __name__ == "__main__":
    app_window = ttk.Window(themename="cosmo")
    app = VentilationApp(app_window)
    app_window.mainloop()