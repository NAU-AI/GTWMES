from datetime import datetime


class CounterRecord:
    def __init__(
        self,
        id=None,
        equipment_output_id=None,
        alias=None,
        real_value=None,
        increment=None,
        registered_at=None,
    ):
        self.id = id
        self.equipment_output_id = equipment_output_id
        self.alias = alias
        self.real_value = real_value
        #self.increment = increment
        self.registered_at = registered_at or datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "equipment_output_id": self.equipment_output_id,
            "alias": self.alias,
            "real_value": self.real_value,
            #"increment": self.increment,
            "registered_at": self.registered_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            equipment_output_id=data.get("equipment_output_id"),
            alias=data.get("alias"),
            real_value=data.get("real_value"),
            #increment=data.get("increment"),
            registered_at=data.get("registered_at"),
        )
