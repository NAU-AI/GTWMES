from typing import Any, List, Optional, Dict
from sqlalchemy.orm import Session
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

            logger.info(
                f"Configuration successfully processed for '{config['equipment_code']}' "
                f"({len(created_variables)} variables). Scheduler updated."
            )
        except Exception as e:
            logger.error(
                f"Error processing equipment configuration: {e}", exc_info=True
            )

    def _validate_and_extract_message(self, message: Dict) -> Dict[str, Any]:
        equipment_code = message.get("equipmentCode")
        ip = message.get("ip")
        p_timer_communication_cycle = message.get("pTimerCommunicationCycle")

        if not equipment_code or not ip:
            raise ValueError("Missing required fields: 'equipmentCode' or 'ip'.")

        logger.info(
            f"Processing configuration for equipment '{equipment_code}' with IP '{ip}'"
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

        for var in variables:
            variable = self.variable_service.create_or_update_variable(
                equipment.id, var
            )
            created_variables[var["key"]] = variable

            if variable.operation_type == "WRITE":
                self._log_variable_write(equipment, variable)

        return created_variables

    def _log_variable_write(self, equipment, variable):
        logger.info(
            f"Written value {variable.value} to PLC {equipment.ip}, "
            f"DB {variable.db_address}, Byte {variable.offset_byte}"
        )

    def _update_equipment_schedule(self, equipment, client, topic_send):
        self.message_service.update_equipment_schedule(equipment, client, topic_send)
