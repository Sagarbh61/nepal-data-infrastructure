
import csv
from pathlib import Path

from rest_framework import generics
from rest_framework.exceptions import APIException

from wbes.serializers import WBESObstacleSerializer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

WBES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "wbes_2023"
    / "business_obstacles.csv"
)


class WBESDataUnavailable(APIException):
    status_code = 500
    default_detail = "The processed WBES dataset is unavailable or invalid."
    default_code = "wbes_data_unavailable"


class WBESBusinessObstacleListView(generics.ListAPIView):
    serializer_class = WBESObstacleSerializer

    def get_queryset(self):
        if not WBES_FILE.is_file():
            raise WBESDataUnavailable()

        try:
            with WBES_FILE.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as file:
                reader = csv.DictReader(file)

                required_columns = set(
                    WBESObstacleSerializer().fields.keys()
                )

                if (
                    reader.fieldnames is None
                    or not required_columns.issubset(reader.fieldnames)
                ):
                    raise WBESDataUnavailable()

                records = list(reader)

        except (OSError, UnicodeError, csv.Error):
            raise WBESDataUnavailable()

        if not records:
            raise WBESDataUnavailable()

        serializer = self.get_serializer(data=records, many=True)

        if not serializer.is_valid():
            raise WBESDataUnavailable()

        return serializer.validated_data


from rest_framework.views import APIView
from rest_framework.response import Response


class WBESMetadataView(APIView):
    def get(self, request):
        metadata = {
            "survey": "World Bank Enterprise Survey, Nepal 2023",
            "survey_period": "May–August 2023",
            "population_covered": (
                "Eligible formal-sector establishments with at least "
                "5 employees, subject to the survey's sector and "
                "ownership eligibility criteria."
            ),
            "measure": (
                "Share of valid responses rating a business obstacle "
                "as a major or severe constraint."
            ),
            "weighting": {
                "primary_weight": "wmedian",
                "weighted_share": (
                    "Uses the survey's wmedian sampling weight."
                ),
                "unweighted_share": (
                    "Uses valid responses without sampling weights."
                ),
            },
            "limitations": [
                (
                    "The results do not represent every business "
                    "in Nepal."
                ),
                (
                    "The figures measure reported perceptions, "
                    "not causal effects on business performance."
                ),
(
    "Missing ratings and special response codes, including "
    "not applicable (-7) and don't know (-9), are excluded. "
    "The excluded count combines these categories."
)
            ],
        }

        return Response(metadata)
