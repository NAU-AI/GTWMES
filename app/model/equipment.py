from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.connection.db_connection import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, unique=True)
    ip = Column(String(20), nullable=False)
    p_timer_communication_cycle = Column(Integer, nullable=True)

    variables = relationship(
        "Variable", back_populates="equipment", cascade="all, delete-orphan"
    )
    outputs = relationship(
        "EquipmentOutput", back_populates="equipment", cascade="all, delete-orphan"
    )
    production_orders = relationship(
        "ProductionOrder", back_populates="equipment", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Equipment(id={self.id}, code='{self.code}', ip='{self.ip}')>"
