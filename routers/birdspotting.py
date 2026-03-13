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
