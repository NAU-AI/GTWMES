from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EquipmentDTO:
    id: int
    code: str
    ip: str
    p_timer_communication_cycle: Optional[int]
    production_order_code: Optional[str]
