from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model.equipment import Equipment
from typing import Optional, List


class EquipmentDAO:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, equipment_id: int) -> Optional[Equipment]:
        return self.session.get(Equipment, equipment_id)

    def find_by_code(self, code: str) -> Optional[Equipment]:
        return self.session.query(Equipment).filter_by(code=code).one_or_none()

    def find_all(self) -> List[Equipment]:
        equipment_list = self.session.query(Equipment).all()
        for equipment in equipment_list:
            self.session.refresh(equipment)
        return equipment_list

    def save(self, equipment: Equipment) -> Equipment:
        try:
            self.session.add(equipment)
            self.session.commit()
            self.session.refresh(equipment)
            return equipment
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Database error: {e}")

    def update(self, equipment_id: int, updated_data: dict) -> Optional[Equipment]:
        try:
            equipment = self.find_by_id(equipment_id)
            if not equipment:
                return None

            for key, value in updated_data.items():
                if hasattr(equipment, key):
                    setattr(equipment, key, value)

            self.session.commit()
            self.session.refresh(equipment)
            return equipment
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Database error: {e}")

    def update_production_order_code(
        self, equipment_id: int, production_order_code: str
    ) -> bool:
        try:
            equipment = self.find_by_id(equipment_id)
            if not equipment:
                return False

            equipment.production_order_code = production_order_code
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Database error updating production order code: {e}")

    def delete(self, equipment_id: int) -> bool:
        try:
            equipment = self.find_by_id(equipment_id)
            if not equipment:
                return False

            self.session.delete(equipment)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Database error: {e}")
