# 5. Databases ORM

## Introduction

In this assignment, you will build a FastAPI project that uses PostgreSQL for all data storage. You will work code-first with SQLModel, structure your API with routers, repositories and models, and add relationships between tables.

This assignment takes the same general flow as our previous assignment, but now the domain is:

- Birds
- Species
- Birdspotting

## Objective

### Knowledge

- PostgreSQL databases
- SQL queries
- Python libraries
  - SQLModel
  - psycopg
  - FastAPI
  - python-dotenv
- Python API structure
- Relational modelling

### Skills

- Setting up PostgreSQL with Docker Compose
- Querying relational data with SQL
- Connecting FastAPI to PostgreSQL
- Structuring an API with models, repositories and routers
- Working with one-to-many relationships

### Necessities

This assignment requires Docker Desktop to be installed and running on your machine.

## Assignment explanation

In the previous assignment, you worked with databases and explored the first steps of connecting Python code to relational data. This assignment continues that work, but now everything uses PostgreSQL.

You will build an API around bird species, individual birds, and birdspotting observations.

### Git hints

Treat this assignment as a sequence of small milestones instead of one large change.

- Create a new branch before each major part of the assignment.
- Commit when one part is working, not after every tiny file save.
- Use commit messages that describe completed work.
- Merge back into main only when that part is stable.

Suggested branches:

- `feature/setup-postgres`
- `feature/sql-recap`
- `feature/fastapi-base`
- `feature/species-api`
- `feature/birds-api`
- `feature/birdspotting-api`
- `feature/docs-cleanup`

Useful commands:

```
git switch main
git switch feature/setup-postgres
git add .
git commit -m "feat: Set up PostgreSQL and Adminer"
git switch main
git merge feature/setup-postgres
```

## Project setup

Start a new project in a new directory and configure your Git repository properly.

Create a new `compose.db.yaml` file in the root of your project.

It should contain at least this:

```yaml
services:
  postgres:
    image: postgres:18-alpine
    restart: always
    ports:
      - 5432:5432
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: bird_api
    volumes:
      - db:/var/lib/postgresql

volumes:
  db:
```

When you start this Compose project, Docker will create a PostgreSQL database for you with persistent storage.

**Git checkpoint**

Commit once:

- `compose.db.yaml` is correct
- `.env` exists
- PostgreSQL and Adminer start successfully

## Adding a GUI

Use adminer as a lightweight GUI so you can inspect your PostgreSQL database in the browser.

> ❓ **QUESTION - Task**
>
> Add an Adminer service to your Compose file.
> Start the containers.
> Connect to PostgreSQL through Adminer.
> Paste the YAML you used below.
> Also write down the connection data you used.

> 💻 **ANSWER**
>
> ```yaml
> services:
>   postgres:
>     image: postgres:18-alpine
>     restart: always
>     env_file:
>       - .env
>     ports:
>       - 5432:5432
>     volumes:
>       - db:/var/lib/postgresql
>
>   adminer:
>     image: adminer
>     restart: always
>     ports:
>       - 8080:8080
>     depends_on:
>       - postgres
>
> volumes:
>   db:
> ```
>
> Adminer connection settings:
>
> | Setting  | Value      |
> |----------|------------|
> | System   | PostgreSQL |
> | Server   | postgres   |
> | Username | user       |
> | Password | password   |
> | Database | bird_api   |

## Recap into SQL

Before connecting Python to the database, first create and query the tables manually in PostgreSQL.

General recommendation: Keep your table names lowercase. Beware of typo's, so that we are sure we are working with the same setup!

**Git checkpoint**

Commit once:

- all 3 tables exist
- test data is inserted
- your 3 SQL queries work

### Table 1: Species

Create a species table.

This table should contain:

- id
- name
- scientific_name
- family
- conservation_status
- wingspan_cm

> ❓ **QUESTION**
>
> Write the SQL statement you used to create the species table.
> Why is `numeric(5,2)` a better fit than `integer` for `wingspan_cm`?

