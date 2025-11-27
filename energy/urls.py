from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("calculator/", views.building_create, name="building_create"),

    path("buildings/", views.building_list, name="building_list"),
    path("buildings/<int:pk>/", views.building_detail, name="building_detail"),
    path("buildings/<int:pk>/edit/", views.building_edit, name="building_edit"),
    path("buildings/<int:pk>/delete/", views.building_delete, name="building_delete"),
    path("buildings/delete_all/", views.building_delete_all, name="building_delete_all"),

    path("buildings/export/csv/", views.building_export_csv, name="building_export_csv"),
    path("buildings/export/xlsx/", views.building_export_xlsx, name="building_export_xlsx"),
    path("buildings/export/pdf/", views.building_export_pdf, name="building_export_pdf"),
    path("buildings/<int:pk>/result/pdf/", views.building_result_pdf, name="building_result_pdf"),
]
