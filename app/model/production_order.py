class ProductionOrder:
    def __init__(self, id=None, equipment_id=None, code=None, is_completed=None):
        self.id = id
        self.equipment_id = equipment_id
        self.code = code
        self.is_completed = is_completed

    def to_dict(self):
        return {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "code": self.code,
            "is_completed": self.is_completed,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            equipment_id=data.get("equipment_id"),
            code=data.get("code"),
            is_completed=bool(data.get("is_completed"))
            if data.get("is_completed") is not None
            else None,
        )
