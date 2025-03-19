import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from model.variable import Variable

logger = logging.getLogger(__name__)


class VariableDAO:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, variable_id: int) -> Optional[Variable]:
        try:
            return (
                self.session.query(Variable).filter(Variable.id == variable_id).first()
            )
        except SQLAlchemyError as e:
            logger.error(
                "Database error while finding variable by ID %d: %s", variable_id, e
            )
            return None

    def find_by_equipment_id(self, equipment_id: int) -> List[Variable]:
        try:
            return (
                self.session.query(Variable)
                .filter(Variable.equipment_id == equipment_id)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(
                "Database error while finding variables by equipment ID %d: %s",
                equipment_id,
                e,
            )
            return []

    def find_by_key(self, equipment_id: int, key: str) -> Optional[Variable]:
        try:
            return (
                self.session.query(Variable)
                .filter(Variable.equipment_id == equipment_id, Variable.key == key)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(
                "Database error while finding variable by key %s for equipment ID %d: %s",
                key,
                equipment_id,
                e,
            )
            return None

    def find_by_equipment_id_and_operation_type(
        self, equipment_id: int, operation_type: str
    ) -> List[Variable]:
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
                "Database error while finding variables for equipment ID %d with operation type %s: %s",
                equipment_id,
                operation_type,
                e,
            )
            return []

    def find_by_equipment_id_category_operation_type(
        self, equipment_id: int, category: str, operation_type: str
    ) -> List[Variable]:
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
                "Database error while finding variables for equipment ID %d, category %s, operation type %s: %s",
                equipment_id,
                category,
                operation_type,
                e,
            )
            return []

    def find_all(self) -> List[Variable]:
        try:
            return self.session.query(Variable).all()
        except SQLAlchemyError as e:
            logger.error("Database error while finding all variables: %s", e)
            return []

    def find_by_equipment_id_and_key(
        self, equipment_id: int, key: str
    ) -> Optional[Variable]:
        try:
            return (
                self.session.query(Variable)
                .filter(Variable.equipment_id == equipment_id, Variable.key == key)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(
                "Database error while finding variable by key %s for equipment ID %d: %s",
                key,
                equipment_id,
                e,
            )
            return None

    def save(self, variable: Variable) -> Optional[Variable]:
        try:
            self.session.add(variable)
            self.session.commit()
            self.session.refresh(variable)
            return variable
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error("Database error while saving variable: %s", e)
            return None

    def update(self, variable_id: int, updated_data: dict) -> Optional[Variable]:
        try:
            variable = self.find_by_id(variable_id)
            if not variable:
                return None

            for key, value in updated_data.items():
                if hasattr(variable, key):
                    setattr(variable, key, value)

            self.session.commit()
            self.session.refresh(variable)
            return variable
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "Database error while updating variable ID %d: %s", variable_id, e
            )
            return None

    def update_value_by_key(
        self, equipment_id: int, key: str, new_value: dict
    ) -> Optional[Variable]:
        try:
            variable = self.find_by_equipment_id_and_key(equipment_id, key)
            if not variable:
                return None

            variable.value = new_value
            self.session.commit()
            self.session.refresh(variable)
            return variable
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "Database error while updating value for variable with key %s and equipment ID %d: %s",
                key,
                equipment_id,
                e,
            )
            return None

    def delete(self, variable_id: int) -> bool:
        try:
            variable = self.find_by_id(variable_id)
            if not variable:
                return False

            self.session.delete(variable)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "Database error while deleting variable ID %d: %s", variable_id, e
            )
            return False
