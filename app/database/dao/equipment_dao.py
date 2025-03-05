from model.equipment import Equipment
from database.connection.db_connection import SessionLocal


class EquipmentDAO:
    def __init__(self):
        self.session = SessionLocal()

    def find_by_id(self, equipment_id: int) -> Equipment:
        return (
            self.session.query(Equipment).filter(Equipment.id == equipment_id).first()
        )

    def find_by_code(self, code: str) -> Equipment:
        return self.session.query(Equipment).filter(Equipment.code == code).first()

    def find_all(self) -> list[Equipment]:
        return self.session.query(Equipment).all()

    def save(self, equipment: Equipment) -> Equipment:
        self.session.add(equipment)
        self.session.commit()
        self.session.refresh(equipment)
        return equipment

    def update(self, equipment_id: int, updated_data: dict) -> Equipment:
        equipment = (
            self.session.query(Equipment).filter(Equipment.id == equipment_id).first()
        )
        if not equipment:
            return None

        for key, value in updated_data.items():
            setattr(equipment, key, value)

        self.session.commit()
        self.session.refresh(equipment)
        return equipment

    def delete(self, equipment_id: int) -> bool:
        equipment = (
            self.session.query(Equipment).filter(Equipment.id == equipment_id).first()
        )
        if not equipment:
            return False

        self.session.delete(equipment)
        self.session.commit()
        return True

    def close(self):
        self.session.close()
