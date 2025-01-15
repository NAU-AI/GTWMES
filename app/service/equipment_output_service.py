from asyncio.log import logger
from exception.Exception import DatabaseException, ServiceException
from database.dao.equipment_output_dao import EquipmentOutputDAO


class EquipmentOutputService:
    def __init__(self, equipment_output_dao=None):
        self.equipment_output_dao = equipment_output_dao or EquipmentOutputDAO()

    def get_by_equipment_id(self, equipment_id):
        if not equipment_id:
            raise ValueError("equipment_id cannot be empty")

        try:
            outputs = self.equipment_output_dao.get_output_by_equipment_id(equipment_id)
            logger.info(
                f"Fetched {len(outputs)} outputs for equipment ID {equipment_id}"
            )
            return outputs
        except DatabaseException as e:
            logger.error(
                f"Service error while fetching outputs for equipment ID {equipment_id}: {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch equipment outputs.") from e

    def create_outputs_for_equipment(self, counting_equipment_id, output_codes):
        if not counting_equipment_id or not output_codes:
            raise ValueError("counting_equipment_id and output_codes are required")

        try:
            output_ids = self.equipment_output_dao.insert_equipment_output(
                counting_equipment_id, output_codes
            )
            logger.info(
                f"Created {len(output_ids)} outputs for equipment ID {counting_equipment_id}"
            )
            return output_ids
        except DatabaseException as e:
            logger.error(
                f"Service error while creating outputs for equipment ID {counting_equipment_id}: {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to create equipment outputs.") from e
