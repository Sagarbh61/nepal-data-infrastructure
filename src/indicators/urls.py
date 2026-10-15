
from django.urls import path

from indicators.views import (
    IndicatorDetailView,
    IndicatorListView,
    IndicatorObservationListView,
)

urlpatterns = [
    path(
        "indicators/",
        IndicatorListView.as_view(),
        name="indicator-list",
    ),
    path(
        "indicators/<str:code>/",
        IndicatorDetailView.as_view(),
        name="indicator-detail",
    ),
    path(
        "observations/",
        IndicatorObservationListView.as_view(),
        name="observation-list",
    ),
]
