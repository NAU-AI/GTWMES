from typing import Optional

from database.dao.equipment_dao import EquipmentDAO
from exception.Exception import NotFoundException, ServiceException
from model.converter.equipment_converter import EquipmentConverter
from model.dto.equipment_dto import EquipmentDTO
from model.equipment import Equipment
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from sqlalchemy.orm import Session
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class EquipmentService:
    def __init__(self, session: Session):
        self.session = session
        self.equipment_dao = EquipmentDAO(self.session)

    def get_equipment_by_code(self, code: str) -> EquipmentDTO:
        if not code:
            raise ValueError("Equipment code cannot be empty")
        try:
            equipment = self.equipment_dao.find_by_code(code)
            if not equipment:
                raise NotFoundException("Equipment with code '%s' not found", code)
            return EquipmentConverter.to_dto(equipment)
        except Exception as e:
            logger.error(
                "Error fetching equipment by code '%s': %s", code, e, exc_info=True
            )
            raise ServiceException("Unable to fetch equipment by code.") from e

    def get_all_equipment(self) -> list[EquipmentDTO]:
        try:
            equipment_list = self.equipment_dao.find_all()
            return EquipmentConverter.to_dto_list(equipment_list)
        except ProgrammingError as e:
            logger.warning("Unable to refresh equipment due to database error: %s", e)
            return []
        except Exception as e:
            logger.error(
                "Error fetching and refreshing equipment: %s", e, exc_info=True
            )
            raise ServiceException("Unable to fetch and refresh equipment.") from e

    def create_or_update_equipment(
        self, code: str, ip: str, p_timer_communication_cycle: Optional[int]
    ) -> EquipmentDTO:
        try:
            existing_equipment = self.equipment_dao.find_by_code(code)
            if existing_equipment:
                logger.info("Updating existing equipment '%s'.", code)
                updated_data = {
                    "ip": ip,
                    "p_timer_communication_cycle": p_timer_communication_cycle,
                }
                updated_equipment = self.equipment_dao.update(
                    existing_equipment.id, updated_data
                )
                return EquipmentConverter.to_dto(updated_equipment)

            logger.info("Creating new equipment '%s'.", code)
            new_equipment = Equipment(
                code=code,
                ip=ip,
                p_timer_communication_cycle=p_timer_communication_cycle,
            )
            saved_equipment = self.equipment_dao.save(new_equipment)
            if not saved_equipment:
                raise ServiceException(f"Failed to create equipment '{code}'.")
            return EquipmentConverter.to_dto(saved_equipment)

        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "Database error creating or updating equipment: %s", e, exc_info=True
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
                    "Assigned production order '%s' to equipment ID %s.",
                    production_order_code,
                    equipment_id,
                )
            return success
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "Database error starting production order: %s", e, exc_info=True
            )
            raise ServiceException("Unable to start production order.") from e

    def complete_production_order(self, equipment_id: int) -> bool:
        try:
            success = self.equipment_dao.update_production_order_code(equipment_id, "")
            if success:
                logger.info(
                    "Completed production order for equipment ID %s.", equipment_id
                )
            return success
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "Database error completing production order: %s", e, exc_info=True
            )
            raise ServiceException("Unable to complete production order.") from e
