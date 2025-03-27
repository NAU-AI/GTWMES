import logging
from typing import List, Optional

from database.connection.db_connection import DatabaseConnection
from model.equipment import Equipment
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)


class EquipmentDAO:
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    def find_by_id(self, equipment_id: int) -> Optional[Equipment]:
        """Find equipment by ID."""
        try:
            with self.db_connection.get_session() as session:
                return session.get(Equipment, equipment_id)
        except SQLAlchemyError as e:
            logger.error("Error finding equipment ID %d: %s", equipment_id, e)
            return None

    def find_by_code(self, code: str) -> Optional[Equipment]:
        """Find equipment by code."""
        try:
            with self.db_connection.get_session() as session:
                return session.query(Equipment).filter_by(code=code).one_or_none()
        except SQLAlchemyError as e:
            logger.error("Error finding equipment by code '%s': %s", code, e)
            return None

    def find_all(self) -> List[Equipment]:
        """Return all equipment entries with relationships loaded."""
        try:
            with self.db_connection.get_session() as session:
                equipment_list = (
                    session.query(Equipment)
                    .options(joinedload(Equipment.variables))
                    .all()
                )
                return equipment_list
        except SQLAlchemyError as e:
            logger.error("Error finding all equipment: %s", e)
            return []

    def save(self, equipment: Equipment) -> Optional[Equipment]:
        """Save a new equipment entry."""
        try:
            with self.db_connection.get_session() as session:
                session.add(equipment)
                session.flush()
                session.refresh(equipment)
                return equipment
        except SQLAlchemyError as e:
            logger.error("Error saving equipment: %s", e)
            return None

    def update(self, equipment_id: int, updated_data: dict) -> Optional[Equipment]:
        """Update an equipment with new field values."""
        try:
            with self.db_connection.get_session() as session:
                equipment = session.get(Equipment, equipment_id)
                if not equipment:
                    return None

                for key, value in updated_data.items():
                    if hasattr(equipment, key):
                        setattr(equipment, key, value)

                session.flush()
                session.refresh(equipment)
                return equipment
        except SQLAlchemyError as e:
            logger.error("Error updating equipment ID %d: %s", equipment_id, e)
            return None

    def update_production_order_code(
        self, equipment_id: int, production_order_code: str
    ) -> bool:
        """Update only the production order code of the equipment."""
        try:
            with self.db_connection.get_session() as session:
                equipment = session.get(Equipment, equipment_id)
                if not equipment:
                    return False

                equipment.production_order_code = production_order_code
                session.flush()
                return True
        except SQLAlchemyError as e:
            logger.error(
                "Error updating production order code for equipment ID %d: %s",
                equipment_id,
                e,
            )
            return False

    def delete(self, equipment_id: int) -> bool:
        """Delete an equipment by its ID."""
        try:
            with self.db_connection.get_session() as session:
                equipment = session.get(Equipment, equipment_id)
                if not equipment:
                    return False

                session.delete(equipment)
                session.flush()
                return True
        except SQLAlchemyError as e:
            logger.error("Error deleting equipment ID %d: %s", equipment_id, e)
            return False
