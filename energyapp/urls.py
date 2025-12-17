from django.urls import path
from .views import building_view
from .views import summer as summer_views

urlpatterns = [
    path("", building_view.dashboard, name="dashboard"),
    path("calculator/", building_view.building_create_simple, name="building_create"),
    path("calculator/simple/", building_view.building_create_simple, name="calculator_simple"),
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
    path("summer/", summer_views.summer_view, name="summer"),
    path("summer/step1/", summer_steps_views.summer_step1, name="summer_step1"),
    path("summer/step2/", summer_steps_views.summer_step2, name="summer_step2"),
]
