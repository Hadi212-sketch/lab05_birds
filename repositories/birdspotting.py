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
