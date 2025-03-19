from typing import Optional
from sqlalchemy import JSON, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.connection.db_connection import Base


class Variable(Base):
    __tablename__ = "variable"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    equipment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("equipment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    offset_byte: Mapped[int] = mapped_column(Integer, nullable=False)
    offset_bit: Mapped[int] = mapped_column(Integer, nullable=False)
    db_address: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(10), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "operation_type IN ('READ', 'WRITE')", name="chk_operation_type"
        ),
        CheckConstraint(
            "category IN ('ALARM', 'OUTPUT', 'EQUIPMENT') OR category IS NULL",
            name="chk_category",
        ),
    )

    equipment = relationship("Equipment", back_populates="variables")

    def __repr__(self):
        return "<Variable(id=%s, key='%s', type='%s', category='%s')>" % (
            self.id,
            self.key,
            self.type,
            self.category,
        )
