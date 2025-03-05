from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database.connection.db_connection import Base


class ActiveTimeRecord(Base):
    __tablename__ = "active_time_record"

    id = Column(Integer, primary_key=True)
    variable_id = Column(Integer, ForeignKey("variable.id"), nullable=False, index=True)
    active_time = Column(Integer, nullable=False)
    registered_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    variable = relationship("Variable", back_populates="active_time_records")

    def __repr__(self):
        return f"<ActiveTimeRecord(id={self.id}, variable_id={self.variable_id}, active_time={self.active_time})>"
