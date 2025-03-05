from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.connection.db_connection import Base


class EquipmentOutput(Base):
    __tablename__ = "equipment_output"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False)
    variable_id = Column(Integer, ForeignKey("variable.id"), nullable=True, index=True)
    equipment_id = Column(
        Integer, ForeignKey("equipment.id"), nullable=False, index=True
    )

    equipment = relationship("Equipment", back_populates="outputs")
    variable = relationship("Variable", back_populates="outputs", lazy="joined")
    counter_records = relationship(
        "CounterRecord", back_populates="equipment_output", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<EquipmentOutput(id={self.id}, code='{self.code}', variable_id={self.variable_id})>"
