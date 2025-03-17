from typing import Optional, Dict
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
            equipment_code = message.get("equipmentCode")
            ip = message.get("ip")
            p_timer_communication_cycle = message.get("pTimerCommunicationCycle")

            if not equipment_code or not ip:
                raise ValueError("Missing required fields: 'equipmentCode' or 'ip'.")

            logger.info(
                f"Processing configuration for equipment '{equipment_code}' with IP '{ip}'"
            )

            equipment = self.equipment_service.create_or_update_equipment(
                equipment_code, ip, p_timer_communication_cycle
            )

            created_variables = {}
            for var in message.get("variables", []):
                variable = self.variable_service.create_or_update_variable(
                    equipment.id, var
                )
                created_variables[var["key"]] = variable

                if variable.operation_type == "WRITE":
                    db = variable.db_address
                    byte = variable.offset_byte
                    value = variable.value

                    self.plc_service.write_int(equipment.ip, db, byte, value)
                    logger.info(
                        f"Written value {value} to PLC {equipment.ip}, DB {db}, Byte {byte}"
                    )

            logger.info(
                f"Configuration successfully processed for '{equipment_code}' "
                f"({len(created_variables)} variables). Scheduler updated."
            )

            self.message_service.update_equipment_schedule(
                equipment,
                client,
                topic_send,
            )
        except Exception as e:
            logger.error(
                f"Error processing equipment configuration: {e}", exc_info=True
            )
