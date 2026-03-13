# Lab 05 — Birds API: Complete Testing & Verification Guide

This is a step-by-step walkthrough to verify that every single part of the assignment works 100%. Follow it top to bottom.

---

## PHASE 1 — Docker & Database Setup

### Step 1: Start Docker Desktop

Open Docker Desktop on your machine. Wait until the bottom-left shows **"Engine running"** (green).

### Step 2: Open a terminal in the project folder

```powershell
cd path\to\lab05_birds
```

### Step 3: Start PostgreSQL + Adminer

```powershell
docker compose -f compose.db.yaml up -d
```

**Verify it works:**

```powershell
docker compose -f compose.db.yaml ps
```

You should see **2 containers** running:

```
NAME                    STATUS
lab05_birds-postgres-1  Up
lab05_birds-adminer-1   Up
```

If you see both as "Up" → ✅ Docker setup works.

### Step 4: Test Adminer connection

1. Open your browser → go to **http://localhost:8080**
2. Fill in:
   - System: **PostgreSQL**
   - Server: **postgres**
   - Username: **user**
   - Password: **password**
   - Database: **bird_api**
3. Click **Login**

If you see the Adminer dashboard with the `bird_api` database → ✅ Adminer works.

> **Troubleshooting:** If "postgres" as server doesn't work from the browser, try **localhost** instead. The `postgres` hostname only works from inside Docker's network (like Adminer). But since Adminer IS in Docker, it should work.

---

## PHASE 2 — SQL Recap (Manual SQL in Adminer)

This verifies Part 4-6 of the assignment (tables, inserts, queries).

### Step 5: Create the tables manually

In Adminer, click **"SQL command"** (left sidebar) and run each of these one at a time:

**Table 1: species**

```sql
CREATE TABLE species (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  scientific_name VARCHAR(255) NOT NULL,
  family VARCHAR(255) NOT NULL,
  conservation_status VARCHAR(255) NOT NULL,
  wingspan_cm NUMERIC(5,2) NOT NULL
);
```

Click **Execute** → you should see "Query executed OK".

**Table 2: birds**

```sql
CREATE TABLE birds (
  id SERIAL PRIMARY KEY,
  nickname VARCHAR(255) NOT NULL,
  ring_code VARCHAR(100) UNIQUE NOT NULL,
  age INTEGER NOT NULL CHECK (age >= 0),
  species_id INTEGER NOT NULL,
  FOREIGN KEY (species_id) REFERENCES species(id) ON DELETE RESTRICT
);
```

Click **Execute** → "Query executed OK".

**Table 3: birdspotting**

```sql
CREATE TABLE birdspotting (
  id SERIAL PRIMARY KEY,
  bird_id INTEGER NOT NULL,
  spotted_at TIMESTAMP NOT NULL,
  location VARCHAR(255) NOT NULL,
  observer_name VARCHAR(255) NOT NULL,
  notes TEXT NULL,
  FOREIGN KEY (bird_id) REFERENCES birds(id) ON DELETE CASCADE
);
```

Click **Execute** → "Query executed OK".

**Verify:** Click on the table names in the left sidebar. You should see all 3 tables: `species`, `birds`, `birdspotting` → ✅ Tables created.

### Step 6: Insert dummy data

Run each INSERT in the SQL command box:

**Species data:**

```sql
INSERT INTO species (name, scientific_name, family, conservation_status, wingspan_cm)
VALUES
  ('House Sparrow', 'Passer domesticus', 'Passeridae', 'Least Concern', 21.00),
  ('European Robin', 'Erithacus rubecula', 'Muscicapidae', 'Least Concern', 22.50),
  ('Barn Owl', 'Tyto alba', 'Tytonidae', 'Least Concern', 95.00),
  ('White Stork', 'Ciconia ciconia', 'Ciconiidae', 'Least Concern', 195.00);
```

**Birds data:**

```sql
INSERT INTO birds (nickname, ring_code, age, species_id)
VALUES
  ('Pip', 'SPARROW-001', 2, 1),
  ('Rusty', 'ROBIN-001', 1, 2),
  ('Ghost', 'OWL-001', 4, 3),
  ('Cloud', 'STORK-001', 6, 4);
```

**Birdspotting data:**

