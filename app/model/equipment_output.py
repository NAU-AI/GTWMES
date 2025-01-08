class EquipmentOutput:
    def __init__(self, id=None, code=None, counting_equipment_id=None):
        self.id = id
        self.code = code
        self.counting_equipment_id = counting_equipment_id

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "counting_equipment_id": self.counting_equipment_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            code=data.get("code"),
            counting_equipment_id=data.get("counting_equipment_id")
        )