> 💻 **ANSWER**
>
> ```sql
> CREATE TABLE species (
>   id SERIAL PRIMARY KEY,
>   name VARCHAR(255) NOT NULL,
>   scientific_name VARCHAR(255) NOT NULL,
>   family VARCHAR(255) NOT NULL,
>   conservation_status VARCHAR(255) NOT NULL,
>   wingspan_cm NUMERIC(5,2) NOT NULL
> );
> ```
>
> `NUMERIC(5,2)` is a better fit than `INTEGER` because bird wingspans are often measured with decimal precision (e.g. 22.50 cm). `INTEGER` can only store whole numbers, so values like 22.5 would be rounded or lost. `NUMERIC(5,2)` allows up to 5 total digits with 2 decimal places (e.g. 195.00), preserving accurate measurements without rounding errors.

Use this dummy data for the table:

```json
[
  {
    "name": "House Sparrow",
    "scientific_name": "Passer domesticus",
    "family": "Passeridae",
    "conservation_status": "Least Concern",
    "wingspan_cm": 21.0
  },
  {
    "name": "European Robin",
    "scientific_name": "Erithacus rubecula",
    "family": "Muscicapidae",
    "conservation_status": "Least Concern",
    "wingspan_cm": 22.5
  },
  {
    "name": "Barn Owl",
    "scientific_name": "Tyto alba",
    "family": "Tytonidae",
    "conservation_status": "Least Concern",
    "wingspan_cm": 95.0
  },
  {
    "name": "White Stork",
    "scientific_name": "Ciconia ciconia",
    "family": "Ciconiidae",
    "conservation_status": "Least Concern",
    "wingspan_cm": 195.0
  }
]
```

```sql
INSERT INTO species (name, scientific_name, family, conservation_status, wingspan_cm)
VALUES
  ('House Sparrow', 'Passer domesticus', 'Passeridae', 'Least Concern', 21.00),
  ('European Robin', 'Erithacus rubecula', 'Muscicapidae', 'Least Concern', 22.50),
  ('Barn Owl', 'Tyto alba', 'Tytonidae', 'Least Concern', 95.00),
  ('White Stork', 'Ciconia ciconia', 'Ciconiidae', 'Least Concern', 195.00);
```

### Table 2: Birds

Now create a second table called birds.

Each bird is one individual animal and belongs to one species.

Use this SQL definition as a starting point:

```sql
CREATE TABLE birds (
  id SERIAL PRIMARY KEY,
  nickname VARCHAR(255) NOT NULL,
  ring_code VARCHAR(100) UNIQUE NOT NULL,
  age INTEGER NOT NULL,
  species_id INTEGER NOT NULL,
  FOREIGN KEY (species_id) REFERENCES species(id) ON DELETE RESTRICT
);
```

Use this dummy data:

```json
[
  {
    "nickname": "Pip",
    "ring_code": "SPARROW-001",
    "age": 2,
    "species_id": 1
  },
  {
    "nickname": "Rusty",
    "ring_code": "ROBIN-001",
    "age": 1,
    "species_id": 2
  },
  {
    "nickname": "Ghost",
    "ring_code": "OWL-001",
    "age": 4,
    "species_id": 3
  },
  {
    "nickname": "Cloud",
    "ring_code": "STORK-001",
    "age": 6,
    "species_id": 4
  }
]
```

```sql
INSERT INTO birds (nickname, ring_code, age, species_id)
VALUES
  ('Pip', 'SPARROW-001', 2, 1),
  ('Rusty', 'ROBIN-001', 1, 2),
  ('Ghost', 'OWL-001', 4, 3),
  ('Cloud', 'STORK-001', 6, 4);
```

### Table 3: Birdspotting

Create a third table called birdspotting.

Each birdspotting record represents one observation of one bird.

Use this SQL definition as a starting point:

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

Insert at least 5 observation records yourself.

