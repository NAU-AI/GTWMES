from sqlalchemy.orm import Session
from typing import List, Optional
from model.dto.variable_dto import VariableDTO
from database.dao.variable_dao import VariableDAO
from model.variable import Variable
from exception.Exception import NotFoundException, ServiceException, ConflictException
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class VariableService:
    def __init__(self, session: Session, variable_dao: Optional[VariableDAO] = None):
        self.session = session
        self.variable_dao = variable_dao or VariableDAO(session)

    def get_variable_by_id(self, variable_id: int) -> Variable:
        try:
            variable = self.variable_dao.find_by_id(variable_id)
            if not variable:
                raise NotFoundException(f"Variable with ID '{variable_id}' not found.")
            return variable
        except Exception as e:
            logger.error(
                f"Error fetching variable by ID '{variable_id}': {e}", exc_info=True
            )
            raise ServiceException("Unable to fetch variable.") from e

    def get_by_equipment_id(self, equipment_id: int) -> List[Variable]:
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
    ) -> List[Variable]:
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

    def get_variable_by_key(self, equipment_id: int, key: str) -> VariableDTO:
        try:
            variable = self.variable_dao.find_by_key(equipment_id, key)
            if not variable:
                raise NotFoundException(
                    f"Variable with key '{key}' not found for equipment ID '{equipment_id}'."
                )
            return VariableDTO(
                equipment_id=variable.equipment_id,
                category=variable.category,
                operation_type=variable.operation_type,
                value=variable.value,
                key=variable.key,
            )
        except Exception as e:
            logger.error(
                f"Error fetching variable by key '{key}' for equipment ID '{equipment_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch variable by key.") from e

    def get_by_equipment_id_and_key(
        self, equipment_id: int, key: str
    ) -> Optional[Variable]:
        if not equipment_id or not key:
            logger.warning("Invalid parameters: equipment_id and key must be provided.")
            return None

        variable = self.variable_dao.find_by_equipment_id_and_key(equipment_id, key)

        if not variable:
            logger.info(
                f"No variable found for equipment_id={equipment_id} and key='{key}'"
            )
            return None

        logger.debug(
            f"Retrieved variable '{key}' for equipment_id={equipment_id}: {variable}"
        )
        return variable

    def get_variables_by_equipment_id_category_operation_type(
        self, equipment_id: int, category: str, operation_type: str
    ) -> List[VariableDTO]:
        try:
            variables = self.variable_dao.find_by_equipment_id_category_operation_type(
                equipment_id, category, operation_type
            )

            if not variables:
                raise NotFoundException(
                    f"No variables found for equipment ID {equipment_id}, category {category}, and operation type {operation_type}."
                )

            variable_dtos = [
                VariableDTO(
                    equipment_id=variable.equipment_id,
                    category=variable.category,
                    operation_type=variable.operation_type,
                    value=variable.value,
                    key=variable.key,  # Include key in the DTO
                )
                for variable in variables
            ]

            return variable_dtos

        except Exception as e:
            logger.error(f"Error fetching variables: {e}", exc_info=True)
            raise ServiceException("Unable to fetch variables.") from e

    def get_all_variables(self) -> List[Variable]:
        try:
            return self.variable_dao.find_all()
        except Exception as e:
            logger.error("Error fetching all variables.", exc_info=True)
            raise ServiceException("Unable to fetch variables.") from e

    def save_variable(self, variable: Variable) -> Variable:
        try:
            existing_variable = self.variable_dao.find_by_equipment_id_and_key(
                variable.equipment_id, variable.key
            )
            if existing_variable:
                raise ConflictException(
                    f"Variable with key '{variable.key}' already exists for equipment ID '{variable.equipment_id}'."
                )

            saved_variable = self.variable_dao.save(variable)
            logger.info(
                f"Created variable '{saved_variable.key}' for equipment ID {saved_variable.equipment_id}."
            )
            return saved_variable
        except Exception as e:
            logger.error(f"Error saving variable '{variable.key}': {e}", exc_info=True)
            raise ServiceException("Unable to save variable.") from e

    def update_variable(self, variable_id: int, updated_data: dict) -> Variable:
        try:
            updated_variable = self.variable_dao.update(variable_id, updated_data)
            if not updated_variable:
                raise NotFoundException(f"Variable with ID '{variable_id}' not found.")

            logger.info(
                f"Updated variable '{updated_variable.key}' for equipment ID {updated_variable.equipment_id}."
            )
            return updated_variable
        except Exception as e:
            logger.error(f"Error updating variable '{variable_id}': {e}", exc_info=True)
            raise ServiceException("Unable to update variable.") from e

    def create_or_update_variable(
        self, equipment_id: int, variable_data: dict, variable_key: Optional[str] = None
    ) -> Variable:
        try:
            key = variable_key or variable_data.get("key")
            if not key:
                raise ValueError("Variable key cannot be empty.")

            required_fields = [
                "dbAddress",
                "offsetByte",
                "offsetBit",
                "type",
                "operationType",
                "category",
            ]
            missing_fields = [
                field for field in required_fields if field not in variable_data
            ]
            if missing_fields:
                raise ValueError(
                    f"Missing required fields for variable '{key}': {', '.join(missing_fields)}"
                )

            variable = self.variable_dao.find_by_equipment_id_and_key(equipment_id, key)

            if variable:
                logger.info(
                    f"Updating existing variable '{key}' for equipment ID {equipment_id}."
                )
                return self.variable_dao.update(variable.id, variable_data)

            logger.info(
                f"Creating new variable '{key}' for equipment ID {equipment_id}."
            )
            new_variable = Variable(
                equipment_id=equipment_id,
                key=key,
                db_address=variable_data["dbAddress"],
                offset_byte=variable_data["offsetByte"],
                offset_bit=variable_data["offsetBit"],
                type=variable_data["type"],
                operation_type=variable_data["operationType"],
                category=variable_data["category"],
            )
            return self.variable_dao.save(new_variable)

        except Exception as e:
            logger.error(
                f"Error creating or updating variable '{key}': {e}", exc_info=True
            )
            raise ServiceException(
                f"Unable to create or update variable '{key}'."
            ) from e

    def update_variable_value(
        self, equipment_id: int, key: str, new_value: dict
    ) -> Variable:
        try:
            updated_variable = self.variable_dao.update_value_by_key(
                equipment_id, key, new_value
            )
            if not updated_variable:
                raise NotFoundException(
                    f"Variable with key '{key}' for equipment ID '{equipment_id}' not found."
                )

            logger.info(
                f"Updated value for variable '{key}' in equipment ID {equipment_id}."
            )
            return updated_variable
        except Exception as e:
            logger.error(
                f"Error updating variable '{key}' for equipment ID '{equipment_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to update variable value.") from e

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
