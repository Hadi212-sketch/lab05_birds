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