```sql
INSERT INTO birdspotting (bird_id, spotted_at, location, observer_name, notes)
VALUES
  (1, '2026-03-01 08:15:00', 'Brussels Park', 'Nina Peeters', 'Seen near the fountain'),
  (1, '2026-03-02 09:40:00', 'Ghent Riverside', 'Lars Mertens', 'Feeding on breadcrumbs'),
  (2, '2026-03-02 07:55:00', 'Antwerp Zoo Garden', 'Emma Janssens', 'Singing from a low branch'),
  (3, '2026-03-03 21:10:00', 'Ardennes Forest Edge', 'Tom Wouters', 'Hunting at dusk'),
  (4, '2026-03-04 12:25:00', 'Leuven Wetlands', 'Sofie Claes', 'Resting close to the marsh');
```

## Query the information

Now that the tables contain data, write a few SQL queries first before rebuilding the same ideas in Python.

### Query 1. Species with a large wingspan

Fetch all species with a wingspan greater than 50 cm.

**TASK**

- Use `WHERE`.
- Sort from largest to smallest wingspan.
- Return only the first 2 rows.

> ❓ **QUESTION**
>
> Which query did you use?

> 💻 **ANSWER**
>
> ```sql
> SELECT *
> FROM species
> WHERE wingspan_cm > 50
> ORDER BY wingspan_cm DESC
> LIMIT 2;
> ```

### Query 2. Bird with its species

Fetch all birds together with the species name they belong to.

**TASK**

- Use a `JOIN`.
- Return at least the bird nickname, ring code and species name.

> ❓ **QUESTION**
>
> Which query did you use?

> 💻 **ANSWER**
>
> ```sql
> SELECT
>   b.nickname,
>   b.ring_code,
>   s.name AS species_name
> FROM birds b
> JOIN species s ON b.species_id = s.id;
> ```

### Query 3. Number of sightings per bird

Count how many times each bird has been spotted.

**TASK**

- Use `COUNT(*)`.
- Group by the bird.
- Sort descending by the number of sightings.

> ❓ **QUESTION**
>
> Which query did you use?

> 💻 **ANSWER**
>
> ```sql
> SELECT
>   b.nickname,
>   COUNT(*) AS sighting_count
> FROM birdspotting bs
> JOIN birds b ON bs.bird_id = b.id
> GROUP BY b.id, b.nickname
> ORDER BY sighting_count DESC;
> ```

## Code-first databases

Now connect PostgreSQL to Python and FastAPI.

### Installing the packages

Use a virtual environment and install at least these packages:

- sqlmodel
- psycopg[binary]
- fastapi
- python-dotenv

I would suggest to create a `requirements.txt` file with these packages in there. I gave you the file here, but to make it even better, add the fixed Package Versions from Pypi in here. Example: `fastapi==0.135.1` Note that we do use `==` here, which is the syntax for these requirements.txt files.

```
fastapi==0.135.1
sqlmodel==0.0.37
psycopg[binary]==3.3.3
python-dotenv==1.2.2
```

### First FastAPI test

Create a `main.py` file:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

Run:

```
fastapi dev main.py
```

Visit:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

**Git checkpoint**

Commit once:

- the FastAPI app starts
- `/` works
- `/docs` opens correctly

### Suggested folder structure

```
lab05_birds
├── routers
│   ├── species.py
│   ├── birds.py
│   └── birdspotting.py
├── repositories
│   ├── species.py
│   ├── birds.py
│   └── birdspotting.py
├── models
│   ├── species.py
│   ├── birds.py
│   └── birdspotting.py
├── database.py
├── main.py
├── .env
└── compose.db.yaml
```

### Database connection

Create a `.env` file next to your Compose file:

```
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_PORT=5432
POSTGRES_HOST=postgres
POSTGRES_DB=bird_api
```

Update your Compose file so it reads from `.env`:

```yaml
services:
  postgres:
    image: postgres:18-alpine
    env_file:
      - .env
    ports:
      - 5432:5432
    volumes:
      - db:/var/lib/postgresql
```

Create a `database.py` script:

```python
import os
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

if os.getenv("ENVIRONMENT") == "DOCKER":
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
else:
    POSTGRES_HOST = "127.0.0.1"

DATABASE_URL = (
    f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

def start_db():
    SQLModel.metadata.create_all(engine)
```

