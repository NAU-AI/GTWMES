from typing import Optional
from database.connection.db_connection import SessionLocal
from model.production_order import ProductionOrder


class ProductionOrderDAO:
    def find_by_id(self, order_id: int) -> ProductionOrder | None:
        with SessionLocal() as session:
            return (
                session.query(ProductionOrder)
                .filter(ProductionOrder.id == order_id)
                .first()
            )

    def find_by_equipment_id(
        self, equipment_id: int, is_completed: bool
    ) -> list[ProductionOrder]:
        with SessionLocal() as session:
            return (
                session.query(ProductionOrder)
                .filter(
                    ProductionOrder.equipment_id == equipment_id,
                    ProductionOrder.is_completed == is_completed,
                )
                .all()
            )

    def find_all(self) -> list[ProductionOrder]:
        with SessionLocal() as session:
            return session.query(ProductionOrder).all()

    def find_production_order_by_equipment_id(
        self, equipment_id: int, is_completed: bool
    ) -> Optional[ProductionOrder]:
        with SessionLocal() as session:
            return (
                session.query(ProductionOrder)
                .filter(
                    ProductionOrder.equipment_id == equipment_id,
                    ProductionOrder.is_completed == is_completed,
                )
                .order_by(ProductionOrder.id.asc())
                .first()
            )

    def get_by_code(self, code: str) -> Optional[ProductionOrder]:
        with SessionLocal() as session:
            return session.query(ProductionOrder).filter_by(code=code).first()

    def save(self, order: ProductionOrder) -> ProductionOrder:
        with SessionLocal() as session:
            session.add(order)
            session.commit()
            session.refresh(order)
            return order

    def delete(self, order_id: int) -> bool:
        with SessionLocal() as session:
            order = (
                session.query(ProductionOrder)
                .filter(ProductionOrder.id == order_id)
                .first()
            )
            if not order:
                return False

            session.delete(order)
            session.commit()
            return True

    def start_new_production_order(
        self, equipment_id: int, code: str
    ) -> ProductionOrder:
        with SessionLocal() as session:
            session.query(ProductionOrder).filter(
                ProductionOrder.equipment_id == equipment_id
            ).update({"is_completed": True})

            new_order = ProductionOrder(
                equipment_id=equipment_id, code=code, is_completed=False
            )
            session.add(new_order)
            session.commit()
            session.refresh(new_order)
            return new_order

    def complete_production_order(self, order_id: int) -> bool:
        with SessionLocal() as session:
            order = (
                session.query(ProductionOrder)
                .filter(ProductionOrder.id == order_id)
                .first()
            )
            if not order or order.is_completed:
                return False

            order.is_completed = True
            session.commit()
            return True
