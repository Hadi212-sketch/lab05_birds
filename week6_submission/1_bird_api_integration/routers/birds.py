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
