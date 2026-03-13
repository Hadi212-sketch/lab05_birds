"""
Automated test script for Lab 05 Birds API.
Run with: python test_api.py
Make sure FastAPI is running first: fastapi dev main.py
"""

import requests
import sys

BASE = "http://127.0.0.1:8000"
passed = 0
failed = 0


def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name} — {detail}")
        failed += 1


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ------------------------------------------------------------------
section("1. ROOT ENDPOINT")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/")
test("GET / returns 200", r.status_code == 200)
test("GET / returns Hello World", r.json().get("message") == "Hello World")

# ------------------------------------------------------------------
section("2. DOCS ENDPOINTS")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/docs")
test("GET /docs returns 200", r.status_code == 200)
r = requests.get(f"{BASE}/redoc")
test("GET /redoc returns 200", r.status_code == 200)

# ------------------------------------------------------------------
section("3. POST SPECIES (create 4)")
# ------------------------------------------------------------------
species_data = [
    {"name": "House Sparrow", "scientific_name": "Passer domesticus", "family": "Passeridae", "conservation_status": "Least Concern", "wingspan_cm": 21.0},
    {"name": "European Robin", "scientific_name": "Erithacus rubecula", "family": "Muscicapidae", "conservation_status": "Least Concern", "wingspan_cm": 22.5},
    {"name": "Barn Owl", "scientific_name": "Tyto alba", "family": "Tytonidae", "conservation_status": "Least Concern", "wingspan_cm": 95.0},
    {"name": "White Stork", "scientific_name": "Ciconia ciconia", "family": "Ciconiidae", "conservation_status": "Least Concern", "wingspan_cm": 195.0},
]
species_ids = []
for s in species_data:
    r = requests.post(f"{BASE}/species/", json=s)
    test(f"POST /species/ — {s['name']}", r.status_code == 201, f"got {r.status_code}: {r.text}")
    if r.status_code == 201:
        species_ids.append(r.json()["id"])

# ------------------------------------------------------------------
section("4. GET SPECIES")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/species/")
test("GET /species/ returns 200", r.status_code == 200)
test("GET /species/ returns 4 species", len(r.json()) == 4, f"got {len(r.json())}")

r = requests.get(f"{BASE}/species/{species_ids[0]}")
test(f"GET /species/{species_ids[0]} returns 200", r.status_code == 200)
test("GET /species/{{id}} includes birds list", "birds" in r.json(), f"keys: {list(r.json().keys())}")

r = requests.get(f"{BASE}/species/99999")
test("GET /species/99999 returns 404", r.status_code == 404)

# ------------------------------------------------------------------
section("5. FILTER SPECIES")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/species/", params={"conservation_status": "Least Concern"})
test("Filter by conservation_status=Least Concern", len(r.json()) == 4, f"got {len(r.json())}")

r = requests.get(f"{BASE}/species/", params={"conservation_status": "Endangered"})
test("Filter by conservation_status=Endangered returns empty", len(r.json()) == 0, f"got {len(r.json())}")

# ------------------------------------------------------------------
section("6. PAGINATE SPECIES")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/species/", params={"offset": 0, "limit": 2})
test("Pagination offset=0 limit=2 returns 2", len(r.json()) == 2, f"got {len(r.json())}")

r = requests.get(f"{BASE}/species/", params={"offset": 2, "limit": 2})
test("Pagination offset=2 limit=2 returns 2", len(r.json()) == 2, f"got {len(r.json())}")

r = requests.get(f"{BASE}/species/", params={"offset": 10, "limit": 2})
test("Pagination offset=10 returns empty", len(r.json()) == 0, f"got {len(r.json())}")

# ------------------------------------------------------------------
section("7. POST BIRDS (create 4)")
# ------------------------------------------------------------------
birds_data = [
    {"nickname": "Pip", "ring_code": "SPARROW-001", "age": 2, "species_id": species_ids[0]},
    {"nickname": "Rusty", "ring_code": "ROBIN-001", "age": 1, "species_id": species_ids[1]},
    {"nickname": "Ghost", "ring_code": "OWL-001", "age": 4, "species_id": species_ids[2]},
    {"nickname": "Cloud", "ring_code": "STORK-001", "age": 6, "species_id": species_ids[3]},
]
bird_ids = []
for b in birds_data:
    r = requests.post(f"{BASE}/birds/", json=b)
    test(f"POST /birds/ — {b['nickname']}", r.status_code == 201, f"got {r.status_code}: {r.text}")
    if r.status_code == 201:
        bird_ids.append(r.json()["id"])

# ------------------------------------------------------------------
section("8. GET BIRDS")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/birds/")
test("GET /birds/ returns 200", r.status_code == 200)
test("GET /birds/ returns 4 birds", len(r.json()) == 4, f"got {len(r.json())}")

