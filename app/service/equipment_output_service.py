from app.utility.logger import Logger
from app.exception.Exception import NotFoundException, ServiceException
from dao.equipment_output_dao import EquipmentOutputDAO
from dao.equipment_dao import EquipmentDAO
from model import EquipmentOutput

logger = Logger.getLogger(__name__)


class EquipmentOutputService:
    def __init__(
        self,
        equipment_output_dao: EquipmentOutputDAO = None,
        equipment_dao: EquipmentDAO = None,
    ):
        self.equipment_output_dao = equipment_output_dao or EquipmentOutputDAO()
        self.equipment_dao = equipment_dao or EquipmentDAO()

    def create_output(self, output: EquipmentOutput) -> EquipmentOutput:
        try:
            saved_output = self.equipment_output_dao.save(output)
            logger.info(
                f"Created new equipment output '{output.code}' for equipment ID {output.equipment_id}"
            )
            return saved_output
        except Exception as e:
            logger.error(f"Error creating equipment output: {e}", exc_info=True)
            raise ServiceException("Unable to create equipment output.") from e

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
            if not self.equipment_dao.find_by_id(equipment_id):
                raise NotFoundException(f"Equipment with ID '{equipment_id}' not found")

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

    def create_outputs_for_equipment(
        self, equipment_id: int, outputs: list[EquipmentOutput]
    ) -> list[EquipmentOutput]:
        try:
            equipment = self.equipment_dao.find_by_id(equipment_id)
            if not equipment:
                raise NotFoundException(f"Equipment with ID '{equipment_id}' not found")

            for output in outputs:
                output.equipment_id = equipment_id

            saved_outputs = self.equipment_output_dao.bulk_save(outputs)
            logger.info(
                f"Created {len(outputs)} equipment outputs for equipment ID {equipment_id}"
            )

            return saved_outputs
        except Exception as e:
            logger.error(
                f"Error creating outputs for equipment '{equipment_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to create equipment outputs.") from e
