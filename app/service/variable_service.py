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
                raise NotFoundException(
                    "Variable with ID '%s' not found." % variable_id
                )
            return variable
        except Exception as e:
            logger.error(
                "Error fetching variable by ID '%s': %s", variable_id, e, exc_info=True
            )
            raise ServiceException("Unable to fetch variable.") from e

    def get_by_equipment_id(self, equipment_id: int) -> List[Variable]:
        try:
            return self.variable_dao.find_by_equipment_id(equipment_id)
        except Exception as e:
            logger.error(
                "Error fetching variables for equipment ID '%s': %s",
                equipment_id,
                e,
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
                "Error fetching variables for equipment ID '%s' and operation type '%s': %s",
                equipment_id,
                operation_type,
                e,
                exc_info=True,
            )
            raise ServiceException("Unable to fetch variables.") from e

    def get_variable_by_key(self, equipment_id: int, key: str) -> VariableDTO:
        try:
            variable = self.variable_dao.find_by_key(equipment_id, key)
            if not variable:
                raise NotFoundException(
                    "Variable with key '%s' not found for equipment ID '%s'."
                    % (key, equipment_id)
                )
            return VariableDTO(
                equipment_id=variable.equipment_id,
                category=variable.category or "",
                operation_type=variable.operation_type,
                value=variable.value,
                key=variable.key,
            )
        except Exception as e:
            logger.error(
                "Error fetching variable by key '%s' for equipment ID '%s': %s",
                key,
                equipment_id,
                e,
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
                "No variable found for equipment_id=%s and key='%s'",
                equipment_id,
                key,
            )
            return None

        logger.debug(
            "Retrieved variable '%s' for equipment_id=%s: %s",
            key,
            equipment_id,
            variable,
        )
        return variable

    def get_variables_by_equipment_id_category_operation_type(
        self, equipment_id: int, category: str, operation_type: str
    ) -> List[Variable]:
        try:
            variables = self.variable_dao.find_by_equipment_id_category_operation_type(
                equipment_id, category, operation_type
            )

            if not variables:
                raise NotFoundException(
                    "No variables found for equipment ID %s, category %s, and operation type %s."
                    % (equipment_id, category, operation_type)
                )

            return variables
        except Exception as e:
            raise ServiceException(f"Error retrieving variables: {str(e)}")

    def get_all_variables(self) -> List[Variable]:
        try:
            return self.variable_dao.find_all()
        except Exception as e:
            logger.error("Error fetching all variables: %s", e, exc_info=True)
            raise ServiceException("Unable to fetch variables.") from e

    def save_variable(self, variable: Variable) -> Variable:
        try:
            existing_variable = self.variable_dao.find_by_equipment_id_and_key(
                variable.equipment_id, variable.key
            )
            if existing_variable:
                raise ConflictException(
                    "Variable with key '%s' already exists for equipment ID '%s'."
                    % (variable.key, variable.equipment_id)
                )

            saved_variable = self.variable_dao.save(variable)
            if saved_variable:
                logger.info(
                    "Created variable '%s' for equipment ID %s.",
                    saved_variable.key,
                    saved_variable.equipment_id,
                )
            return saved_variable
        except Exception as e:
            logger.error(
                "Error saving variable '%s': %s", variable.key, e, exc_info=True
            )
            raise ServiceException("Unable to save variable.") from e

    def update_variable(self, variable_id: int, updated_data: dict) -> Variable:
        try:
            updated_variable = self.variable_dao.update(variable_id, updated_data)
            if not updated_variable:
                raise NotFoundException(
                    "Variable with ID '%s' not found." % variable_id
                )

            logger.info(
                "Updated variable '%s' for equipment ID %s.",
                updated_variable.key,
                updated_variable.equipment_id,
            )
            return updated_variable
        except Exception as e:
            logger.error(
                "Error updating variable '%s': %s", variable_id, e, exc_info=True
            )
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
                    "Missing required fields for variable '%s': %s",
                    key,
                    ", ".join(missing_fields),
                )

            variable = self.variable_dao.find_by_equipment_id_and_key(equipment_id, key)

            if variable:
                logger.info(
                    "Updating existing variable '%s' for equipment ID %s.",
                    key,
                    equipment_id,
                )
                return self.variable_dao.update(variable.id, variable_data)

            logger.info(
                "Creating new variable '%s' for equipment ID %s.", key, equipment_id
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
                "Error creating or updating variable '%s': %s", key, e, exc_info=True
            )
            raise ServiceException(
                "Unable to create or update variable '%s'." % key
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
                    "Variable with key '%s' for equipment ID '%s' not found."
                    % (key, equipment_id)
                )

            logger.info(
                "Updated value for variable '%s' in equipment ID %s.",
                key,
                equipment_id,
            )
            return updated_variable
        except Exception as e:
            logger.error(
                "Error updating variable '%s' for equipment ID '%s': %s",
                key,
                equipment_id,
                e,
                exc_info=True,
            )
            raise ServiceException("Unable to update variable value.") from e

    def delete_variable(self, variable_id: int) -> bool:
        try:
            deleted = self.variable_dao.delete(variable_id)
            if not deleted:
                raise NotFoundException(
                    "Variable with ID '%s' not found." % variable_id
                )

            logger.info("Deleted variable with ID %s.", variable_id)
            return True
        except Exception as e:
            logger.error(
                "Error deleting variable ID %s: %s", variable_id, e, exc_info=True
            )
            raise ServiceException("Unable to delete variable.") from e