r = requests.get(f"{BASE}/birds/{bird_ids[0]}")
test(f"GET /birds/{bird_ids[0]} returns 200", r.status_code == 200)
test("GET /birds/{{id}} includes species object", "species" in r.json(), f"keys: {list(r.json().keys())}")
test("Species object has correct name", r.json().get("species", {}).get("name") == "House Sparrow", f"got {r.json().get('species')}")

# ------------------------------------------------------------------
section("9. BIRD VALIDATION — negative age")
# ------------------------------------------------------------------
r = requests.post(f"{BASE}/birds/", json={"nickname": "Bad", "ring_code": "BAD-001", "age": -5, "species_id": species_ids[0]})
test("POST bird with age=-5 returns 422", r.status_code == 422, f"got {r.status_code}")

# ------------------------------------------------------------------
section("10. BIRD VALIDATION — invalid species_id")
# ------------------------------------------------------------------
r = requests.post(f"{BASE}/birds/", json={"nickname": "Fake", "ring_code": "FAKE-001", "age": 1, "species_id": 99999})
test("POST bird with species_id=99999 returns 500 (FK violation)", r.status_code == 500, f"got {r.status_code}")

# ------------------------------------------------------------------
section("11. FILTER BIRDS")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/birds/", params={"species_id": species_ids[0]})
test(f"Filter by species_id={species_ids[0]}", len(r.json()) == 1, f"got {len(r.json())}")
test("Filtered bird is Pip", r.json()[0]["nickname"] == "Pip", f"got {r.json()[0].get('nickname')}")

# ------------------------------------------------------------------
section("12. PAGINATE BIRDS")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/birds/", params={"offset": 0, "limit": 2})
test("Pagination offset=0 limit=2 returns 2", len(r.json()) == 2, f"got {len(r.json())}")

# ------------------------------------------------------------------
section("13. BACK-REFERENCE: species with birds")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/species/{species_ids[0]}")
test("GET /species/{{id}} returns birds list", len(r.json().get("birds", [])) == 1, f"got {r.json().get('birds')}")
test("Bird in list is Pip", r.json()["birds"][0]["nickname"] == "Pip")

r = requests.get(f"{BASE}/species/{species_ids[0]}/birds")
test("GET /species/{{id}}/birds returns 200", r.status_code == 200)
test("GET /species/{{id}}/birds returns 1 bird", len(r.json()) == 1, f"got {len(r.json())}")

# ------------------------------------------------------------------
section("14. POST BIRDSPOTTING (create 5)")
# ------------------------------------------------------------------
spottings_data = [
    {"bird_id": bird_ids[0], "spotted_at": "2026-03-01T08:15:00", "location": "Brussels Park", "observer_name": "Nina Peeters", "notes": "Seen near the fountain"},
    {"bird_id": bird_ids[0], "spotted_at": "2026-03-02T09:40:00", "location": "Ghent Riverside", "observer_name": "Lars Mertens", "notes": "Feeding on breadcrumbs"},
    {"bird_id": bird_ids[1], "spotted_at": "2026-03-02T07:55:00", "location": "Antwerp Zoo Garden", "observer_name": "Emma Janssens", "notes": "Singing from a low branch"},
    {"bird_id": bird_ids[2], "spotted_at": "2026-03-03T21:10:00", "location": "Ardennes Forest Edge", "observer_name": "Tom Wouters", "notes": "Hunting at dusk"},
    {"bird_id": bird_ids[3], "spotted_at": "2026-03-04T12:25:00", "location": "Leuven Wetlands", "observer_name": "Sofie Claes", "notes": "Resting close to the marsh"},
]
spotting_ids = []
for sp in spottings_data:
    r = requests.post(f"{BASE}/birdspotting/", json=sp)
    test(f"POST /birdspotting/ — {sp['location']}", r.status_code == 201, f"got {r.status_code}: {r.text}")
    if r.status_code == 201:
        spotting_ids.append(r.json()["id"])

# ------------------------------------------------------------------
section("15. GET BIRDSPOTTING")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/birdspotting/")
test("GET /birdspotting/ returns 200", r.status_code == 200)
test("GET /birdspotting/ returns 5 records", len(r.json()) == 5, f"got {len(r.json())}")

r = requests.get(f"{BASE}/birdspotting/{spotting_ids[0]}")
test(f"GET /birdspotting/{spotting_ids[0]} returns 200", r.status_code == 200)
test("GET /birdspotting/{{id}} includes bird object", "bird" in r.json(), f"keys: {list(r.json().keys())}")

