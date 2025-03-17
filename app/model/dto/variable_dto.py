from typing import Optional


class VariableDTO:
    def __init__(
        self,
        equipment_id: int,
        category: str,
        operation_type: str,
        value: Optional[dict] = None,
        key: Optional[str] = None,
    ):
        self.equipment_id = equipment_id
        self.category = category
        self.operation_type = operation_type
        self.value = value
        self.key = key

    def to_dict(self) -> dict:
        return {
            "equipmentId": self.equipment_id,
            "category": self.category,
            "operationType": self.operation_type,
            "value": self.value,
            "key": self.key,
        }
