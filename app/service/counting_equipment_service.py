from asyncio.log import logger
from utility.scheduler import Scheduler
from exception.Exception import (
    ConflictException,
    DatabaseException,
    NotFoundException,
    ServiceException,
)
from database.dao.equipment_output_dao import EquipmentOutputDAO
from database.dao.counting_equipment_dao import CountingEquipmentDAO


class CountingEquipmentService:
    def __init__(
        self, counting_equipment_dao=None, equipment_output_dao=None, scheduler=None
    ):
        self.counting_equipment_dao = counting_equipment_dao or CountingEquipmentDAO()
        self.equipment_output_dao = equipment_output_dao or EquipmentOutputDAO()
        self.scheduler = scheduler or Scheduler()

    def update_equipment_configuration(self, data):
        self._validate_equipment_update_data(data)

        try:
            existing_equipment = self._get_equipment_or_raise(data["equipmentCode"])

            updated_id = self.counting_equipment_dao.update_config_equipment(
                {
                    "equipmentCode": existing_equipment.code,
                    "pTimerCommunicationCycle": data["pTimerCommunicationCycle"],
                }
            )

            logger.info(f"Updated equipment with code '{data['equipmentCode']}'")

            task_id = f"equipment_{existing_equipment.id}"
            new_interval = data["pTimerCommunicationCycle"]

            existing_equipment.p_timer_communication_cycle = new_interval
            success = self.scheduler.update_timer(task_id, new_interval)

            if not success:
                logger.warning(
                    f"Failed to update timer for equipment with code '{data['equipmentCode']}'"
                )

            return {"id": updated_id, "message": "Equipment successfully updated"}
        except Exception as e:
            logger.error(f"Error while updating equipment: {e}", exc_info=True)
            raise ServiceException("Unable to update equipment configuration.") from e

    def get_equipment_by_code(self, code):
        if not code:
            raise ValueError("Equipment code cannot be empty")

        try:
            equipment = self.counting_equipment_dao.get_equipment_by_code(code)
            if not equipment:
                raise NotFoundException(f"No equipment found with code '{code}'")
            logger.info(f"Fetched equipment with code '{code}'")
            return equipment
        except NotFoundException as e:
            logger.warning(str(e))
            raise
        except Exception as e:
            logger.error(
                f"Error while fetching equipment by code '{code}': {e}", exc_info=True
            )
            raise ServiceException("Unable to fetch equipment by code.") from e

    def get_equipment_by_id(self, equipment_id):
        if not equipment_id:
            raise ValueError("equipment_id cannot be null or empty.")

        try:
            equipment = self.counting_equipment_dao.get_equipment_by_id(equipment_id)
            if not equipment:
                logger.warning(f"No equipment found for ID: {equipment_id}")
            return equipment
        except DatabaseException as e:
            logger.error(
                f"Database error while fetching equipment with ID '{equipment_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Failed to fetch equipment by ID.") from e
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching equipment with ID '{equipment_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("An unexpected error occurred.") from e

    def get_all_equipment(self):
        try:
            equipment_list = self.counting_equipment_dao.get_all_equipment()
            return equipment_list
        except Exception as e:
            logger.error("Error while fetching all equipment.", exc_info=True)
            raise ServiceException("Unable to fetch all equipment.") from e

    def insert_config_equipment(self, data):
        self._validate_equipment_data(data)

        try:
            if self.counting_equipment_dao.get_equipment_by_code(data["equipmentCode"]):
                raise ConflictException(
                    f"Equipment with code '{data['equipmentCode']}' already exists"
                )

            equipment_id = self.counting_equipment_dao.insert_config_equipment(data)
            logger.info(f"Inserted new equipment with ID {equipment_id}")
            return {"id": equipment_id, "message": "Equipment successfully inserted"}
        except ConflictException as e:
            logger.warning(str(e))
            raise
        except Exception as e:
            logger.error(f"Error while inserting equipment: {e}", exc_info=True)
            raise ServiceException("Unable to insert new equipment.") from e

    @staticmethod
    def _validate_equipment_data(data):
        required_fields = {"equipmentCode", "pTimerCommunicationCycle"}
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary")
        if not required_fields.issubset(data.keys()):
            missing_fields = required_fields - data.keys()
            raise ValueError(f"Missing required fields: {missing_fields}")
        if not isinstance(data["pTimerCommunicationCycle"], int):
            raise ValueError("pTimerCommunicationCycle must be an integer")
        if not data["equipmentCode"]:
            raise ValueError("equipmentCode cannot be empty")

    @staticmethod
    def _validate_equipment_update_data(data):
        if "equipmentCode" not in data or not data["equipmentCode"]:
            raise ValueError("Equipment code is required")
        if "pTimerCommunicationCycle" not in data or not isinstance(
            data["pTimerCommunicationCycle"], int
        ):
            raise ValueError("pTimerCommunicationCycle must be an integer")

    def _get_equipment_or_raise(self, code):
        equipment = self.counting_equipment_dao.get_equipment_by_code(code)
        if not equipment:
            raise Exception.NotFoundException(f"Equipment with code '{code}' not found")
        return equipment
