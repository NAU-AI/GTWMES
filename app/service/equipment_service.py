from exception.Exception import ConflictException, ServiceException, NotFoundException
from utility.logger import Logger
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError
from sqlalchemy.orm import Session
from database.dao.equipment_dao import EquipmentDAO
from model.equipment import Equipment
from typing import List, Optional

logger = Logger.get_logger(__name__)


class EquipmentService:
    def __init__(self, session: Session):
        self.session = session
        self.equipment_dao = EquipmentDAO(self.session)

    def get_equipment_by_code(self, code: str) -> Equipment:
        if not code:
            raise ValueError("Equipment code cannot be empty")
        try:
            equipment = self.equipment_dao.find_by_code(code)
            if not equipment:
                raise NotFoundException(f"Equipment with code '{code}' not found")
            return equipment
        except Exception as e:
            logger.error(
                f"Error fetching equipment by code '{code}': {e}", exc_info=True
            )
            raise ServiceException("Unable to fetch equipment by code.") from e

    def get_all_equipment(self):
        try:
            return self.equipment_dao.find_all()
        except ProgrammingError as e:
            logger.warning(f"Unable to fetch equipment due to database error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching all equipment: {e}", exc_info=True)
            raise ServiceException("Unable to fetch all equipment.") from e

    def get_all_equipment_refreshed(self):
        try:
            return self.equipment_dao.find_all()
        except ProgrammingError as e:
            logger.warning(f"Unable to refresh equipment due to database error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching and refreshing equipment: {e}", exc_info=True)
            raise ServiceException("Unable to fetch and refresh equipment.") from e

    def insert_equipment(self, equipment: Equipment) -> Equipment:
        try:
            existing_equipment = self.equipment_dao.find_by_code(equipment.code)
            if existing_equipment:
                raise ConflictException(
                    f"Equipment with code '{equipment.code}' already exists"
                )
            saved_equipment = self.equipment_dao.save(equipment)
            logger.info(
                f"Inserted new equipment '{saved_equipment.code}' with ID {saved_equipment.id}"
            )
            return saved_equipment
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error inserting equipment: {e}", exc_info=True)
            raise ServiceException("Unable to insert new equipment.") from e

    def create_or_update_equipment(
        self, code: str, ip: str, p_timer_communication_cycle: Optional[int]
    ) -> Equipment:
        try:
            existing_equipment = self.equipment_dao.find_by_code(code)
            if existing_equipment:
                logger.info(f"Updating existing equipment '{code}'.")
                updated_data = {
                    "ip": ip,
                    "p_timer_communication_cycle": p_timer_communication_cycle,
                }
                updated_equipment = self.equipment_dao.update(
                    existing_equipment.id, updated_data
                )
                return updated_equipment

            logger.info(f"Creating new equipment '{code}'.")
            new_equipment = Equipment(
                code=code,
                ip=ip,
                p_timer_communication_cycle=p_timer_communication_cycle,
            )
            return self.equipment_dao.save(new_equipment)
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                f"Database error creating or updating equipment: {e}", exc_info=True
            )
            raise ServiceException("Unable to create or update equipment.") from e

    def start_production_order(
        self, equipment_id: int, production_order_code: str
    ) -> bool:
        try:
            success = self.equipment_dao.update_production_order_code(
                equipment_id, production_order_code
            )
            if success:
                logger.info(
                    f"Assigned production order '{production_order_code}' to equipment ID {equipment_id}."
                )
            return success
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                f"Database error starting production order: {e}", exc_info=True
            )
            raise ServiceException("Unable to start production order.") from e

    def complete_production_order(self, equipment_id: int) -> bool:
        try:
            success = self.equipment_dao.update_production_order_code(equipment_id, "")
            if success:
                logger.info(
                    f"Completed production order for equipment ID {equipment_id}."
                )
            return success
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                f"Database error completing production order: {e}", exc_info=True
            )
            raise ServiceException("Unable to complete production order.") from e
