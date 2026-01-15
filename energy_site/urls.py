from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    path("", lambda request: redirect("/pv/")),
    path("admin/", admin.site.urls),
    path("", include("energyapp.urls")),
    path("pv/", include("pvdata.urls")),

]
path("", include("energyapp.urls")),

from django.urls import path, include



