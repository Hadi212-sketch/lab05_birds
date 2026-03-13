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
    """Response model for reading a bird (includes species)."""
    id: int
    species_id: int


class BirdReadWithSpecies(BirdRead):
    """Response model for reading a bird with its species details."""
    species: Optional["SpeciesRead"] = None


# --- Import at bottom to avoid circular imports ---
from models.species import SpeciesRead  # noqa: E402

BirdReadWithSpecies.model_rebuild()
