from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.connection.db_connection import Base


class ProductionOrder(Base):
    __tablename__ = "production_order"

    id = Column(Integer, primary_key=True)
    equipment_id = Column(
        Integer, ForeignKey("equipment.id"), nullable=False, index=True
    )
    code = Column(String(20), nullable=False, unique=True)
    is_completed = Column(Boolean, nullable=False)

    equipment = relationship("Equipment", back_populates="production_orders")

    def __repr__(self):
        return f"<ProductionOrder(id={self.id}, code='{self.code}', is_completed={self.is_completed})>"
