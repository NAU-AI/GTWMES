import logging
from sqlalchemy.orm import Session, load_only
from sqlalchemy.exc import SQLAlchemyError
from model.equipment import Equipment
from typing import Optional, List

logger = logging.getLogger(__name__)


class EquipmentDAO:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, equipment_id: int) -> Optional[Equipment]:
        """Find equipment by ID."""
        try:
            return self.session.get(Equipment, equipment_id)
        except SQLAlchemyError as e:
            logger.error("Error finding equipment ID %d: %s", equipment_id, e)
            return None

    def find_by_code(self, code: str) -> Optional[Equipment]:
        """Find equipment by its code (selective fields only)."""
        try:
            return (
                self.session.query(Equipment)
                .options(
                    load_only(
                        Equipment.id, Equipment.code, Equipment.production_order_code
                    )
                )
                .filter_by(code=code)
                .one_or_none()
            )
        except SQLAlchemyError as e:
            logger.error("Error finding equipment by code '%s': %s", code, e)
            return None

    def find_all(self) -> List[Equipment]:
        """Return all equipment entries."""
        try:
            return self.session.query(Equipment).all()
        except SQLAlchemyError as e:
            logger.error("Error finding all equipment: %s", e)
            return []

    def save(self, equipment: Equipment) -> Optional[Equipment]:
        try:
            self.session.add(equipment)
            self.session.flush()
            self.session.refresh(equipment)
            self.session.commit()
            return equipment
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error("Error saving equipment: %s", e)
            return None

    def update(self, equipment_id: int, updated_data: dict) -> Optional[Equipment]:
        """Update an equipment with new field values."""
        try:
            equipment = self.find_by_id(equipment_id)
            if not equipment:
                return None

            for key, value in updated_data.items():
                if hasattr(equipment, key):
                    setattr(equipment, key, value)

            self.session.flush()
            self.session.refresh(equipment)
            self.session.commit()
            return equipment
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error("Error updating equipment ID %d: %s", equipment_id, e)
            return None

    def update_production_order_code(
        self, equipment_id: int, production_order_code: str
    ) -> bool:
        """Update only the production order code of the equipment."""
        try:
            equipment = self.find_by_id(equipment_id)
            if not equipment:
                return False

            equipment.production_order_code = production_order_code
            self.session.flush()
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "Error updating production order code for equipment ID %d: %s",
                equipment_id,
                e,
            )
            return False

    def delete(self, equipment_id: int) -> bool:
        """Delete an equipment by its ID."""
        try:
            equipment = self.find_by_id(equipment_id)
            if not equipment:
                return False

            self.session.delete(equipment)
            self.session.flush()
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error("Error deleting equipment ID %d: %s", equipment_id, e)
            return False
