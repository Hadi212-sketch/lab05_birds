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
