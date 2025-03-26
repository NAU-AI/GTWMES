import logging
from typing import List, Optional

from model.variable import Variable
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class VariableDAO:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, variable_id: int) -> Optional[Variable]:
        """Find a variable by its ID."""
        try:
            return (
                self.session.query(Variable).filter(Variable.id == variable_id).first()
            )
        except SQLAlchemyError as e:
            logger.error("Error finding variable ID %d: %s", variable_id, e)
            return None

    def find_by_equipment_id(self, equipment_id: int) -> List[Variable]:
        """Find all variables for a given equipment."""
        try:
            return (
                self.session.query(Variable)
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
            return (
                self.session.query(Variable)
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
            return (
                self.session.query(Variable)
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
            return (
                self.session.query(Variable)
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
            return self.session.query(Variable).all()
        except SQLAlchemyError as e:
            logger.error("Error finding all variables: %s", e)
            return []

    def save(self, variable: Variable) -> Optional[Variable]:
        """Save a new variable."""
        try:
            self.session.add(variable)
            self.session.flush()
            self.session.refresh(variable)
            self.session.commit()
            return variable
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error("Error saving variable: %s", e)
            return None

    def update(self, variable_id: int, updated_data: dict) -> Optional[Variable]:
        """Update a variable with new data."""
        try:
            variable = self.find_by_id(variable_id)
            if not variable:
                return None

            for key, value in updated_data.items():
                if hasattr(variable, key):
                    setattr(variable, key, value)

            self.session.flush()
            self.session.refresh(variable)
            self.session.commit()
            return variable
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error("Error updating variable ID %d: %s", variable_id, e)
            return None

    def update_value_by_key(
        self, equipment_id: int, key: str, new_value: dict
    ) -> Optional[Variable]:
        """Update a variable’s value by its equipment ID and key."""
        try:
            variable = self.find_by_equipment_id_and_key(equipment_id, key)
            if not variable:
                return None

            variable.value = new_value
            self.session.flush()
            self.session.refresh(variable)
            self.session.commit()
            return variable
        except SQLAlchemyError as e:
            self.session.rollback()
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
            variable = self.find_by_id(variable_id)
            if not variable:
                return False

            self.session.delete(variable)
            self.session.flush()
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error("Error deleting variable ID %d: %s", variable_id, e)
            return False
