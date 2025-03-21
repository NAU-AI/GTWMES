from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class VariableDTO:
    id: int
    equipment_id: int
    key: str
    offset_byte: int
    offset_bit: int
    db_address: int
    type: str
    operation_type: str
    category: Optional[str]
    value: Optional[dict]
