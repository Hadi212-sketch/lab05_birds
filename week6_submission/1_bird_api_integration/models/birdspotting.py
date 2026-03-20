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
