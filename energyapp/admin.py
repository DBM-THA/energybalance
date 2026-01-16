from django.contrib import admin

from .models import Building, GwpManufacturing, GwpCompensation


# ---------- Inline: GWP Herstellung direkt im Building ----------
class GwpManufacturingInline(admin.StackedInline):
    model = GwpManufacturing
    extra = 0
    max_num = 1
    can_delete = False

    # readonly: wenn total_* noch nicht existiert, ignorieren wir sie unten per try/except nicht,
    # daher lassen wir hier nur die Felder, die sicher existieren:
    readonly_fields = ("new_per_year", "existing_per_year")


# ---------- Building Admin (dein bestehender Admin + Inline) ----------
@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    # Spalten in der Übersicht
    list_display = (
        "name",
        "floor_area_display",
        "result_Q_h_display",
        "degree_days",
    )
    search_fields = ("name",)
    list_filter = ("degree_days",)

    # Ergebnisfelder sollen nur angezeigt, nicht geändert werden
    readonly_fields = (
        "result_Q_T",
        "result_Q_V",
        "result_Q_I",
        "result_Q_S",
        "result_Q_h",
        "result_H_T",
        "result_H_V",
        "result_floor_area",
        "result_roof_area",
        "result_opaque_wall_area",
        "result_window_area",
        "result_Q_S_n",
        "result_Q_S_e",
        "result_Q_S_s",
        "result_Q_S_w",
        "result_Q_PV_total",
        "result_Q_PV_on",
        "result_Q_PV_off",
    )

    # Gruppierung wie im Formular
    fieldsets = (
        ("Allgemein", {"fields": ("name",)}),
        (
            "Geometrie",
            {
                "fields": (
                    "length_ns",
                    "width_ow",
                    "storeys",
                    "room_height",
                )
            },
        ),
        (
            "Bauteile – U-Werte",
            {
                "fields": (
                    "u_wall",
                    "u_roof",
                    "u_floor",
                    "u_window",
                )
            },
        ),
        (
            "Fensterflächen [%]",
            {
                "fields": (
                    "window_share_n",
                    "window_share_e",
                    "window_share_s",
                    "window_share_w",
                )
            },
        ),
        (
            "Solare Gewinne – g-Werte",
            {
                "fields": (
                    "g_n",
                    "g_e",
                    "g_s",
                    "g_w",
                )
            },
        ),
        (
            "Innere Gewinne",
            {
                "fields": (
                    "person_density",
                    "persons",
                )
            },
        ),
        (
            "Lüftung & Klima",
            {
                "fields": (
                    "air_change_rate",
                    "degree_days",
                    "setpoint_temp",
                )
            },
        ),
        (
            "PV-Anlage",
            {
                "fields": (
                    "pv_roof_share",
                    "pv_specific_yield",
                    "pv_self_consumption_share",
                )
            },
        ),
        (
            "Berechnungsergebnisse",
            {
                "fields": (
                    "result_floor_area",
                    "result_roof_area",
                    "result_opaque_wall_area",
                    "result_window_area",
                    "result_H_T",
                    "result_H_V",
                    "result_Q_T",
                    "result_Q_V",
                    "result_Q_I",
                    "result_Q_S",
                    "result_Q_h",
                    "result_Q_S_n",
                    "result_Q_S_e",
                    "result_Q_S_s",
                    "result_Q_S_w",
                    "result_Q_PV_total",
                    "result_Q_PV_on",
                    "result_Q_PV_off",
                )
            },
        ),
    )

    # ✅ HIER: Inline einbauen
    inlines = [GwpManufacturingInline]

    # kleine Helfer für Liste
    def floor_area_display(self, obj):
        if obj.result_floor_area is None:
            return "-"
        return f"{obj.result_floor_area:.1f}"

    floor_area_display.short_description = "Grundfläche [m²]"

    def result_Q_h_display(self, obj):
        if obj.result_Q_h is None:
            return "-"
        return f"{obj.result_Q_h:.0f}"

    result_Q_h_display.short_description = "Q_h [kWh/a]"


# ---------- GWP Herstellung Admin Liste ----------
@admin.register(GwpManufacturing)
class GwpManufacturingAdmin(admin.ModelAdmin):
    list_display = (
        "building",
        "new_components_gwp",
        "existing_components_gwp",
        "service_life_years",
        "new_per_year",
        "existing_per_year",
    )
    list_select_related = ("building",)
    readonly_fields = ("new_per_year", "existing_per_year")


# ---------- GWP Kompensation Admin Liste ----------
@admin.register(GwpCompensation)
class GwpCompensationAdmin(admin.ModelAdmin):
    list_display = ("building",)
    list_select_related = ("building",)