```sql
INSERT INTO birdspotting (bird_id, spotted_at, location, observer_name, notes)
VALUES
  (1, '2026-03-01 08:15:00', 'Brussels Park', 'Nina Peeters', 'Seen near the fountain'),
  (1, '2026-03-02 09:40:00', 'Ghent Riverside', 'Lars Mertens', 'Feeding on breadcrumbs'),
  (2, '2026-03-02 07:55:00', 'Antwerp Zoo Garden', 'Emma Janssens', 'Singing from a low branch'),
  (3, '2026-03-03 21:10:00', 'Ardennes Forest Edge', 'Tom Wouters', 'Hunting at dusk'),
  (4, '2026-03-04 12:25:00', 'Leuven Wetlands', 'Sofie Claes', 'Resting close to the marsh');
```

**Verify:** Click each table in Adminer → click "Select data". You should see:
- `species`: 4 rows → ✅
- `birds`: 4 rows → ✅
- `birdspotting`: 5 rows → ✅

### Step 7: Test the 3 SQL queries

**Query 1 — Species with wingspan > 50, ordered DESC, limit 2:**

```sql
SELECT *
FROM species
WHERE wingspan_cm > 50
ORDER BY wingspan_cm DESC
LIMIT 2;
```

**Expected result:**

| id | name        | wingspan_cm |
|----|-------------|-------------|
| 4  | White Stork | 195.00      |
| 3  | Barn Owl    | 95.00       |

If you get these 2 rows → ✅ Query 1 works.

**Query 2 — Birds with their species (JOIN):**

```sql
SELECT
  b.nickname,
  b.ring_code,
  s.name AS species_name
FROM birds b
JOIN species s ON b.species_id = s.id;
```

**Expected result:**

| nickname | ring_code    | species_name   |
|----------|-------------|----------------|
| Pip      | SPARROW-001 | House Sparrow  |
| Rusty    | ROBIN-001   | European Robin |
| Ghost    | OWL-001     | Barn Owl       |
| Cloud    | STORK-001   | White Stork    |

If you see all 4 rows with correct species names → ✅ Query 2 works.

**Query 3 — Sightings count per bird:**

```sql
SELECT
  b.nickname,
  COUNT(*) AS sighting_count
FROM birdspotting bs
JOIN birds b ON bs.bird_id = b.id
GROUP BY b.id, b.nickname
ORDER BY sighting_count DESC;
```

**Expected result:**

| nickname | sighting_count |
|----------|---------------|
| Pip      | 2             |
| Rusty    | 1             |
| Ghost    | 1             |
| Cloud    | 1             |

If Pip has 2 and the rest have 1 → ✅ Query 3 works.

### Step 8: Drop the manually created tables

Since FastAPI + SQLModel will recreate the tables automatically (via `start_db()`), drop them now so there's no conflict:

```sql
DROP TABLE IF EXISTS birdspotting;
DROP TABLE IF EXISTS birds;
DROP TABLE IF EXISTS species;
```

> **Important:** Drop in this exact order (birdspotting first, then birds, then species) because of the foreign key dependencies.

---

## PHASE 3 — Python & FastAPI Setup

### Step 9: Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> If you get a PowerShell execution policy error, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Your prompt should now show `(venv)` at the beginning → ✅

### Step 10: Install dependencies

```powershell
pip install -r requirements.txt
```

**Verify:**

```powershell
pip list | findstr -i "fastapi sqlmodel psycopg dotenv"
```

You should see all 4 packages with version numbers → ✅

### Step 11: Start the FastAPI server

