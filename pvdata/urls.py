from django.urls import path
from .views import pv_details

urlpatterns = [
    path("details/", pv_details, name="pv_details"),
]
