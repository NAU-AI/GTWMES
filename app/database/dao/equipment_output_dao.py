from database.connection.db_connection import SessionLocal
from model.equipment_output import EquipmentOutput


class EquipmentOutputDAO:
    def __init__(self):
        self.session = SessionLocal()

    def save(self, output: EquipmentOutput) -> EquipmentOutput:
        self.session.add(output)
        self.session.commit()
        self.session.refresh(output)
        return output

    def update(self, output_id: int, updated_data: dict) -> EquipmentOutput:
        output = (
            self.session.query(EquipmentOutput)
            .filter(EquipmentOutput.id == output_id)
            .first()
        )
        if not output:
            return None

        for key, value in updated_data.items():
            setattr(output, key, value)

        self.session.commit()
        self.session.refresh(output)
        return output

    def find_by_id(self, output_id: int) -> EquipmentOutput:
        return (
            self.session.query(EquipmentOutput)
            .filter(EquipmentOutput.id == output_id)
            .first()
        )

    def find_by_equipment_id(self, equipment_id: int) -> list[EquipmentOutput]:
        return (
            self.session.query(EquipmentOutput)
            .filter(EquipmentOutput.equipment_id == equipment_id)
            .all()
        )

    def find_all(self) -> list[EquipmentOutput]:
        return self.session.query(EquipmentOutput).all()

    def find_by_equipment_id_and_code(
        self, equipment_id: int, code: str
    ) -> EquipmentOutput:
        return (
            self.session.query(EquipmentOutput)
            .filter(
                EquipmentOutput.equipment_id == equipment_id,
                EquipmentOutput.code == code,
            )
            .first()
        )

    def delete(self, output_id: int) -> bool:
        output = (
            self.session.query(EquipmentOutput)
            .filter(EquipmentOutput.id == output_id)
            .first()
        )
        if not output:
            return False

        self.session.delete(output)
        self.session.commit()
        return True

    def close(self):
        self.session.close()
