import logging
from app.exception.Exception import (
    ConflictException,
    NotFoundException,
    ServiceException,
)
from dao.equipment_dao import EquipmentDAO
from dao.equipment_output_dao import EquipmentOutputDAO
from model import Equipment

logger = logging.getLogger(__name__)


class EquipmentService:
    def __init__(
        self,
        equipment_dao: EquipmentDAO = None,
        equipment_output_dao: EquipmentOutputDAO = None,
    ):
        self.equipment_dao = equipment_dao or EquipmentDAO()
        self.equipment_output_dao = equipment_output_dao or EquipmentOutputDAO()

    def update_equipment(self, equipment: Equipment) -> Equipment:
        try:
            existing_equipment = self.equipment_dao.find_by_id(equipment.id)
            if not existing_equipment:
                raise NotFoundException(f"Equipment with ID '{equipment.id}' not found")

            if equipment.ip is not None:
                existing_equipment.ip = equipment.ip
            if equipment.p_timer_communication_cycle is not None:
                existing_equipment.p_timer_communication_cycle = (
                    equipment.p_timer_communication_cycle
                )

            self.equipment_dao.save(existing_equipment)
            logger.info(f"Updated equipment '{equipment.code}'")

            return existing_equipment
        except Exception as e:
            logger.error(f"Error updating equipment: {e}", exc_info=True)
            raise ServiceException("Unable to update equipment.") from e

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

    def get_equipment_by_id(self, equipment_id: int) -> Equipment:
        if not equipment_id:
            raise ValueError("equipment_id cannot be null or empty.")

        try:
            equipment = self.equipment_dao.find_by_id(equipment_id)
            if not equipment:
                raise NotFoundException(f"Equipment with ID '{equipment_id}' not found")

            return equipment
        except Exception as e:
            logger.error(
                f"Error fetching equipment by ID '{equipment_id}': {e}", exc_info=True
            )
            raise ServiceException("An unexpected error occurred.") from e

    def get_all_equipment(self) -> list[Equipment]:
        try:
            return self.equipment_dao.find_all()
        except Exception as e:
            logger.error("Error fetching all equipment.", exc_info=True)
            raise ServiceException("Unable to fetch all equipment.") from e

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

            return self.equipment_dao.find_by_id(saved_equipment.id)
        except Exception as e:
            logger.error(f"Error inserting equipment: {e}", exc_info=True)
            raise ServiceException("Unable to insert new equipment.") from e

    def delete_equipment(self, equipment_id: int) -> dict:
        if not equipment_id:
            raise ValueError("Equipment ID cannot be null or empty.")

        try:
            deleted = self.equipment_dao.delete(equipment_id)
            if not deleted:
                raise NotFoundException(f"Equipment with ID '{equipment_id}' not found")

            logger.info(f"Deleted equipment with ID {equipment_id}")
            return {"message": f"Equipment with ID {equipment_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting equipment: {e}", exc_info=True)
            raise ServiceException("Unable to delete equipment.") from e

    def _get_equipment_by_code(self, code: str) -> Equipment:
        equipment = self.equipment_dao.find_by_code(code)
        if not equipment:
            raise NotFoundException(f"Equipment with code '{code}' not found")
        return equipment

    def _get_equipment_by_id(self, equipment_id: int) -> Equipment:
        equipment = self.equipment_dao.find_by_id(equipment_id)
        if not equipment:
            raise NotFoundException(f"Equipment with ID '{equipment_id}' not found")
        return equipment

    def _validate_equipment_update_data(self, data: dict):
        if "equipmentCode" not in data or not data["equipmentCode"]:
            raise ValueError("Missing or empty 'equipmentCode' in request data")
        if "timerCommunicationCycle" in data and not isinstance(
            data["timerCommunicationCycle"], int
        ):
            raise ValueError("'timerCommunicationCycle' must be an integer")

    def _validate_equipment_data(self, data: dict):
        required_fields = ["code", "ip"]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing or empty '{field}' in request data")
