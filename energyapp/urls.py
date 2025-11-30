from django.urls import path
from .views import building_viewspy

urlpatterns = [
    path("", building_viewspy.dashboard, name="dashboard"),
    path("calculator/", building_viewspy.building_create, name="building_create"),

    path("buildings/", building_viewspy.building_list, name="building_list"),
    path("buildings/<int:pk>/", building_viewspy.building_detail, name="building_detail"),
    path("buildings/<int:pk>/edit/", building_viewspy.building_edit, name="building_edit"),
    path("buildings/<int:pk>/delete/", building_viewspy.building_delete, name="building_delete"),
    path("buildings/delete_all/", building_viewspy.building_delete_all, name="building_delete_all"),

    path("buildings/export/csv/", building_viewspy.building_export_csv, name="building_export_csv"),
    path("buildings/export/xlsx/", building_viewspy.building_export_xlsx, name="building_export_xlsx"),
    path("buildings/export/pdf/", building_viewspy.building_export_pdf, name="building_export_pdf"),
    path("buildings/<int:pk>/result/pdf/", building_viewspy.building_result_pdf, name="building_result_pdf"),
]
