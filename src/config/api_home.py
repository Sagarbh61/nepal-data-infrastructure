
from django.http import JsonResponse


def api_home(request):
    return JsonResponse(
        {
            "name": "Nepal Data Infrastructure API",
            "status": "online",
            "endpoints": {
                "population": "/api/population/",
                "indicators": "/api/indicators/",
                "wbes_business_obstacles": (
                    "/api/wbes/business-obstacles/"
                ),
                "wbes_metadata": "/api/wbes/metadata/",
            },
        }
    )
