from django.urls import path
from .views import pv_calculator, pv_compute_api

urlpatterns = [
    path("", pv_calculator, name="pv_calculator"),               # /pv/
    path("api/compute/", pv_compute_api, name="pv_compute_api"), # /pv/api/compute/
]
