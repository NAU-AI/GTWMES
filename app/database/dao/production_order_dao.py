from database.connection.db_connection import SessionLocal
from model import ProductionOrder


class ProductionOrderDAO:
    def __init__(self):
        self.session = SessionLocal()

    def find_by_id(self, order_id: int) -> ProductionOrder:
        return (
            self.session.query(ProductionOrder)
            .filter(ProductionOrder.id == order_id)
            .first()
        )

    def find_by_equipment_id(
        self, equipment_id: int, is_completed: bool
    ) -> list[ProductionOrder]:
        return (
            self.session.query(ProductionOrder)
            .filter(
                ProductionOrder.equipment_id == equipment_id,
                ProductionOrder.is_completed == is_completed,
            )
            .all()
        )

    def find_all(self) -> list[ProductionOrder]:
        return self.session.query(ProductionOrder).all()

    def save(self, order: ProductionOrder) -> ProductionOrder:
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def delete(self, order_id: int) -> bool:
        order = (
            self.session.query(ProductionOrder)
            .filter(ProductionOrder.id == order_id)
            .first()
        )
        if not order:
            return False

        self.session.delete(order)
        self.session.commit()
        return True

    def complete_production_order(self, order_id: int) -> bool:
        order = (
            self.session.query(ProductionOrder)
            .filter(ProductionOrder.id == order_id)
            .first()
        )
        if not order or order.is_completed:
            return False

        order.is_completed = True
        self.session.commit()
        return True

    def start_new_production_order(
        self, equipment_id: int, code: str
    ) -> ProductionOrder:
        self.session.query(ProductionOrder).filter(
            ProductionOrder.equipment_id == equipment_id
        ).update({"is_completed": True})

        new_order = ProductionOrder(
            equipment_id=equipment_id, code=code, is_completed=False
        )
        self.session.add(new_order)
        self.session.commit()
        self.session.refresh(new_order)
        return new_order

    def close(self):
        self.session.close()
