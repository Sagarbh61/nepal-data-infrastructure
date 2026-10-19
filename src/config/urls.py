
"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import include, path

from config.api_home import api_home

urlpatterns = [
    path("", api_home, name="api-home"),
    path("admin/", admin.site.urls),
    path("api/population/", include("population.urls")),
    path("api/", include("indicators.urls")),
    path("api/wbes/", include("wbes.urls")),
]
