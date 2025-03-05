from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database.connection.db_connection import Base


class CounterRecord(Base):
    __tablename__ = "counter_record"

    id = Column(Integer, primary_key=True)
    real_value = Column(Integer, nullable=False)
    equipment_output_id = Column(
        Integer, ForeignKey("equipment_output.id"), nullable=False, index=True
    )
    registered_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    equipment_output = relationship("EquipmentOutput", back_populates="counter_records")

    def __repr__(self):
        return f"<CounterRecord(id={self.id}, real_value={self.real_value}, registered_at={self.registered_at})>"