```powershell
fastapi dev main.py
```

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
```

If no errors and the server starts → ✅ FastAPI base works.

### Step 12: Test root endpoint

Open browser → go to **http://127.0.0.1:8000**

**Expected response:**

```json
{"message": "Hello World"}
```

If you see this → ✅ Root endpoint works.

### Step 13: Open the docs

Go to **http://127.0.0.1:8000/docs**

You should see the Swagger UI with these tag groups:
- **Species** (6 endpoints)
- **Birds** (5 endpoints)
- **Birdspotting** (5 endpoints)
- **Root** (1 endpoint)

If all groups appear with their endpoints → ✅ Documentation works.

---

## PHASE 4 — Test CRUD Operations via /docs

Now test every endpoint using the Swagger UI at http://127.0.0.1:8000/docs.

For each test: click the endpoint → click **"Try it out"** → fill in the body/params → click **"Execute"**.

### Step 14: POST — Create Species

Click **POST /species/** → Try it out → paste this body:

**Species 1:**
```json
{
  "name": "House Sparrow",
  "scientific_name": "Passer domesticus",
  "family": "Passeridae",
  "conservation_status": "Least Concern",
  "wingspan_cm": 21.0
}
```

Click **Execute**.

**Expected:** Response code **201**, body includes `"id": 1` → ✅

**Species 2:**
```json
{
  "name": "European Robin",
  "scientific_name": "Erithacus rubecula",
  "family": "Muscicapidae",
  "conservation_status": "Least Concern",
  "wingspan_cm": 22.5
}
```

**Expected:** Code **201**, `"id": 2` → ✅

**Species 3:**
```json
{
  "name": "Barn Owl",
  "scientific_name": "Tyto alba",
  "family": "Tytonidae",
  "conservation_status": "Least Concern",
  "wingspan_cm": 95.0
}
```

**Expected:** Code **201**, `"id": 3` → ✅

**Species 4:**
```json
{
  "name": "White Stork",
  "scientific_name": "Ciconia ciconia",
  "family": "Ciconiidae",
  "conservation_status": "Least Concern",
  "wingspan_cm": 195.0
}
```

**Expected:** Code **201**, `"id": 4` → ✅

### Step 15: GET — List all species

Click **GET /species/** → Try it out → Execute (leave all params empty).

**Expected:** Code **200**, array with 4 species → ✅

### Step 16: GET — Single species with birds (back-reference)

Click **GET /species/{species_id}** → species_id = `1` → Execute.

**Expected:** Code **200**, body includes `"birds": []` (empty for now, no birds yet) → ✅

### Step 17: POST — Create Birds

Click **POST /birds/** → Try it out:

**Bird 1:**
```json
{
  "nickname": "Pip",
  "ring_code": "SPARROW-001",
  "age": 2,
  "species_id": 1
}
```

**Expected:** Code **201**, `"id": 1` → ✅

**Bird 2:**
```json
{
  "nickname": "Rusty",
  "ring_code": "ROBIN-001",
  "age": 1,
  "species_id": 2
}
```

**Expected:** Code **201**, `"id": 2` → ✅

**Bird 3:**
```json
{
  "nickname": "Ghost",
  "ring_code": "OWL-001",
  "age": 4,
  "species_id": 3
}
```

**Expected:** Code **201**, `"id": 3` → ✅

**Bird 4:**
```json
{
  "nickname": "Cloud",
  "ring_code": "STORK-001",
  "age": 6,
  "species_id": 4
}
```

**Expected:** Code **201**, `"id": 4` → ✅

### Step 18: Verify species→birds back-reference now works

Click **GET /species/{species_id}** → species_id = `1` → Execute.

**Expected:** Code **200**, body now includes:
```json
"birds": [
  {
    "nickname": "Pip",
    "ring_code": "SPARROW-001",
    "age": 2,
    "id": 1,
    "species_id": 1
  }
]
```

If you see the birds array populated → ✅ Back-reference works.

Also test **GET /species/1/birds** → should return the same bird list → ✅

### Step 19: GET — Bird with species details

Click **GET /birds/{bird_id}** → bird_id = `1` → Execute.

**Expected:** Code **200**, body includes:
```json
{
  "nickname": "Pip",
  "ring_code": "SPARROW-001",
  "age": 2,
  "id": 1,
  "species_id": 1,
  "species": {
    "name": "House Sparrow",
    "scientific_name": "Passer domesticus",
    ...
  }
}
```

If the `species` object is included → ✅ Bird→Species relationship works.

### Step 20: POST — Create Birdspotting observations

Click **POST /birdspotting/** → Try it out:

**Observation 1:**
```json
{
  "bird_id": 1,
  "spotted_at": "2026-03-01T08:15:00",
  "location": "Brussels Park",
  "observer_name": "Nina Peeters",
  "notes": "Seen near the fountain"
}
```

**Expected:** Code **201** → ✅

**Observation 2:**
```json
{
  "bird_id": 1,
  "spotted_at": "2026-03-02T09:40:00",
  "location": "Ghent Riverside",
  "observer_name": "Lars Mertens",
  "notes": "Feeding on breadcrumbs"
}
```

**Expected:** Code **201** → ✅

**Observation 3:**
```json
{
  "bird_id": 2,
  "spotted_at": "2026-03-02T07:55:00",
  "location": "Antwerp Zoo Garden",
  "observer_name": "Emma Janssens",
  "notes": "Singing from a low branch"
}
```

**Expected:** Code **201** → ✅

### Step 21: GET — Birdspotting with bird details

Click **GET /birdspotting/{spotting_id}** → spotting_id = `1` → Execute.

**Expected:** Code **200**, body includes a `"bird"` object:
```json
{
  "id": 1,
  "bird_id": 1,
  "spotted_at": "2026-03-01T08:15:00",
  "location": "Brussels Park",
  "observer_name": "Nina Peeters",
  "notes": "Seen near the fountain",
  "bird": {
    "nickname": "Pip",
    ...
  }
}
```

If the `bird` object is included → ✅ Birdspotting→Bird relationship works.

---

## PHASE 5 — Test Filtering

### Step 22: Filter species by conservation status

Click **GET /species/** → set `conservation_status` = `Least Concern` → Execute.

**Expected:** All 4 species returned → ✅

Now try `conservation_status` = `Endangered` → Execute.

**Expected:** Empty array `[]` → ✅ (none match)

### Step 23: Filter birds by species_id

Click **GET /birds/** → set `species_id` = `1` → Execute.

**Expected:** Only Pip is returned → ✅

### Step 24: Filter birdspotting by observer name

Click **GET /birdspotting/** → set `observer_name` = `Nina Peeters` → Execute.

**Expected:** Only 1 observation (Brussels Park) → ✅

---

## PHASE 6 — Test Pagination

### Step 25: Paginate species

Click **GET /species/** → set `offset` = `0`, `limit` = `2` → Execute.

**Expected:** Only first 2 species returned → ✅

Now set `offset` = `2`, `limit` = `2` → Execute.

**Expected:** Last 2 species returned → ✅

### Step 26: Paginate birds

Click **GET /birds/** → set `offset` = `0`, `limit` = `1` → Execute.

**Expected:** Only 1 bird → ✅

### Step 27: Paginate birdspotting

Click **GET /birdspotting/** → set `offset` = `0`, `limit` = `2` → Execute.

**Expected:** Only 2 observations → ✅

---

## PHASE 7 — Test Validation

### Step 28: Negative age rejection (API layer)

Click **POST /birds/** → paste:

```json
{
  "nickname": "BadBird",
  "ring_code": "BAD-001",
  "age": -5,
  "species_id": 1
}
```

**Expected:** Code **422 Unprocessable Entity** with a validation error message about `age` → ✅

This proves `Field(ge=0)` works at the API/Pydantic level.

### Step 29: Duplicate ring_code rejection

Click **POST /birds/** → paste:

```json
{
  "nickname": "Duplicate",
  "ring_code": "SPARROW-001",
  "age": 1,
  "species_id": 1
}
```

**Expected:** Code **500** (IntegrityError) because `SPARROW-001` already exists (UNIQUE constraint) → ✅

### Step 30: Invalid species_id rejection

Click **POST /birds/** → paste:

```json
{
  "nickname": "Nobody",
  "ring_code": "FAKE-001",
  "age": 1,
  "species_id": 999
}
```

**Expected:** Code **500** (IntegrityError / ForeignKeyViolation) because species 999 does not exist → ✅

---

## PHASE 8 — Test Update & Delete (Extra Tasks)

### Step 31: PUT — Update a species

Click **PUT /species/{species_id}** → species_id = `1` → paste:

```json
{
  "name": "House Sparrow (Updated)",
  "scientific_name": "Passer domesticus",
  "family": "Passeridae",
  "conservation_status": "Near Threatened",
  "wingspan_cm": 21.5
}
```

**Expected:** Code **200**, response shows updated values → ✅

**Verify:** GET /species/1 → name should be "House Sparrow (Updated)" → ✅

### Step 32: PUT — Update a bird

Click **PUT /birds/{bird_id}** → bird_id = `1` → paste:

```json
{
  "nickname": "Pip (Updated)",
  "ring_code": "SPARROW-001",
  "age": 3,
  "species_id": 1
}
```

**Expected:** Code **200**, response shows updated values → ✅

### Step 33: PUT — Update a birdspotting

Click **PUT /birdspotting/{spotting_id}** → spotting_id = `1` → paste:

```json
{
  "bird_id": 1,
  "spotted_at": "2026-03-01T10:00:00",
  "location": "Brussels Park (Updated)",
  "observer_name": "Nina Peeters",
  "notes": "Updated note - seen near the bridge"
}
```

**Expected:** Code **200**, response shows updated values → ✅

### Step 34: DELETE — Delete a birdspotting

Click **DELETE /birdspotting/{spotting_id}** → spotting_id = `3` → Execute.

**Expected:** Code **204 No Content** → ✅

**Verify:** GET /birdspotting/ → should now show only 2 records → ✅

### Step 35: Test ON DELETE CASCADE

Delete bird 1 (Pip) and verify its birdspotting records are also deleted:

Click **DELETE /birds/{bird_id}** → bird_id = `1` → Execute.

**Expected:** Code **204** → ✅

**Verify:** GET /birdspotting/ → all observations for bird_id=1 should be gone (only 0 records left now since we already deleted observation 3) → ✅

### Step 36: Test ON DELETE RESTRICT

Try deleting species 2 (European Robin) which still has bird Rusty referencing it:

Click **DELETE /species/{species_id}** → species_id = `2` → Execute.

**Expected:** Code **500** (IntegrityError) — cannot delete species that has birds → ✅

This proves `ON DELETE RESTRICT` works.

### Step 37: GET non-existent resource (404 handling)

Click **GET /species/{species_id}** → species_id = `999` → Execute.

**Expected:** Code **404**, body: `{"detail": "Species not found"}` → ✅

Try the same for birds and birdspotting with id 999 → both should return 404 → ✅

---

## PHASE 9 — Verify in Adminer

### Step 38: Cross-check database state

Go back to **http://localhost:8080** → log in → click on each table:

1. Click `species` → "Select data" → verify the remaining records match what your API shows
2. Click `birds` → "Select data" → verify Pip is gone (we deleted it), Rusty/Ghost/Cloud remain
3. Click `birdspotting` → "Select data" → verify Pip's observations are gone (CASCADE)

If Adminer data matches API responses → ✅ Database is consistent.

---

## PHASE 10 — Verify Documentation Quality

### Step 39: Check /docs completeness

Back at **http://127.0.0.1:8000/docs**, verify:

- [ ] Every endpoint has a **description/docstring** (visible under the endpoint name)
- [ ] Every POST/PUT endpoint shows the **request body schema** (click to expand)
- [ ] Every endpoint shows the **response model schema** (under "Responses")
- [ ] Routes are grouped by **tags**: Species, Birds, Birdspotting, Root
- [ ] POST endpoints return **201**, DELETE returns **204**, errors return **404/422**

If all boxes check → ✅ Documentation is complete.

### Step 40: Check ReDoc

Go to **http://127.0.0.1:8000/redoc**

This should show a nicely formatted API documentation page with all endpoints, models, and schemas → ✅

---

## FINAL CHECKLIST

| #  | Test | Status |
|----|------|--------|
| 1  | Docker containers running (postgres + adminer) | ☐ |
| 2  | Adminer connects to bird_api database | ☐ |
| 3  | SQL tables created manually | ☐ |
| 4  | SQL INSERT data works (4 species, 4 birds, 5 birdspotting) | ☐ |
| 5  | SQL Query 1 (wingspan > 50, DESC, LIMIT 2) returns correct rows | ☐ |
| 6  | SQL Query 2 (JOIN birds + species) returns correct rows | ☐ |
| 7  | SQL Query 3 (COUNT + GROUP BY) returns correct counts | ☐ |
| 8  | FastAPI server starts without errors | ☐ |
| 9  | GET / returns Hello World | ☐ |
| 10 | /docs shows all endpoints grouped by tags | ☐ |
| 11 | POST species works (4 species created) | ☐ |
| 12 | GET /species returns all species | ☐ |
| 13 | GET /species/{id} returns species + birds (back-reference) | ☐ |
| 14 | GET /species/{id}/birds returns birds list | ☐ |
| 15 | POST birds works (4 birds created) | ☐ |
| 16 | GET /birds/{id} returns bird + species (relationship) | ☐ |
| 17 | POST birdspotting works (3+ observations) | ☐ |
| 18 | GET /birdspotting/{id} returns observation + bird | ☐ |
| 19 | Filter: GET /species?conservation_status=... works | ☐ |
| 20 | Filter: GET /birds?species_id=... works | ☐ |
| 21 | Filter: GET /birdspotting?observer_name=... works | ☐ |
| 22 | Pagination: offset + limit work on all 3 resources | ☐ |
| 23 | Validation: negative age returns 422 | ☐ |
| 24 | PUT update works for species/birds/birdspotting | ☐ |
| 25 | DELETE works for species/birds/birdspotting | ☐ |
| 26 | ON DELETE CASCADE: deleting bird removes its observations | ☐ |
| 27 | ON DELETE RESTRICT: deleting species with birds is blocked | ☐ |
| 28 | 404 returned for non-existent resources | ☐ |
| 29 | Adminer shows correct database state | ☐ |
| 30 | /docs has docstrings, tags, request/response models, correct status codes | ☐ |

**If all 30 boxes are checked → your assignment is 100% complete and verified.**

---

## Cleanup (when you're done)

Stop the FastAPI server: press `Ctrl+C` in the terminal.

Stop Docker containers:

```powershell
docker compose -f compose.db.yaml down
```

To also wipe the database volume (fresh start):

```powershell
docker compose -f compose.db.yaml down -v
```

Deactivate virtual environment:

```powershell
deactivate
```
