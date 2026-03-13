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
    # Apply manual pagination on the relationship list
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