Make sure this is used in your `main.py`.

## Species example

Start with the species resource first.

SQLModel combines Pydantic-style models with SQLAlchemy table definitions, so you only need a models directory.

### models/species.py

```python
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.birds import Bird


class SpeciesBase(SQLModel):
    """Base model for species data (shared fields)."""
    name: str
    scientific_name: str
    family: str
    conservation_status: str
    wingspan_cm: Decimal = Field(max_digits=5, decimal_places=2)


class Species(SpeciesBase, table=True):
    """Species database table model."""
    id: Optional[int] = Field(default=None, primary_key=True)

    birds: List["Bird"] = Relationship(back_populates="species")


class SpeciesCreate(SpeciesBase):
    """Request model for creating a species."""
    pass


class SpeciesRead(SpeciesBase):
    """Response model for reading a species."""
    id: int


class SpeciesReadWithBirds(SpeciesRead):
    """Response model for a species with its birds."""
    birds: List["BirdReadNested"] = []


# --- Nested model to avoid circular imports ---
from models.birds import BirdReadNested  # noqa: E402

SpeciesReadWithBirds.model_rebuild()
```

### repositories/species.py

```python
from typing import Optional

from sqlmodel import Session, select

from models.species import Species, SpeciesCreate


class SpeciesRepository:
    """Repository for species CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(
        self,
        conservation_status: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Species]:
        """Get all species, optionally filtered by conservation status."""
        statement = select(Species)
        if conservation_status:
            statement = statement.where(
                Species.conservation_status == conservation_status
            )
        statement = statement.offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def get_one(self, species_id: int) -> Optional[Species]:
        """Get a single species by id."""
        return self.session.get(Species, species_id)

    def insert(self, payload: SpeciesCreate) -> Species:
        """Insert a new species."""
        item = Species.model_validate(payload)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(self, species_id: int, payload: SpeciesCreate) -> Optional[Species]:
        """Update an existing species."""
        item = self.session.get(Species, species_id)
        if not item:
            return None
        update_data = payload.model_dump()
        for key, value in update_data.items():
            setattr(item, key, value)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete(self, species_id: int) -> bool:
        """Delete a species by id. Returns True if deleted."""
        item = self.session.get(Species, species_id)
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True
```

### routers/species.py

```python
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from database import get_session
from models.birds import BirdReadNested
from models.species import Species, SpeciesCreate, SpeciesRead, SpeciesReadWithBirds
from repositories.species import SpeciesRepository

router = APIRouter(prefix="/species", tags=["Species"])


def get_species_repository(
    session: Annotated[Session, Depends(get_session)],
) -> SpeciesRepository:
    return SpeciesRepository(session)


@router.get("/", response_model=List[SpeciesRead])
async def get_species(
    repo: Annotated[SpeciesRepository, Depends(get_species_repository)],
    conservation_status: Optional[str] = Query(
        default=None, description="Filter by conservation status"
    ),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
):
    """Get all species. Supports filtering by conservation_status and pagination."""
    return repo.get_all(
        conservation_status=conservation_status, offset=offset, limit=limit
    )


@router.get("/{species_id}", response_model=SpeciesReadWithBirds)
async def get_species_by_id(
    species_id: int,
    repo: Annotated[SpeciesRepository, Depends(get_species_repository)],
):
    """Get a single species by id, including its birds (back-reference)."""
    item = repo.get_one(species_id)
    if not item:
        raise HTTPException(status_code=404, detail="Species not found")
    return item


@router.get("/{species_id}/birds", response_model=List[BirdReadNested])
async def get_birds_by_species(
    species_id: int,
    repo: Annotated[SpeciesRepository, Depends(get_species_repository)],
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
):
    """Get all birds belonging to a specific species."""
    item = repo.get_one(species_id)
    if not item:
        raise HTTPException(status_code=404, detail="Species not found")
    birds = item.birds[offset : offset + limit]
    return birds


@router.post("/", response_model=SpeciesRead, status_code=201)
async def add_species(
    species: SpeciesCreate,
    repo: Annotated[SpeciesRepository, Depends(get_species_repository)],
):
    """Create a new species."""
    return repo.insert(species)


@router.put("/{species_id}", response_model=SpeciesRead)
async def update_species(
    species_id: int,
    species: SpeciesCreate,
    repo: Annotated[SpeciesRepository, Depends(get_species_repository)],
):
    """Update an existing species."""
    item = repo.update(species_id, species)
    if not item:
        raise HTTPException(status_code=404, detail="Species not found")
    return item


@router.delete("/{species_id}", status_code=204)
async def delete_species(
    species_id: int,
    repo: Annotated[SpeciesRepository, Depends(get_species_repository)],
):
    """Delete a species by id."""
    success = repo.delete(species_id)
    if not success:
        raise HTTPException(status_code=404, detail="Species not found")
    return None
```

