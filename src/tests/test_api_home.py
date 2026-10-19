from django.test import SimpleTestCase


class APIHomeTests(SimpleTestCase):
    def test_homepage_returns_api_directory(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
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
            },
        )
