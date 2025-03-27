from typing import List, Optional

from exception.Exception import NotFoundException, ServiceException
from model.dto.equipment_dto import EquipmentDTO
from model.dto.production_count_dto import ProductionCountDTO
from model.dto.variable import VariableDTO
from service.equipment_service import EquipmentService
from service.variable_service import VariableService
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class ProductionCountService:
    def __init__(
        self,
        variable_service: VariableService,
        equipment_service: EquipmentService,
    ):
        self.variable_service = variable_service
        self.equipment_service = equipment_service

    def build_production_count(self, equipment_code: str, message_type: str) -> dict:
        try:
            equipment = self._get_equipment_by_code(equipment_code)

            variables = self._get_all_variables(equipment.id)

            production_count_dto = self._build_production_count_dto(
                message_type=message_type,
                equipment_code=equipment.code,
                production_order_code=equipment.production_order_code,
                variables=variables,
            )

            return production_count_dto.to_dict()

        except Exception as e:
            logger.error(
                "Error building production count message: %s", e, exc_info=True
            )
            raise ServiceException("Failed to build production count message.") from e

    def _build_production_count_dto(
        self,
        message_type: str,
        equipment_code: str,
        production_order_code: Optional[str],
        variables: List[VariableDTO],
    ) -> ProductionCountDTO:
        equipment_status = self._get_variable_value(
            variables, "equipmentStatus", default=0
        )
        active_time = self._get_variable_value(variables, "activeTime", default=0)

        alarm_values = [
            alarm_variable.value if alarm_variable.value is not None else 0
            for alarm_variable in variables
            if alarm_variable.category == "ALARM"
        ]

        output_counters = [
            {
                "outputCode": output_variable.key,
                "value": (
                    output_variable.value if output_variable.value is not None else 0
                ),
            }
            for output_variable in variables
            if output_variable.category == "OUTPUT"
        ]

        return ProductionCountDTO(
            json_type=message_type,
            equipment_code=equipment_code,
            production_order_code=(
                production_order_code if production_order_code is not None else ""
            ),
            equipment_status=equipment_status,
            active_time=active_time,
            alarms=alarm_values,
            counters=output_counters,
        )

    def _get_equipment_by_code(self, equipment_code: str) -> EquipmentDTO:
        equipment_dto = self.equipment_service.get_equipment_by_code(equipment_code)
        if not equipment_dto:
            raise NotFoundException(
                f"Equipment with code '{equipment_code}' not found."
            )
        return equipment_dto

    def _get_all_variables(self, equipment_id: int) -> List[VariableDTO]:
        variable_dtos = self.variable_service.get_by_equipment_id_and_operation_type(
            equipment_id, "READ"
        )
        if not variable_dtos:
            raise NotFoundException(
                f"No variables found for equipment ID {equipment_id}."
            )
        return variable_dtos

    @staticmethod
    def _get_variable_value(
        variables: List[VariableDTO], key: str, default: int = 0
    ) -> int:
        for variable in variables:
            if variable.key == key:
                if isinstance(variable.value, (int, float, str)):
                    return (
                        int(variable.value) if variable.value is not None else default
                    )
                return default
        return default
