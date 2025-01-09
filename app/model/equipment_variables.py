class EquipmentVariables:
    def __init__(
        self,
        id=None,
        counting_equipment_id=None,
        name=None,
        offset_byte=None,
        offset_bit=None,
        db_address=None,
        type=None,
    ):
        self.id = id
        self.counting_equipment_id = counting_equipment_id
        self.name = name
        self.offset_byte = offset_byte
        self.offset_bit = offset_bit
        self.db_address = db_address
        self.type = type

    def to_dict(self):
        return {
            "id": self.id,
            "counting_equipment_id": self.counting_equipment_id,
            "name": self.name,
            "offset_byte": self.offset_byte,
            "offset_bit": self.offset_bit,
            "db_address": self.db_address,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            counting_equipment_id=data.get("counting_equipment_id"),
            name=data.get("name"),
            offset_byte=data.get("offset_byte"),
            offset_bit=data.get("offset_bit"),
            db_address=data.get("db_address"),
            type=data.get("type"),
        )
