class Alarm:
    def __init__(
        self,
        id=None,
        equipment_id=None,
        alarm_0=None,
        alarm_1=None,
        alarm_2=None,
        alarm_3=None,
        registered_at=None,
    ):
        self.id = id
        self.equipment_id = equipment_id
        self.alarm_0 = alarm_0
        self.alarm_1 = alarm_1
        self.alarm_2 = alarm_2
        self.alarm_3 = alarm_3
        self.registered_at = registered_at

    def to_dict(self):
        return {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "alarm_0": self.alarm_0,
            "alarm_1": self.alarm_1,
            "alarm_2": self.alarm_2,
            "alarm_3": self.alarm_3,
            "registered_at": self.registered_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            equipment_id=data.get("equipment_id"),
            alarm_0=data.get("alarm_0"),
            alarm_1=data.get("alarm_1"),
            alarm_2=data.get("alarm_2"),
            alarm_3=data.get("alarm_3"),
            registered_at=data.get("registered_at"),
        )