**Git checkpoint**

Commit once:

- `GET /species` works
- `POST /species` works
- data is written to PostgreSQL

## Add the relationship between Birds and Species

Now extend the project with birds.

**TASK**

- Create `models/birds.py`.
- Extend it with the `Bird` and `BirdCreate` models.
- Create `repositories/birds.py`.
- Create `routers/birds.py`.
- Link the router in `main.py`.
- Make sure a bird cannot be inserted with a species that does not exist.

Use this as a starting point:

### models/birds.py

```python
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import CheckConstraint, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.birdspotting import Birdspotting
    from models.species import Species


class BirdBase(SQLModel):
    """Base model for bird data (shared fields)."""
    nickname: str
    ring_code: str
    age: int = Field(ge=0, description="Age of the bird in years (cannot be negative)")


class Bird(BirdBase, table=True):
    """Bird database table model."""
    __tablename__ = "birds"
    __table_args__ = (
        CheckConstraint("age >= 0", name="check_bird_age_non_negative"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    ring_code: str = Field(unique=True)
    species_id: int = Field(foreign_key="species.id")

    species: Optional["Species"] = Relationship(back_populates="birds")
    birdspottings: List["Birdspotting"] = Relationship(back_populates="bird")


class BirdCreate(BirdBase):
    """Request model for creating a bird."""
    species_id: int


class BirdReadNested(BirdBase):
    """Nested response model for bird (without species to avoid recursion)."""
    id: int
    species_id: int


class BirdRead(BirdBase):
    """Response model for reading a bird."""
    id: int
    species_id: int


class BirdReadWithSpecies(BirdRead):
    """Response model for reading a bird with its species details."""
    species: Optional["SpeciesRead"] = None


# --- Import at bottom to avoid circular imports ---
from models.species import SpeciesRead  # noqa: E402

BirdReadWithSpecies.model_rebuild()
```

### repositories/birds.py

```python
from typing import Optional

from sqlmodel import Session, select

from models.birds import Bird, BirdCreate


class BirdRepository:
    """Repository for bird CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(
        self,
        species_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Bird]:
        """Get all birds, optionally filtered by species_id."""
        statement = select(Bird)
        if species_id is not None:
            statement = statement.where(Bird.species_id == species_id)
        statement = statement.offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def get_one(self, bird_id: int) -> Optional[Bird]:
        """Get a single bird by id."""
        return self.session.get(Bird, bird_id)

    def insert(self, payload: BirdCreate) -> Bird:
        """Insert a new bird."""
        item = Bird.model_validate(payload)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(self, bird_id: int, payload: BirdCreate) -> Optional[Bird]:
        """Update an existing bird."""
        item = self.session.get(Bird, bird_id)
        if not item:
            return None
        update_data = payload.model_dump()
        for key, value in update_data.items():
            setattr(item, key, value)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete(self, bird_id: int) -> bool:
        """Delete a bird by id. Returns True if deleted."""
        item = self.session.get(Bird, bird_id)
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True

    def get_by_species(
        self,
        species_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Bird]:
        """Get all birds belonging to a specific species."""
        statement = (
            select(Bird)
            .where(Bird.species_id == species_id)
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(statement).all())
```

