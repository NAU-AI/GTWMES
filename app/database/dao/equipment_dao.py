from model.equipment import Equipment

from database.connection.db_connection import SessionLocal


class EquipmentDAO:
    def find_by_id(self, equipment_id: int) -> Equipment | None:
        with SessionLocal() as session:
            return session.query(Equipment).filter(Equipment.id == equipment_id).first()

    def find_by_code(self, code: str) -> Equipment | None:
        with SessionLocal() as session:
            return session.query(Equipment).filter(Equipment.code == code).first()

    def find_all(self) -> list[Equipment]:
        with SessionLocal() as session:
            return session.query(Equipment).all()

    def get_all_equipment_refreshed(self) -> list[Equipment]:
        with SessionLocal() as session:
            session.expire_all()
            return session.query(Equipment).all()

    def save(self, equipment: Equipment) -> Equipment:
        with SessionLocal() as session:
            session.add(equipment)
            session.commit()
            session.refresh(equipment)
            return equipment

    def update(self, equipment_id: int, updated_data: dict) -> Equipment | None:
        with SessionLocal() as session:
            equipment = (
                session.query(Equipment).filter(Equipment.id == equipment_id).first()
            )
            if not equipment:
                return None

            for key, value in updated_data.items():
                setattr(equipment, key, value)

            session.commit()
            session.refresh(equipment)
            return equipment

    def delete(self, equipment_id: int) -> bool:
        with SessionLocal() as session:
            equipment = (
                session.query(Equipment).filter(Equipment.id == equipment_id).first()
            )
            if not equipment:
                return False

            session.delete(equipment)
            session.commit()
            return True
