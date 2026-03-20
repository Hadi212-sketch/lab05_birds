import unittest

import httpx

from bird_api_client import BirdAPIClient, BirdAPIError
from gradio_app import (
    build_bird_choices,
    build_birds_dataframe,
    build_sightings_dataframe,
    build_species_choices,
    build_species_dataframe,
    build_species_lookup,
    format_bird_label,
    format_species_label,
    format_timestamp,
    normalize_filter,
)


class BirdAPIClientTests(unittest.TestCase):
    def make_client(self, handler):
        return BirdAPIClient(
            base_url="http://testserver",
            transport=httpx.MockTransport(handler),
        )

    def test_list_species_passes_filter_params(self):
        def handler(request):
            self.assertEqual(request.method, "GET")
            self.assertEqual(request.url.path, "/species/")
            self.assertEqual(
                dict(request.url.params),
                {
                    "conservation_status": "Least Concern",
                    "offset": "0",
                    "limit": "1000",
                },
            )
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 1,
                        "name": "Puffin",
                        "scientific_name": "Fratercula arctica",
                        "family": "Alcidae",
                        "conservation_status": "Least Concern",
                        "wingspan_cm": 53,
                    }
                ],
            )

        client = self.make_client(handler)
        result = client.list_species(conservation_status="Least Concern")
        self.assertEqual(result[0]["name"], "Puffin")

    def test_create_bird_raises_clean_error_message(self):
        def handler(request):
            self.assertEqual(request.method, "POST")
            self.assertEqual(request.url.path, "/birds/")
            return httpx.Response(409, json={"detail": "Ring code already exists"})

        client = self.make_client(handler)
        with self.assertRaises(BirdAPIError) as context:
            client.create_bird(
                {
                    "nickname": "Skipper",
                    "ring_code": "AB-1234",
                    "age": 2,
                    "species_id": 1,
                }
            )

        self.assertEqual(str(context.exception), "Ring code already exists")


class GradioFormattingTests(unittest.TestCase):
    def setUp(self):
        self.species = [
            {
                "id": 1,
                "name": "Puffin",
                "scientific_name": "Fratercula arctica",
                "family": "Alcidae",
                "conservation_status": "Vulnerable",
                "wingspan_cm": 53,
            },
            {
                "id": 2,
                "name": "Barn Owl",
                "scientific_name": "Tyto alba",
                "family": "Tytonidae",
                "conservation_status": "Least Concern",
                "wingspan_cm": 95,
            },
        ]
        self.birds = [
            {
                "id": 1,
                "nickname": "Skipper",
                "ring_code": "PUF-001",
                "age": 3,
                "species_id": 1,
            },
            {
                "id": 2,
                "nickname": "Ghost",
                "ring_code": "OWL-001",
                "age": 4,
                "species_id": 2,
            },
        ]
        self.sightings = [
            {
                "id": 5,
                "bird_id": 1,
                "spotted_at": "2026-03-05T14:14:14",
                "location": "Cliffs of Moher",
                "observer_name": "Marty",
                "notes": "Feeding on some fishes.",
            }
        ]

    def test_filter_normalization(self):
        self.assertIsNone(normalize_filter("All"))
        self.assertIsNone(normalize_filter(""))
        self.assertEqual(normalize_filter("Least Concern"), "Least Concern")

    def test_species_label_and_choices(self):
        self.assertEqual(
            format_species_label(self.species[0]),
            "Puffin (Fratercula arctica)",
        )
        self.assertEqual(
            build_species_choices(self.species),
            [
                ("Puffin (Fratercula arctica)", 1),
                ("Barn Owl (Tyto alba)", 2),
            ],
        )

    def test_species_dataframe_has_expected_columns(self):
        dataframe = build_species_dataframe(self.species)
        self.assertEqual(
            list(dataframe.columns),
            [
                "id",
                "name",
                "scientific_name",
                "family",
                "conservation_status",
                "wingspan_cm",
            ],
        )
        self.assertEqual(dataframe.iloc[0]["wingspan_cm"], 53.0)

    def test_birds_dataframe_uses_species_names(self):
        species_lookup = build_species_lookup(self.species)
        self.assertEqual(
            format_bird_label(self.birds[0], species_lookup),
            "Skipper [PUF-001] - Puffin",
        )
        self.assertEqual(
            build_bird_choices(self.birds, species_lookup),
            [
                ("Skipper [PUF-001] - Puffin", 1),
                ("Ghost [OWL-001] - Barn Owl", 2),
            ],
        )
        dataframe = build_birds_dataframe(self.birds, species_lookup)
        self.assertEqual(dataframe.iloc[1]["species"], "Barn Owl")

    def test_sightings_dataframe_contains_related_labels(self):
        species_lookup = build_species_lookup(self.species)
        bird_lookup = {item["id"]: item for item in self.birds}
        dataframe = build_sightings_dataframe(
            self.sightings, bird_lookup, species_lookup
        )
        self.assertEqual(dataframe.iloc[0]["bird"], "Skipper")
        self.assertEqual(dataframe.iloc[0]["species"], "Puffin")
        self.assertEqual(dataframe.iloc[0]["spotted_at"], "2026-03-05 14:14:14")

    def test_timestamp_formatting_is_human_readable(self):
        self.assertEqual(
            format_timestamp("2026-03-20T07:30:00"),
            "2026-03-20 07:30:00",
        )


if __name__ == "__main__":
    unittest.main()
