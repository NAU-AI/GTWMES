from sqlalchemy.orm import Session
from typing import List, Optional
from model.dto.variable import VariableDTO
from model.converter.variable_converter import VariableConverter
from model.variable import Variable
from database.dao.variable_dao import VariableDAO
from exception.Exception import NotFoundException, ServiceException
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class VariableService:
    def __init__(self, session: Session, variable_dao: Optional[VariableDAO] = None):
        self.session = session
        self.variable_dao = variable_dao or VariableDAO(session)

    def get_by_equipment_id_and_operation_type(
        self, equipment_id: int, operation_type: str
    ) -> List[VariableDTO]:
        try:
            variables = self.variable_dao.find_by_equipment_id_and_operation_type(
                equipment_id, operation_type
            )
            return VariableConverter.to_dto_list(variables)
        except Exception as e:
            logger.error(
                "Error fetching variables for equipment ID '%s' and operation type '%s': %s",
                equipment_id,
                operation_type,
                e,
                exc_info=True,
            )
            raise ServiceException("Unable to fetch variables.") from e

    def get_by_equipment_id_and_key(
        self, equipment_id: int, key: str
    ) -> Optional[VariableDTO]:
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
        return VariableConverter.to_dto(variable)

    def get_variables_by_equipment_id_category_operation_type(
        self, equipment_id: int, category: str, operation_type: str
    ) -> List[VariableDTO]:
        try:
            variables = self.variable_dao.find_by_equipment_id_category_operation_type(
                equipment_id, category, operation_type
            )

            if not variables:
                raise NotFoundException(
                    "No variables found for equipment ID %s, category %s, and operation type %s.",
                    equipment_id,
                    category,
                    operation_type,
                )

            return VariableConverter.to_dto_list(variables)
        except Exception as e:
            raise ServiceException(f"Error retrieving variables: {str(e)}")

    def create_or_update_variable(
        self, equipment_id: int, variable_data: dict, variable_key: Optional[str] = None
    ) -> VariableDTO:
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
                updated_variable = self.variable_dao.update(variable.id, variable_data)
                return VariableConverter.to_dto(updated_variable)

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
            return VariableConverter.to_dto(self.variable_dao.save(new_variable))

        except Exception as e:
            logger.error(
                f"Error creating or updating variable '{key}': {e}", exc_info=True
            )
            raise ServiceException(
                f"Unable to create or update variable '{key}'."
            ) from e

    def update_variable_value(
        self, equipment_id: int, key: str, new_value: dict
    ) -> VariableDTO:
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
            return VariableConverter.to_dto(updated_variable)
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
