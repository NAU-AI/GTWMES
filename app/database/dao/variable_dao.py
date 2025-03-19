from sqlalchemy.orm import Session
from typing import List, Optional
from model.variable import Variable


class VariableDAO:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, variable_id: int) -> Optional[Variable]:
        return self.session.query(Variable).filter(Variable.id == variable_id).first()

    def find_by_equipment_id(self, equipment_id: int) -> List[Variable]:
        return (
            self.session.query(Variable)
            .filter(Variable.equipment_id == equipment_id)
            .all()
        )

    def find_by_key(self, equipment_id: int, key: str) -> Optional[Variable]:
        return (
            self.session.query(Variable)
            .filter(Variable.equipment_id == equipment_id, Variable.key == key)
            .first()
        )

    def find_by_equipment_id_and_operation_type(
        self, equipment_id: int, operation_type: str
    ) -> List[Variable]:
        return (
            self.session.query(Variable)
            .filter(
                Variable.equipment_id == equipment_id,
                Variable.operation_type == operation_type,
            )
            .all()
        )

    def find_by_equipment_id_category_operation_type(
        self, equipment_id: int, category: str, operation_type: str
    ) -> List[Variable]:
        return (
            self.session.query(Variable)
            .filter(
                Variable.equipment_id == equipment_id,
                Variable.category == category,
                Variable.operation_type == operation_type,
            )
            .all()
        )

    def find_all(self) -> List[Variable]:
        return self.session.query(Variable).all()

    def find_by_equipment_id_and_key(
        self, equipment_id: int, key: str
    ) -> Optional[Variable]:
        return (
            self.session.query(Variable)
            .filter(Variable.equipment_id == equipment_id, Variable.key == key)
            .first()
        )

    def save(self, variable: Variable) -> Variable:
        self.session.add(variable)
        self.session.commit()
        self.session.refresh(variable)
        return variable

    def update(self, variable_id: int, updated_data: dict) -> Optional[Variable]:
        variable = self.find_by_id(variable_id)
        if not variable:
            return None

        for key, value in updated_data.items():
            if hasattr(variable, key):
                setattr(variable, key, value)

        self.session.commit()
        self.session.refresh(variable)
        return variable

    def update_value_by_key(
        self, equipment_id: int, key: str, new_value: dict
    ) -> Optional[Variable]:
        variable = self.find_by_equipment_id_and_key(equipment_id, key)
        if not variable:
            return None

        variable.value = new_value
        self.session.commit()
        self.session.refresh(variable)
        return variable

    def delete(self, variable_id: int) -> bool:
        variable = (
            self.session.query(Variable).filter(Variable.id == variable_id).first()
        )
        if not variable:
            return False
        self.session.delete(variable)
        self.session.commit()
        return True
