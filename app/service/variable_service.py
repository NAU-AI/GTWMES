from database.dao.variable_dao import VariableDAO
from model.variable import Variable
from exception.Exception import NotFoundException, ServiceException
from utility.logger import Logger

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

    def get_by_equipment_id_and_operation_type(
        self, equipment_id: int, operation_type: str
    ) -> list[Variable]:
        try:
            return self.variable_dao.find_by_equipment_id_and_operation_type(
                equipment_id, operation_type
            )
        except Exception as e:
            logger.error(
                f"Error fetching variables for equipment ID '{equipment_id}' and operation type '{operation_type}': {e}",
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

    def create_or_update_variable(
        self, equipment_id: int, variable_data: dict, variable_key: str = None
    ) -> Variable:
        try:
            key = variable_key if variable_key else variable_data["key"]

            variable = self.variable_dao.find_by_equipment_id_and_key(equipment_id, key)

            if variable:
                logger.info(
                    f"Updating existing variable '{key}' for equipment ID {equipment_id}."
                )
            else:
                logger.info(
                    f"Creating new variable '{key}' for equipment ID {equipment_id}."
                )
                variable = Variable(equipment_id=equipment_id, key=key)

            variable.db_address = variable_data["dbAddress"]
            variable.offset_byte = variable_data["offsetByte"]
            variable.offset_bit = variable_data["offsetBit"]
            variable.type = variable_data["type"]
            variable.operation_type = variable_data["operationType"]

            return self.variable_dao.save(variable)

        except Exception as e:
            logger.error(
                f"Error creating or updating variable '{key}': {e}", exc_info=True
            )
            raise ServiceException("Unable to create or update variable.") from e

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