### routers/birds.py

```python
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from database import get_session
from models.birds import BirdCreate, BirdRead, BirdReadWithSpecies
from repositories.birds import BirdRepository

router = APIRouter(prefix="/birds", tags=["Birds"])


def get_bird_repository(
    session: Annotated[Session, Depends(get_session)],
) -> BirdRepository:
    return BirdRepository(session)


@router.get("/", response_model=List[BirdRead])
async def get_birds(
    repo: Annotated[BirdRepository, Depends(get_bird_repository)],
    species_id: Optional[int] = Query(
        default=None, description="Filter by species id"
    ),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
):
    """Get all birds. Supports filtering by species_id and pagination."""
    return repo.get_all(species_id=species_id, offset=offset, limit=limit)


@router.get("/{bird_id}", response_model=BirdReadWithSpecies)
async def get_bird_by_id(
    bird_id: int,
    repo: Annotated[BirdRepository, Depends(get_bird_repository)],
):
    """Get a single bird by id, including its species details."""
    item = repo.get_one(bird_id)
    if not item:
        raise HTTPException(status_code=404, detail="Bird not found")
    return item


@router.post("/", response_model=BirdRead, status_code=201)
async def add_bird(
    bird: BirdCreate,
    repo: Annotated[BirdRepository, Depends(get_bird_repository)],
):
    """Create a new bird. The species_id must reference an existing species."""
    return repo.insert(bird)


@router.put("/{bird_id}", response_model=BirdRead)
async def update_bird(
    bird_id: int,
    bird: BirdCreate,
    repo: Annotated[BirdRepository, Depends(get_bird_repository)],
):
    """Update an existing bird."""
    item = repo.update(bird_id, bird)
    if not item:
        raise HTTPException(status_code=404, detail="Bird not found")
    return item


@router.delete("/{bird_id}", status_code=204)
async def delete_bird(
    bird_id: int,
    repo: Annotated[BirdRepository, Depends(get_bird_repository)],
):
    """Delete a bird by id."""
    success = repo.delete(bird_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bird not found")
    return None
```

**Git checkpoint**

Commit once:

- birds can be added
- birds are linked to an existing species
- invalid `species_id` values are rejected

## Add Birdspotting observations

Now add the third resource: birdspotting.

Each observation belongs to one bird.

**TASK**

- Create the SQLModel table model.
- Create the SQLModel request and response models.
- Create repository methods for:
  - `get_all`
  - `get_one`
  - `insert`
- Create router endpoints for those methods.
- Make sure the response includes the linked bird.

Suggested fields:

- id
- bird_id
- spotted_at
- location
- observer_name
- notes

### models/birdspotting.py

```python
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.birds import Bird


class BirdspottingBase(SQLModel):
    """Base model for birdspotting data (shared fields)."""
    spotted_at: datetime
    location: str
    observer_name: str
    notes: Optional[str] = None


class Birdspotting(BirdspottingBase, table=True):
    """Birdspotting database table model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    bird_id: int = Field(foreign_key="birds.id", ondelete="CASCADE")

    bird: Optional["Bird"] = Relationship(back_populates="birdspottings")


class BirdspottingCreate(BirdspottingBase):
    """Request model for creating a birdspotting observation."""
    bird_id: int


class BirdspottingRead(BirdspottingBase):
    """Response model for reading a birdspotting observation."""
    id: int
    bird_id: int


class BirdspottingReadWithBird(BirdspottingRead):
    """Response model for a birdspotting observation with its bird details."""
    bird: Optional["BirdRead"] = None


# --- Import at bottom to avoid circular imports ---
from models.birds import BirdRead  # noqa: E402

BirdspottingReadWithBird.model_rebuild()
```

### repositories/birdspotting.py

