from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.connection.db_connection import Base


class Variable(Base):
    __tablename__ = "variable"

    id = Column(Integer, primary_key=True)
    equipment_id = Column(
        Integer, ForeignKey("equipment.id"), nullable=False, index=True
    )
    key = Column(String(20), nullable=False, unique=True)
    offset_byte = Column(Integer, nullable=False)
    offset_bit = Column(Integer, nullable=False)
    db_address = Column(String(20), nullable=False)
    type = Column(String(20), nullable=False)
    operation_type = Column(String(10), nullable=False)

    outputs = relationship("EquipmentOutput", back_populates="variable")
    active_time_records = relationship(
        "ActiveTimeRecord", back_populates="variable", cascade="all, delete-orphan"
    )
    alarms = relationship(
        "AlarmRecord", back_populates="variable", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Variable(id={self.id}, key='{self.key}', type='{self.type}')>"
