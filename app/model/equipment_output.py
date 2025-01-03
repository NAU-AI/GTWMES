class EquipmentOutput:
    def __init__(self, id=None, code=None, alias=None, counting_equipment_id=None, disable=None): # i need to change on the database from "equipment_id" to "counting_equipment_id". This way corkdefect and GTW code will be equal
        self.id = id
        self.code = code
        #self.alias = alias # on the GTW we dont have "alias". See if we need to add it
        self.counting_equipment_id = counting_equipment_id
        self.disable = disable # see why disable is not on the corkdefect code

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            #"alias": self.alias,
            "counting_equipment_id": self.counting_equipment_id,
            "disable": self.disable,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            code=data.get("code"),
            #alias=data.get("alias"),
            counting_equipment_id=data.get("counting_equipment_id"),
            disable=data.get("disable")
        )