```python
from typing import Optional

from sqlmodel import Session, select

from models.birdspotting import Birdspotting, BirdspottingCreate


class BirdspottingRepository:
    """Repository for birdspotting CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(
        self,
        observer_name: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Birdspotting]:
        """Get all birdspotting records, optionally filtered by observer name."""
        statement = select(Birdspotting)
        if observer_name:
            statement = statement.where(
                Birdspotting.observer_name == observer_name
            )
        statement = statement.offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def get_one(self, spotting_id: int) -> Optional[Birdspotting]:
        """Get a single birdspotting record by id."""
        return self.session.get(Birdspotting, spotting_id)

    def insert(self, payload: BirdspottingCreate) -> Birdspotting:
        """Insert a new birdspotting observation."""
        item = Birdspotting.model_validate(payload)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(
        self, spotting_id: int, payload: BirdspottingCreate
    ) -> Optional[Birdspotting]:
        """Update an existing birdspotting observation."""
        item = self.session.get(Birdspotting, spotting_id)
        if not item:
            return None
        update_data = payload.model_dump()
        for key, value in update_data.items():
            setattr(item, key, value)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete(self, spotting_id: int) -> bool:
        """Delete a birdspotting record by id. Returns True if deleted."""
        item = self.session.get(Birdspotting, spotting_id)
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True
```

### routers/birdspotting.py

```python
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from database import get_session
from models.birdspotting import (
    BirdspottingCreate,
    BirdspottingRead,
    BirdspottingReadWithBird,
)
from repositories.birdspotting import BirdspottingRepository

router = APIRouter(prefix="/birdspotting", tags=["Birdspotting"])


def get_birdspotting_repository(
    session: Annotated[Session, Depends(get_session)],
) -> BirdspottingRepository:
    return BirdspottingRepository(session)


@router.get("/", response_model=List[BirdspottingRead])
async def get_birdspottings(
    repo: Annotated[BirdspottingRepository, Depends(get_birdspotting_repository)],
    observer_name: Optional[str] = Query(
        default=None, description="Filter by observer name"
    ),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
):
    """Get all birdspotting observations. Supports filtering by observer_name and pagination."""
    return repo.get_all(
        observer_name=observer_name, offset=offset, limit=limit
    )


@router.get("/{spotting_id}", response_model=BirdspottingReadWithBird)
async def get_birdspotting_by_id(
    spotting_id: int,
    repo: Annotated[BirdspottingRepository, Depends(get_birdspotting_repository)],
):
    """Get a single birdspotting observation by id, including the linked bird."""
    item = repo.get_one(spotting_id)
    if not item:
        raise HTTPException(status_code=404, detail="Birdspotting not found")
    return item


@router.post("/", response_model=BirdspottingRead, status_code=201)
async def add_birdspotting(
    spotting: BirdspottingCreate,
    repo: Annotated[BirdspottingRepository, Depends(get_birdspotting_repository)],
):
    """Create a new birdspotting observation. The bird_id must reference an existing bird."""
    return repo.insert(spotting)


@router.put("/{spotting_id}", response_model=BirdspottingRead)
async def update_birdspotting(
    spotting_id: int,
    spotting: BirdspottingCreate,
    repo: Annotated[BirdspottingRepository, Depends(get_birdspotting_repository)],
):
    """Update an existing birdspotting observation."""
    item = repo.update(spotting_id, spotting)
    if not item:
        raise HTTPException(status_code=404, detail="Birdspotting not found")
    return item


@router.delete("/{spotting_id}", status_code=204)
async def delete_birdspotting(
    spotting_id: int,
    repo: Annotated[BirdspottingRepository, Depends(get_birdspotting_repository)],
):
    """Delete a birdspotting observation by id."""
    success = repo.delete(spotting_id)
    if not success:
        raise HTTPException(status_code=404, detail="Birdspotting not found")
    return None
```

**Git checkpoint**

Commit once:

- birdspotting records can be created
- `GET /birdspotting` works
- `GET /birdspotting/{id}` works
- each observation is linked to a bird

## Test if it works

Use `/docs` to test your API.

At minimum:

- Insert 2 species.
- Insert 2 birds linked to those species.
- Insert 3 birdspotting observations linked to those birds.
- Perform a GET request to verify the relations.

