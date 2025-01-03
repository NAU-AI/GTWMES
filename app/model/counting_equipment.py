class CountingEquipment:
    def __init__(self, id=None, code=None, equipment_status=None, p_timer_communication_cycle=None, plc_ip=None):
        self.id = id
        self.code = code
        self.equipment_status = equipment_status
        self.p_timer_communication_cycle = p_timer_communication_cycle
        self.plc_ip = plc_ip

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "equipment_status": self.equipment_status,
            "p_timer_communication_cycle": self.p_timer_communication_cycle,
            "plc_ip": self.plc_ip,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            code=data.get("code"),
            equipment_status=data.get("equipment_status"),
            p_timer_communication_cycle=data.get("p_timer_communication_cycle"),
            plc_ip=data.get("plc_ip"),
        )
