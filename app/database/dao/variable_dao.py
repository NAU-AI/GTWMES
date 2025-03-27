import logging
from typing import List, Optional

from database.connection.db_connection import DatabaseConnection
from model.variable import Variable
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class VariableDAO:
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    def find_by_id(self, variable_id: int) -> Optional[Variable]:
        """Find a variable by its ID."""
        try:
            with self.db_connection.get_session() as session:
                return session.get(Variable, variable_id)
        except SQLAlchemyError as e:
            logger.error("Error finding variable ID %d: %s", variable_id, e)
            return None

    def find_by_equipment_id(self, equipment_id: int) -> List[Variable]:
        """Find all variables for a given equipment."""
        try:
            with self.db_connection.get_session() as session:
                return (
                    session.query(Variable)
                    .filter(Variable.equipment_id == equipment_id)
                    .all()
                )
        except SQLAlchemyError as e:
            logger.error(
                "Error finding variables by equipment ID %d: %s", equipment_id, e
            )
            return []

    def find_by_equipment_id_and_key(
        self, equipment_id: int, key: str
    ) -> Optional[Variable]:
        """Find a variable by equipment ID and key."""
        try:
            with self.db_connection.get_session() as session:
                return (
                    session.query(Variable)
                    .filter(Variable.equipment_id == equipment_id, Variable.key == key)
                    .first()
                )
        except SQLAlchemyError as e:
            logger.error(
                "Error finding variable by key %s and equipment ID %d: %s",
                key,
                equipment_id,
                e,
            )
            return None

    def find_by_equipment_id_and_operation_type(
        self, equipment_id: int, operation_type: str
    ) -> List[Variable]:
        """Find variables by equipment ID and operation type."""
        try:
            with self.db_connection.get_session() as session:
                return (
                    session.query(Variable)
                    .filter(
                        Variable.equipment_id == equipment_id,
                        Variable.operation_type == operation_type,
                    )
                    .all()
                )
        except SQLAlchemyError as e:
            logger.error(
                "Error finding variables by equipment ID %d and operation type %s: %s",
                equipment_id,
                operation_type,
                e,
            )
            return []

    def find_by_all_filters(
        self, equipment_id: int, category: str, operation_type: str
    ) -> List[Variable]:
        """Find variables by equipment ID, category, and operation type."""
        try:
            with self.db_connection.get_session() as session:
                return (
                    session.query(Variable)
                    .filter(
                        Variable.equipment_id == equipment_id,
                        Variable.category == category,
                        Variable.operation_type == operation_type,
                    )
                    .all()
                )
        except SQLAlchemyError as e:
            logger.error(
                "Error finding variables by equipment ID %d, category %s, "
                "operation type %s: %s",
                equipment_id,
                category,
                operation_type,
                e,
            )
            return []

    def find_all(self) -> List[Variable]:
        """Find all variables."""
        try:
            with self.db_connection.get_session() as session:
                return session.query(Variable).all()
        except SQLAlchemyError as e:
            logger.error("Error finding all variables: %s", e)
            return []

    def save(self, variable: Variable) -> Optional[Variable]:
        """Save a new variable."""
        try:
            with self.db_connection.get_session() as session:
                session.add(variable)
                session.flush()
                session.refresh(variable)
                return variable
        except SQLAlchemyError as e:
            logger.error("Error saving variable: %s", e)
            return None

    def update(self, variable_id: int, updated_data: dict) -> Optional[Variable]:
        """Update a variable with new data."""
        try:
            with self.db_connection.get_session() as session:
                variable = session.get(Variable, variable_id)
                if not variable:
                    return None

                for key, value in updated_data.items():
                    if hasattr(variable, key):
                        setattr(variable, key, value)

                session.flush()
                session.refresh(variable)
                return variable
        except SQLAlchemyError as e:
            logger.error("Error updating variable ID %d: %s", variable_id, e)
            return None

    def update_value_by_key(
        self, equipment_id: int, key: str, new_value: dict
    ) -> Optional[Variable]:
        """Update a variable’s value by its equipment ID and key."""
        try:
            with self.db_connection.get_session() as session:
                variable = (
                    session.query(Variable)
                    .filter(Variable.equipment_id == equipment_id, Variable.key == key)
                    .first()
                )
                if not variable:
                    return None

                variable.value = new_value
                session.flush()
                session.refresh(variable)
                return variable
        except SQLAlchemyError as e:
            logger.error(
                "Error updating value for variable with key %s and equipment ID %d: %s",
                key,
                equipment_id,
                e,
            )
            return None

    def delete(self, variable_id: int) -> bool:
        """Delete a variable by ID."""
        try:
            with self.db_connection.get_session() as session:
                variable = session.get(Variable, variable_id)
                if not variable:
                    return False

                session.delete(variable)
                session.flush()
                return True
        except SQLAlchemyError as e:
            logger.error("Error deleting variable ID %d: %s", variable_id, e)
            return False
