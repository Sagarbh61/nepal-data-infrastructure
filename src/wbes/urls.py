
from django.urls import path

from wbes.views import (
    WBESBusinessObstacleListView,
    WBESMetadataView,
)

urlpatterns = [
    path(
        "business-obstacles/",
        WBESBusinessObstacleListView.as_view(),
        name="wbes-business-obstacles",
    ),
    path(
        "metadata/",
        WBESMetadataView.as_view(),
        name="wbes-metadata",
    ),
]