### main.py

```python
from fastapi import FastAPI

from database import start_db
from routers import birds, birdspotting, species

app = FastAPI(
    title="Birds API",
    description="A FastAPI project for managing bird species, individual birds, and birdspotting observations.",
    version="1.0.0",
)

app.include_router(species.router)
app.include_router(birds.router)
app.include_router(birdspotting.router)


@app.on_event("startup")
def on_startup():
    """Create database tables on application startup."""
    start_db()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — health check."""
    return {"message": "Hello World"}
```

### Running the server

For local development, use:

```
fastapi dev main.py
```

This gives you an auto-reloading development server without needing to call uvicorn manually.

## Documentation

Make sure your API is documented properly:

- Add docstrings ✅
- Use request and response models ✅
- Group routes with tags ✅
- Return correct HTTP status codes ✅

**Final Git checkpoint**

Make one final cleanup commit when:

- the project runs from start to finish
- the main endpoints work in `/docs`
- the code is organised cleanly
- your branch history shows clear progress

Suggested final commit message:

```
git commit -m "feat: Finish Birds API assignment"
```

## Extra tasks

- Add update and delete endpoints for all three resources. ✅
- Add filtering, for example:
  - species by conservation status ✅
  - birds by species ✅
  - birdspotting by observer ✅
- Add a back-reference so you can fetch one species together with all its birds. ✅
- Add validation so age cannot be negative. ✅
- Add pagination to at least one listing endpoint. ✅

## Extra task solution

Implemented in the solution project:

### CRUD endpoints

```
POST /species
PUT /species/{id}
DELETE /species/{id}

POST /birds
PUT /birds/{id}
DELETE /birds/{id}

POST /birdspotting
PUT /birdspotting/{id}
DELETE /birdspotting/{id}
```

### Filtering examples

```
GET /species?conservation_status=Least Concern
GET /birds?species_id=1
GET /birdspotting?observer_name=Nina Peeters
```

### Back-reference examples

```
GET /species/1
GET /species/1/birds
```

### Validation

Bird age is validated in the API with `ge=0` and enforced in PostgreSQL with a `CHECK` constraint so negative values are rejected at both levels.

### Pagination examples

```
GET /species?offset=0&limit=10
GET /birds?species_id=1&offset=0&limit=10
GET /birdspotting?observer_name=Nina Peeters&offset=0&limit=10
```

### Branches used

```
feature/setup-postgres
feature/sql-recap
feature/fastapi-base
feature/species-api
feature/birds-api
feature/birdspotting-api
feature/docs-cleanup
feature/birds-crud-extras
feature/birds-filtering-extras
feature/birds-backreference-extras
feature/birds-validation-extras
feature/birds-pagination-extras
feature/birds-docs-extras
```

### Git workflow

```bash
# Setup
git switch main
git switch -c feature/setup-postgres
git add .
git commit -m "feat: Set up PostgreSQL and Adminer with Docker Compose"
git switch main
git merge feature/setup-postgres

# SQL recap
git switch -c feature/sql-recap
git add .
git commit -m "feat: Create SQL tables, insert test data, write recap queries"
git switch main
git merge feature/sql-recap

# FastAPI base
git switch -c feature/fastapi-base
git add .
git commit -m "feat: Set up FastAPI base with database connection"
git switch main
git merge feature/fastapi-base

# Species API
git switch -c feature/species-api
git add .
git commit -m "feat: Implement Species CRUD with model, repository and router"
git switch main
git merge feature/species-api

# Birds API
git switch -c feature/birds-api
git add .
git commit -m "feat: Implement Birds CRUD with Species relationship"
git switch main
git merge feature/birds-api

# Birdspotting API
git switch -c feature/birdspotting-api
git add .
git commit -m "feat: Implement Birdspotting CRUD with Bird relationship"
git switch main
git merge feature/birdspotting-api

# Docs cleanup
git switch -c feature/docs-cleanup
git add .
git commit -m "feat: Finish Birds API assignment"
git switch main
git merge feature/docs-cleanup
```
