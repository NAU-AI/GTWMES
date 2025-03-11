from database.connection.db_connection import SessionLocal
from model.variable import Variable


class VariableDAO:
    def save(self, variable: Variable) -> Variable:
        with SessionLocal() as session:
            session.add(variable)
            session.commit()
            session.refresh(variable)
            return variable

    def update(self, variable_id: int, updated_data: dict) -> Variable | None:
        with SessionLocal() as session:
            variable = (
                session.query(Variable).filter(Variable.id == variable_id).first()
            )
            if not variable:
                return None

            for key, value in updated_data.items():
                setattr(variable, key, value)

            session.commit()
            session.refresh(variable)
            return variable

    def find_by_id(self, variable_id: int) -> Variable | None:
        with SessionLocal() as session:
            return session.query(Variable).filter(Variable.id == variable_id).first()

    def find_by_equipment_id(self, equipment_id: int) -> list[Variable]:
        with SessionLocal() as session:
            return (
                session.query(Variable)
                .filter(Variable.equipment_id == equipment_id)
                .all()
            )

    def find_by_equipment_output_id(self, equipment_output_id: int) -> list[Variable]:
        with SessionLocal() as session:
            return (
                session.query(Variable)
                .join(Variable.outputs)
                .filter(Variable.outputs.any(id=equipment_output_id))
                .all()
            )

    def find_by_equipment_id_and_operation_type(
        self, equipment_id: int, operation_type: str
    ) -> list[Variable]:
        with SessionLocal() as session:
            return (
                session.query(Variable)
                .filter(
                    Variable.equipment_id == equipment_id,
                    Variable.operation_type == operation_type,
                )
                .all()
            )

    def find_all(self) -> list[Variable]:
        with SessionLocal() as session:
            return session.query(Variable).all()

    def find_by_equipment_id_and_key(
        self, equipment_id: int, key: str
    ) -> Variable | None:
        with SessionLocal() as session:
            return (
                session.query(Variable)
                .filter(Variable.equipment_id == equipment_id, Variable.key == key)
                .first()
            )

    def delete(self, variable_id: int) -> bool:
        with SessionLocal() as session:
            variable = (
                session.query(Variable).filter(Variable.id == variable_id).first()
            )
            if not variable:
                return False

            session.delete(variable)
            session.commit()
            return True
