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
