from typing import List, Optional

from database.dao.equipment_dao import EquipmentDAO
from exception.Exception import NotFoundException, ServiceException
from model.dto.equipment_dto import EquipmentDTO
from model.equipment import Equipment
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class EquipmentService:
    def __init__(self, equipment_dao: EquipmentDAO):
        self.equipment_dao = equipment_dao

    def get_equipment_by_code(self, code: str) -> EquipmentDTO:
        if not code:
            raise ValueError("Equipment code cannot be empty")
        try:
            equipment = self.equipment_dao.find_by_code(code)
            if not equipment:
                raise NotFoundException(f"Equipment with code '{code}' not found")
            return self._convert_to_dto([equipment])[0]  # Convert single object to DTO
        except Exception as e:
            logger.error(
                "Error fetching equipment by code '%s': %s", code, e, exc_info=True
            )
            raise ServiceException("Unable to fetch equipment by code.") from e

    def get_all_equipment(self) -> List[EquipmentDTO]:
        """Fetch all equipment and convert to DTOs."""
        try:
            equipment_list = self.equipment_dao.find_all()
            return self._convert_to_dto(equipment_list)
        except Exception as e:
            logger.error("Error fetching all equipment: %s", e, exc_info=True)
            raise ServiceException("Unable to fetch all equipment.") from e

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
                return self._convert_to_dto([updated_equipment])[0]

            logger.info("Creating new equipment '%s'.", code)
            new_equipment = Equipment(
                code=code,
                ip=ip,
                p_timer_communication_cycle=p_timer_communication_cycle,
            )
            saved_equipment = self.equipment_dao.save(new_equipment)
            if not saved_equipment:
                raise ServiceException(f"Failed to create equipment '{code}'.")
            return self._convert_to_dto([saved_equipment])[0]

        except Exception as e:
            logger.error(
                "Error creating or updating equipment '%s': %s", code, e, exc_info=True
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
        except Exception as e:
            logger.error(
                "Error starting production order for equipment ID %s: %s",
                equipment_id,
                e,
                exc_info=True,
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
        except Exception as e:
            logger.error(
                "Error completing production order for equipment ID %s: %s",
                equipment_id,
                e,
                exc_info=True,
            )
            raise ServiceException("Unable to complete production order.") from e

    def _convert_to_dto(self, equipment_list: List[Equipment]) -> List[EquipmentDTO]:
        """Convert a list of Equipment objects to a list of EquipmentDTOs."""
        equipment_dto_list = []
        for equipment in equipment_list:
            equipment_dto = EquipmentDTO(
                id=equipment.id,
                code=equipment.code,
                ip=equipment.ip,
                p_timer_communication_cycle=equipment.p_timer_communication_cycle,
                production_order_code=equipment.production_order_code,
            )
            equipment_dto_list.append(equipment_dto)
        return equipment_dto_list
