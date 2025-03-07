from database.connection.db_connection import SessionLocal
from model.equipment_output import EquipmentOutput


class EquipmentOutputDAO:
    def save(self, output: EquipmentOutput) -> EquipmentOutput:
        with SessionLocal() as session:
            session.add(output)
            session.commit()
            session.refresh(output)
            return output

    def update(self, output_id: int, updated_data: dict) -> EquipmentOutput | None:
        with SessionLocal() as session:
            output = (
                session.query(EquipmentOutput)
                .filter(EquipmentOutput.id == output_id)
                .first()
            )
            if not output:
                return None

            for key, value in updated_data.items():
                setattr(output, key, value)

            session.commit()
            session.refresh(output)
            return output

    def find_by_id(self, output_id: int) -> EquipmentOutput | None:
        with SessionLocal() as session:
            return (
                session.query(EquipmentOutput)
                .filter(EquipmentOutput.id == output_id)
                .first()
            )

    def find_by_equipment_id(self, equipment_id: int) -> list[EquipmentOutput]:
        with SessionLocal() as session:
            return (
                session.query(EquipmentOutput)
                .filter(EquipmentOutput.equipment_id == equipment_id)
                .all()
            )

    def find_all(self) -> list[EquipmentOutput]:
        with SessionLocal() as session:
            return session.query(EquipmentOutput).all()

    def find_by_equipment_id_and_code(
        self, equipment_id: int, code: str
    ) -> EquipmentOutput | None:
        with SessionLocal() as session:
            return (
                session.query(EquipmentOutput)
                .filter(
                    EquipmentOutput.equipment_id == equipment_id,
                    EquipmentOutput.code == code,
                )
                .first()
            )

    def delete(self, output_id: int) -> bool:
        with SessionLocal() as session:
            output = (
                session.query(EquipmentOutput)
                .filter(EquipmentOutput.id == output_id)
                .first()
            )
            if not output:
                return False

            session.delete(output)
            session.commit()
            return True
