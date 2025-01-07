import datetime

class ActiveTime:
    def __init__(
        self,
        id=None,
        active_time=None,
        #increment_active_time=None,
        registered_at=None,
        equipment_id=None,
    ):
        self.id = id
        self.active_time = active_time
        #self.increment_active_time = increment_active_time
        self.registered_at = registered_at or datetime.datetime.now()
        self.equipment_id = equipment_id

    def to_dict(self):
        return {
            "id": self.id,
            "active_time": self.active_time,
            #"increment_active_time": self.increment_active_time,
            "registered_at": self.registered_at,
            "equipment_id": self.equipment_id,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            active_time=data.get("active_time"),
            #increment_active_time=data.get("increment_active_time"),
            registered_at=data.get("registered_at"),
            equipment_id=data.get("equipment_id"),
        )
