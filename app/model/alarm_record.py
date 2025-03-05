from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database.connection.db_connection import Base


class AlarmRecord(Base):
    __tablename__ = "alarm_record"

    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)
    registered_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    variable_id = Column(Integer, ForeignKey("variable.id"), nullable=False, index=True)

    variable = relationship("Variable", back_populates="alarms")

    def __repr__(self):
        return f"<AlarmRecord(id={self.id}, value={self.value}, registered_at={self.registered_at})>"
