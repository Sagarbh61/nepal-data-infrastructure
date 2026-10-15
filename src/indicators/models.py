from django.db import models

# Create your models here.

class Indicator(models.Model):
  code = models.CharField(max_length=50, unique=True)
  name = models.CharField(max_length=255)
  source = models.CharField(max_length=100, default="World Development Indicators")

  class Meta:
    ordering = ["code"]

  def __str__(self):
    return f"{self.code}: {self.name}"

class IndicatorObservation(models.Model):
  indicator = models.ForeignKey(Indicator, on_delete=models.PROTECT, related_name="observations")
  country_code = models.CharField(max_length=3)
  year = models.PositiveSmallIntegerField()
  value = models.DecimalField(
    max_digits=43,
    decimal_places=29,
    null=True,
    blank=True,
)

  class Meta:
    ordering = ["country_code", "indicator__code", "year"]
    constraints = [
      models.UniqueConstraint(
        fields=["indicator", "country_code", "year"],
        name="unique_indicator_country_year",
      ),
      models.CheckConstraint(
        condition=models.Q(year__gte=1960, year__lte=2100),
        name="valid_indicator_observation_year",
      ),
    ]

  def __str__(self):
    return f"{self.indicator.code} - {self.country_code} - {self.year}"