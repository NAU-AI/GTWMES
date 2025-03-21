from model.dto.equipment_dto import EquipmentDTO
from model.equipment import Equipment


class EquipmentConverter:
    @staticmethod
    def to_dto(equipment: Equipment) -> EquipmentDTO:
        return EquipmentDTO(
            id=equipment.id,
            code=equipment.code,
            ip=equipment.ip,
            p_timer_communication_cycle=equipment.p_timer_communication_cycle,
            production_order_code=equipment.production_order_code,
        )

    @staticmethod
    def to_dto_list(equipments: list[Equipment]) -> list[EquipmentDTO]:
        return [EquipmentConverter.to_dto(e) for e in equipments]
