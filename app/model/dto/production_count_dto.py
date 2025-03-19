from typing import List


class ProductionCountDTO:
    def __init__(
        self,
        json_type: str,
        equipment_code: str,
        production_order_code: str,
        equipment_status: int,
        active_time: int,
        alarms: List[int],
        counters: List[dict],
    ):
        self.json_type = json_type
        self.equipment_code = equipment_code
        self.production_order_code = production_order_code
        self.equipment_status = equipment_status
        self.active_time = active_time
        self.alarms = alarms
        self.counters = counters

    def to_dict(self):
        return {
            "jsonType": self.json_type,
            "equipmentCode": self.equipment_code,
            "productionOrderCode": self.production_order_code,
            "equipmentStatus": self.equipment_status,
            "activeTime": self.active_time,
            "alarms": self.alarms,
            "counters": self.counters,
        }
