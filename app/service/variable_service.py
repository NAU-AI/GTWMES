from dao.variable_dao import VariableDAO
from model import Variable
from app.exception import NotFoundException, ServiceException
from app.utility.logger import Logger

logger = Logger.get_logger(__name__)


class VariableService:
    def __init__(self, variable_dao: VariableDAO = None):
        self.variable_dao = variable_dao or VariableDAO()

    def get_variable_by_id(self, variable_id: int) -> Variable:
        try:
            if variable := self.variable_dao.find_by_id(variable_id):
                return variable
            else:
                raise NotFoundException(f"Variable with ID '{variable_id}' not found.")
        except Exception as e:
            logger.error(
                f"Error fetching variable by ID '{variable_id}': {e}", exc_info=True
            )
            raise ServiceException("Unable to fetch variable.") from e

    def get_by_equipment_id(self, equipment_id: int) -> list[Variable]:
        try:
            return self.variable_dao.find_by_equipment_id(equipment_id)
        except Exception as e:
            logger.error(
                f"Error fetching variables for equipment ID '{equipment_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch variables.") from e

    def get_by_equipment_output_id(self, equipment_output_id: int) -> list[Variable]:
        try:
            return self.variable_dao.find_by_equipment_output_id(equipment_output_id)
        except Exception as e:
            logger.error(
                f"Error fetching variables for equipment output ID '{equipment_output_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch variables.") from e

    def get_all_variables(self) -> list[Variable]:
        try:
            return self.variable_dao.find_all()
        except Exception as e:
            logger.error("Error fetching all variables.", exc_info=True)
            raise ServiceException("Unable to fetch variables.") from e

    def save_variable(self, variable: Variable) -> Variable:
        try:
            saved_variable = self.variable_dao.save(variable)
            logger.info(
                f"Created variable '{saved_variable.key}' for equipment ID {saved_variable.equipment_id}."
            )
            return saved_variable
        except Exception as e:
            logger.error(f"Error saving variable '{variable.key}': {e}", exc_info=True)
            raise ServiceException("Unable to save variable.") from e

    def update_variable(self, variable: Variable) -> Variable:
        try:
            existing_variable = self.variable_dao.find_by_id(variable.id)
            if not existing_variable:
                raise NotFoundException(f"Variable with ID '{variable.id}' not found.")

            existing_variable.key = variable.key
            existing_variable.db_address = variable.db_address
            existing_variable.offset_byte = variable.offset_byte
            existing_variable.offset_bit = variable.offset_bit
            existing_variable.type = variable.type
            existing_variable.operation_type = variable.operation_type

            updated_variable = self.variable_dao.save(existing_variable)
            logger.info(
                f"Updated variable '{updated_variable.key}' for equipment ID {updated_variable.equipment_id}."
            )
            return updated_variable
        except Exception as e:
            logger.error(f"Error updating variable '{variable.id}': {e}", exc_info=True)
            raise ServiceException("Unable to update variable.") from e

    def delete_variable(self, variable_id: int) -> bool:
        try:
            deleted = self.variable_dao.delete(variable_id)
            if not deleted:
                raise NotFoundException(f"Variable with ID '{variable_id}' not found.")

            logger.info(f"Deleted variable with ID {variable_id}.")
            return True
        except Exception as e:
            logger.error(
                f"Error deleting variable ID {variable_id}: {e}", exc_info=True
            )
            raise ServiceException("Unable to delete variable.") from e
