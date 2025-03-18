from model.dto.production_count_dto import ProductionCountDTO
from model.dto.variable_dto import VariableDTO
from sqlalchemy.orm import Session
from service.variable_service import VariableService
from exception.Exception import ServiceException, NotFoundException
from utility.logger import Logger
from model.equipment import Equipment
from service.equipment_service import EquipmentService  # Import the EquipmentService
from typing import List, Optional

logger = Logger.get_logger(__name__)


class ProductionCountService:
    def __init__(
        self,
        session: Session,
        variable_service: Optional[VariableService] = None,
        equipment_service: Optional[EquipmentService] = None,
    ):
        self.variable_service = variable_service or VariableService(session)
        self.equipment_service = equipment_service or EquipmentService(session)

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
            logger.error(f"Error building production count message: {e}", exc_info=True)
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
                "value": output_variable.value
                if output_variable.value is not None
                else 0,
            }
            for output_variable in variables
            if output_variable.category == "OUTPUT"
        ]

        return ProductionCountDTO(
            json_type=message_type,
            equipment_code=equipment_code,
            production_order_code=production_order_code
            if production_order_code is not None
            else "",
            equipment_status=equipment_status,
            active_time=active_time,
            alarms=alarm_values,
            counters=output_counters,
        )

    def _get_equipment_by_code(self, equipment_code: str) -> Equipment:
        equipment = self.equipment_service.get_equipment_by_code(equipment_code)
        if not equipment:
            raise NotFoundException(
                f"Equipment with code '{equipment_code}' not found."
            )
        return equipment

    def _get_all_variables(self, equipment_id: int) -> List[VariableDTO]:
        variables = self.variable_service.get_by_equipment_id_and_operation_type(
            equipment_id, "READ"
        )
        if not variables:
            raise NotFoundException(
                f"No variables found for equipment ID {equipment_id}."
            )
        return [
            VariableDTO(
                equipment_id=var.equipment_id,
                category=var.category,
                operation_type=var.operation_type,
                value=var.value,
                key=var.key,
            )
            for var in variables
        ]

    def _get_variable_value(
        self, variables: List[VariableDTO], key: str, default: Optional[int] = 0
    ) -> int:
        for variable in variables:
            if variable.key == key:
                return variable.value if variable.value is not None else default
        return default