# ------------------------------------------------------------------
section("16. FILTER BIRDSPOTTING")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/birdspotting/", params={"observer_name": "Nina Peeters"})
test("Filter by observer_name=Nina Peeters", len(r.json()) == 1, f"got {len(r.json())}")

r = requests.get(f"{BASE}/birdspotting/", params={"observer_name": "Nobody"})
test("Filter by observer_name=Nobody returns empty", len(r.json()) == 0, f"got {len(r.json())}")

# ------------------------------------------------------------------
section("17. PAGINATE BIRDSPOTTING")
# ------------------------------------------------------------------
r = requests.get(f"{BASE}/birdspotting/", params={"offset": 0, "limit": 2})
test("Pagination offset=0 limit=2 returns 2", len(r.json()) == 2, f"got {len(r.json())}")

# ------------------------------------------------------------------
section("18. PUT — UPDATE")
# ------------------------------------------------------------------
r = requests.put(f"{BASE}/species/{species_ids[0]}", json={
    "name": "House Sparrow (Updated)", "scientific_name": "Passer domesticus",
    "family": "Passeridae", "conservation_status": "Near Threatened", "wingspan_cm": 21.5
})
test("PUT /species/ returns 200", r.status_code == 200)
test("Species name updated", r.json()["name"] == "House Sparrow (Updated)")

r = requests.put(f"{BASE}/birds/{bird_ids[0]}", json={
    "nickname": "Pip (Updated)", "ring_code": "SPARROW-001", "age": 3, "species_id": species_ids[0]
})
test("PUT /birds/ returns 200", r.status_code == 200)
test("Bird nickname updated", r.json()["nickname"] == "Pip (Updated)")

r = requests.put(f"{BASE}/birdspotting/{spotting_ids[0]}", json={
    "bird_id": bird_ids[0], "spotted_at": "2026-03-01T10:00:00",
    "location": "Brussels Park (Updated)", "observer_name": "Nina Peeters", "notes": "Updated note"
})
test("PUT /birdspotting/ returns 200", r.status_code == 200)
test("Spotting location updated", r.json()["location"] == "Brussels Park (Updated)")

# PUT non-existent
r = requests.put(f"{BASE}/species/99999", json={
    "name": "X", "scientific_name": "X", "family": "X", "conservation_status": "X", "wingspan_cm": 1.0
})
test("PUT /species/99999 returns 404", r.status_code == 404)

# ------------------------------------------------------------------
section("19. DELETE — BIRDSPOTTING")
# ------------------------------------------------------------------
r = requests.delete(f"{BASE}/birdspotting/{spotting_ids[-1]}")
test("DELETE /birdspotting/ returns 204", r.status_code == 204)

r = requests.get(f"{BASE}/birdspotting/{spotting_ids[-1]}")
test("Deleted spotting returns 404", r.status_code == 404)

# ------------------------------------------------------------------
section("20. DELETE — CASCADE TEST")
# ------------------------------------------------------------------
# Delete bird_ids[0] (Pip) — should cascade-delete its 2 birdspottings
r = requests.delete(f"{BASE}/birds/{bird_ids[0]}")
test("DELETE /birds/ (Pip) returns 204", r.status_code == 204)

r = requests.get(f"{BASE}/birdspotting/{spotting_ids[0]}")
test("Pip's spotting 1 cascade-deleted (404)", r.status_code == 404)

r = requests.get(f"{BASE}/birdspotting/{spotting_ids[1]}")
test("Pip's spotting 2 cascade-deleted (404)", r.status_code == 404)

# ------------------------------------------------------------------
section("21. DELETE — RESTRICT TEST")
# ------------------------------------------------------------------
# Try deleting species that still has birds → should fail
r = requests.delete(f"{BASE}/species/{species_ids[1]}")
test("DELETE species with birds returns 500 (RESTRICT)", r.status_code == 500, f"got {r.status_code}")

# ------------------------------------------------------------------
section("22. DELETE — SPECIES (clean up)")
# ------------------------------------------------------------------
# Delete bird first, then species
r = requests.delete(f"{BASE}/birds/{bird_ids[1]}")
test("DELETE bird Rusty returns 204", r.status_code == 204)

r = requests.delete(f"{BASE}/species/{species_ids[1]}")
test("DELETE species (no birds) returns 204", r.status_code == 204)

# Delete non-existent
r = requests.delete(f"{BASE}/species/99999")
test("DELETE /species/99999 returns 404", r.status_code == 404)


# ==================================================================
print(f"\n{'='*60}")
print(f"  RESULTS: {passed} passed, {failed} failed, {passed+failed} total")
print(f"{'='*60}")

if failed > 0:
    sys.exit(1)
else:
    print("\n  🎉 ALL TESTS PASSED — assignment is 100% working!\n")
    sys.exit(0)
