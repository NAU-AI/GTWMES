from database.connection.db_connection import SessionLocal
from model.variable import Variable


class VariableDAO:
    def __init__(self):
        self.session = SessionLocal()

    def save(self, variable: Variable) -> Variable:
        self.session.add(variable)
        self.session.commit()
        self.session.refresh(variable)
        return variable

    def update(self, variable_id: int, updated_data: dict) -> Variable:
        variable = (
            self.session.query(Variable).filter(Variable.id == variable_id).first()
        )
        if not variable:
            return None

        for key, value in updated_data.items():
            setattr(variable, key, value)

        self.session.commit()
        self.session.refresh(variable)
        return variable

    def find_by_id(self, variable_id: int) -> Variable:
        return self.session.query(Variable).filter(Variable.id == variable_id).first()

    def find_by_equipment_id(self, equipment_id: int) -> list[Variable]:
        return (
            self.session.query(Variable)
            .filter(Variable.equipment_id == equipment_id)
            .all()
        )

    def find_by_equipment_output_id(self, equipment_output_id: int) -> list[Variable]:
        return (
            self.session.query(Variable)
            .join(Variable.outputs)
            .filter(Variable.outputs.any(id=equipment_output_id))
            .all()
        )

    def find_all(self) -> list[Variable]:
        return self.session.query(Variable).all()

    def find_by_equipment_id_and_key(self, equipment_id: int, key: str) -> Variable:
        return (
            self.session.query(Variable)
            .filter(Variable.equipment_id == equipment_id, Variable.key == key)
            .first()
        )

    def delete(self, variable_id: int) -> bool:
        variable = (
            self.session.query(Variable).filter(Variable.id == variable_id).first()
        )
        if not variable:
            return False

        self.session.delete(variable)
        self.session.commit()
        return True

    def close(self):
        self.session.close()
