from typing import Optional
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.connection.db_connection import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    ip: Mapped[str] = mapped_column(String(20), nullable=False)
    p_timer_communication_cycle: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    production_order_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, default=None
    )

    variables = relationship(
        "Variable", back_populates="equipment", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Equipment(id={self.id}, code='{self.code}', ip='{self.ip}')>"
