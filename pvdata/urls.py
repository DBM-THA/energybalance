
from django.urls import path
from .views import pv_calculator
from .preset_api import pv_preset

urlpatterns = [
    path("", pv_calculator, name="pv_calculator"),     # /pv/
    path("preset/<int:pk>/", pv_preset, name="pv_preset"),  # /pv/preset/1/
]