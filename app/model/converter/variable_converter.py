from model.dto.variable import VariableDTO
from model.variable import Variable


class VariableConverter:
    @staticmethod
    def to_dto(variable: Variable) -> VariableDTO:
        return VariableDTO(
            id=variable.id,
            equipment_id=variable.equipment_id,
            key=variable.key,
            offset_byte=variable.offset_byte,
            offset_bit=variable.offset_bit,
            db_address=variable.db_address,
            type=variable.type,
            operation_type=variable.operation_type,
            category=variable.category,
            value=variable.value,
        )

    @staticmethod
    def to_dto_list(variables: list[Variable]) -> list[VariableDTO]:
        return [VariableConverter.to_dto(var) for var in variables]
