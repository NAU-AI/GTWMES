from utility.logger import Logger
from exception.Exception import NotFoundException, ServiceException
from database.dao.equipment_output_dao import EquipmentOutputDAO
from model.equipment_output import EquipmentOutput

logger = Logger.get_logger(__name__)


class EquipmentOutputService:
    def __init__(self, equipment_output_dao: EquipmentOutputDAO = None):
        self.equipment_output_dao = equipment_output_dao or EquipmentOutputDAO()

    def save(self, output: EquipmentOutput) -> EquipmentOutput:
        try:
            saved_output = self.equipment_output_dao.save(output)
            logger.info(
                f"Saved equipment output '{saved_output.code}' with ID {saved_output.id}"
            )
            return saved_output
        except Exception as e:
            logger.error(f"Error saving equipment output: {e}", exc_info=True)
            raise ServiceException("Unable to save equipment output.") from e

    def create_output(self, equipment_id: int, output_data: dict) -> EquipmentOutput:
        try:
            output = EquipmentOutput(
                equipment_id=equipment_id, code=output_data["code"]
            )

            saved_output = self.equipment_output_dao.save(output)
            logger.info(
                f"Created new equipment output '{saved_output.code}' for equipment ID {saved_output.equipment_id}"
            )
            return saved_output

        except Exception as e:
            logger.error(
                f"Error creating equipment output for '{output_data.get('code')}' on equipment ID {equipment_id}: {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to create equipment output.") from e

    def find_by_equipment_id_and_code(
        self, equipment_id: int, code: str
    ) -> EquipmentOutput:
        try:
            return self.equipment_output_dao.find_by_equipment_id_and_code(
                equipment_id, code
            )
        except Exception as e:
            logger.error(
                f"Error finding output with equipment ID '{equipment_id}' and code '{code}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to find equipment output.") from e

    def get_output_by_id(self, output_id: int) -> EquipmentOutput:
        try:
            if output := self.equipment_output_dao.find_by_id(output_id):
                return output
            else:
                raise NotFoundException(
                    f"Equipment output with ID '{output_id}' not found"
                )
        except Exception as e:
            logger.error(
                f"Error fetching equipment output by ID '{output_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch equipment output.") from e

    def get_by_equipment_id(self, equipment_id: int) -> list[EquipmentOutput]:
        try:
            return self.equipment_output_dao.find_by_equipment_id(equipment_id)
        except Exception as e:
            logger.error(
                f"Error fetching equipment outputs for equipment ID '{equipment_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch equipment outputs.") from e

    def get_all_outputs(self) -> list[EquipmentOutput]:
        try:
            return self.equipment_output_dao.find_all()
        except Exception as e:
            logger.error("Error fetching all equipment outputs.", exc_info=True)
            raise ServiceException("Unable to fetch all equipment outputs.") from e

    def update_output(self, output_id: int, new_variable_id: int) -> EquipmentOutput:
        try:
            existing_output = self.equipment_output_dao.find_by_id(output_id)
            if not existing_output:
                raise NotFoundException(
                    f"Equipment output with ID '{output_id}' not found"
                )

            existing_output.variable_id = new_variable_id

            self.equipment_output_dao.save(existing_output)
            logger.info(
                f"Updated variable for equipment output ID {existing_output.id} to variable ID {new_variable_id}"
            )

            return existing_output
        except Exception as e:
            logger.error(f"Error updating equipment output: {e}", exc_info=True)
            raise ServiceException("Unable to update equipment output.") from e

    def delete_output(self, output_id: int) -> dict:
        try:
            deleted = self.equipment_output_dao.delete(output_id)
            if not deleted:
                raise NotFoundException(
                    f"Equipment output with ID '{output_id}' not found"
                )

            logger.info(f"Deleted equipment output with ID {output_id}")
            return {
                "message": f"Equipment output with ID {output_id} deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting equipment output: {e}", exc_info=True)
            raise ServiceException("Unable to delete equipment output.") from e
