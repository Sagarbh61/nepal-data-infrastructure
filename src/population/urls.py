from django.urls import path

from population.views import LocalGovernmentPopulationListView

urlpatterns = [
path(
  "",
  LocalGovernmentPopulationListView.as_view(), name="population-list"
),

]