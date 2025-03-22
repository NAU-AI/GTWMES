from typing import Any, List, Optional, Dict
from sqlalchemy.orm import Session
from model.dto.equipment_dto import EquipmentDTO
from model.dto.variable import VariableDTO
from utility.logger import Logger
from service.equipment_service import EquipmentService
from service.variable_service import VariableService
from service.message_service import MessageService
from service.plc_service import PlcService

logger = Logger.get_logger(__name__)


class ConfigurationHandlerService:
    def __init__(
        self,
        session: Session,
        equipment_service: Optional[EquipmentService] = None,
        variable_service: Optional[VariableService] = None,
        message_service: Optional[MessageService] = None,
        plc_service: Optional[PlcService] = None,
    ):
        self.session = session
        self.equipment_service = equipment_service or EquipmentService(session)
        self.variable_service = variable_service or VariableService(session)
        self.message_service = message_service or MessageService(session)
        self.plc_service = plc_service or PlcService(session)

    def process_equipment_configuration(self, client, topic_send, message: Dict):
        try:
            config = self._validate_and_extract_message(message)
            equipment = self._create_or_update_equipment(config)
            created_variables = self._process_variables(
                equipment, message.get("variables", [])
            )
            self._update_equipment_schedule(equipment, client, topic_send)
            self.plc_service.schedule_plc_readings()

            logger.info(
                "Configuration successfully processed for '%s' (%d variables). Scheduler updated.",
                config["equipment_code"],
                len(created_variables),
            )
        except Exception as e:
            logger.error(
                "Error processing equipment configuration: %s", e, exc_info=True
            )

    @staticmethod
    def _validate_and_extract_message(message: Dict) -> Dict[str, Any]:
        equipment_code = message.get("equipmentCode")
        ip = message.get("ip")
        p_timer_communication_cycle = message.get("pTimerCommunicationCycle")

        if not equipment_code or not ip:
            raise ValueError("Missing required fields: 'equipmentCode' or 'ip'.")

        logger.info(
            "Processing configuration for equipment '%s' with IP '%s'",
            equipment_code,
            ip,
        )

        return {
            "equipment_code": equipment_code,
            "ip": ip,
            "p_timer_communication_cycle": p_timer_communication_cycle,
        }

    def _create_or_update_equipment(self, config: Dict[str, Any]):
        return self.equipment_service.create_or_update_equipment(
            config["equipment_code"],
            config["ip"],
            config["p_timer_communication_cycle"],
        )

    def _process_variables(self, equipment, variables: List[Dict]) -> Dict[str, Any]:
        created_variables = {}
        incoming_keys = {var["key"] for var in variables}

        existing_variables_dto = (
            self.variable_service.get_by_equipment_id_and_operation_type(
                equipment.id, "WRITE"
            )
        )
        existing_variables_map = {var.key: var for var in existing_variables_dto}
        existing_keys = set(existing_variables_map.keys())

        for var in variables:
            key = var["key"]
            variable = self.variable_service.create_or_update_variable(
                equipment.id, var
            )
            created_variables[key] = variable

            if variable.operation_type == "WRITE":
                self._write_variable_into_plc(equipment, variable)

        keys_to_delete = existing_keys - incoming_keys
        for key in keys_to_delete:
            var_to_delete = existing_variables_map[key]
            self.variable_service.delete_variable(var_to_delete.id)
            logger.info(
                f"Deleted variable '{key}' for equipment ID {equipment.id} as it was not in the incoming list."
            )

        return created_variables

    def _write_variable_into_plc(
        self, equipment: EquipmentDTO, variable: VariableDTO
    ) -> None:
        try:
            if variable.value is None:
                raise ValueError(f"Variable {variable.key} has no value set.")
            if variable.db_address is None or variable.offset_byte is None:
                raise ValueError(
                    f"Variable {variable.key} lacks DB address or byte offset."
                )

            if variable.type.upper() == "BOOL":
                self.plc_service.write_bool(
                    equipment.ip,
                    variable.db_address,
                    variable.offset_byte,
                    variable.offset_bit,
                    bool(variable.value),
                )
            elif variable.type.upper() == "INT":
                self.plc_service.write_int(
                    equipment.ip,
                    variable.db_address,
                    variable.offset_byte,
                    int(variable.value)
                    if isinstance(variable.value, (int, float, str))
                    else 0,
                )
            else:
                raise TypeError(f"Unsupported variable type: {variable.type}")

            logger.info(
                "Successfully wrote '%s' (type %s) to PLC %s, DB %s, Byte %s",
                variable.value,
                variable.type,
                equipment.ip,
                variable.db_address,
                variable.offset_byte,
            )

        except Exception as e:
            logger.error(
                "Error writing variable '%s' to PLC %s: %s",
                variable.key,
                equipment.ip,
                e,
            )

    def _update_equipment_schedule(self, equipment, client, topic_send):
        self.message_service.update_equipment_schedule(equipment, client, topic_send)
