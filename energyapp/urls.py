from django.urls import path
from .views import building_view
from .views import summer_steps as summer_steps_views
from .views import summer as summer_views
from energyapp.views.gwp_manufacturing_view import gwp_manufacturing_edit
from energyapp.views.gwp_overview import gwp_overview
from energyapp.views.gwp_compensation_view import gwp_compensation_edit
from .views.load_profile import energy_balance_view
urlpatterns = [
    path("", building_view.dashboard, name="dashboard"),
    path("calculator/", building_view.building_create_detailed, name="building_create"),
    path("calculator/detailed/", building_view.building_create_detailed, name="calculator_detailed"),
    path("buildings/", building_view.building_list, name="building_list"),
    path("buildings/<int:pk>/", building_view.building_detail, name="building_detail"),
    path("buildings/<int:pk>/edit/", building_view.building_edit, name="building_edit"),
    path("buildings/<int:pk>/delete/", building_view.building_delete, name="building_delete"),
    path("buildings/delete_all/", building_view.building_delete_all, name="building_delete_all"),
    path("buildings/export/csv/", building_view.building_export_csv, name="building_export_csv"),
    path("buildings/export/xlsx/", building_view.building_export_xlsx, name="building_export_xlsx"),
    path("buildings/export/pdf/", building_view.building_export_pdf, name="building_export_pdf"),
    path("buildings/<int:pk>/result/pdf/", building_view.building_result_pdf, name="building_result_pdf"),
    path("buildings/<int:pk>/summer/", summer_steps_views.summer_step1, name="summer"),
    path("buildings/<int:pk>/summer/step1/", summer_steps_views.summer_step1, name="summer_step1"),
    path("buildings/<int:pk>/summer/step2/", summer_steps_views.summer_step2, name="summer_step2"),
    path("summer/fc-info/", summer_views.fc_info, name="fc_info"),
    path("summary-dashboard/", building_view.summary_dashboard, name="summary_dashboard"),
    path("internal-gains/", building_view.internal_gains, name="internal_gains"),
    path(
        "buildings/<int:building_id>/gwp/",
        gwp_overview,
        name="gwp_overview",
    ),
    path(
        "buildings/<int:building_id>/gwp/herstellung/",
        gwp_manufacturing_edit,
        name="gwp_manufacturing_edit",
    ),
    path(
        "buildings/<int:building_id>/gwp/kompensation/",
        gwp_compensation_edit,
        name="gwp_compensation_edit",
    ),
    path("envelope/", building_view.envelope_detail, name="envelope_detail"),
    path("solar-gains/", building_view.solar_gains, name="solar_gains"),
    path('building/<int:pk>/bilanz/', energy_balance_view, name='energy_balance'),

    path("pv-details/", building_view.pv_details, name="pv_details"),
    path("ventilation/", building_view.ventilation, name="ventilation"),
]
