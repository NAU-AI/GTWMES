import logging
from typing import Optional
from sqlalchemy.orm import Session
from service.equipment_service import EquipmentService
from service.variable_service import VariableService
from service.message_service import MessageService

logger = logging.getLogger(__name__)


class ConfigurationHandlerService:
    def __init__(
        self,
        session: Session,
        equipment_service: Optional[EquipmentService] = None,
        variable_service: Optional[VariableService] = None,
        message_service: Optional[MessageService] = None,
    ):
        self.session = session
        self.equipment_service = equipment_service or EquipmentService(session)
        self.variable_service = variable_service or VariableService(session)
        self.message_service = message_service or MessageService(session)

    def process_equipment_configuration(self, client, message: dict):
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

            variables = message.get("variable", [])
            outputs = message.get("output", [])
            alarms = message.get("alarm", [])

            created_variables = self.create_or_update_variables(equipment.id, variables)
            created_outputs = self.create_or_update_variables(
                equipment.id, outputs, category="OUTPUT"
            )
            created_alarms = self.create_or_update_variables(
                equipment.id, alarms, category="ALARM"
            )

            logger.info(
                f"Configuration successfully processed for '{equipment_code}' "
                f"({len(created_variables)} variables, {len(created_outputs)} outputs, {len(created_alarms)} alarms)"
            )

        except Exception as e:
            logger.error(
                f"Error processing equipment configuration: {e}", exc_info=True
            )

    def create_or_update_variables(
        self, equipment_id: int, variables: list[dict], category: Optional[str] = None
    ) -> dict:
        created_variables = {}

        for variable_data in variables:
            try:
                if category:
                    variable_data["category"] = category

                variable = self.variable_service.create_or_update_variable(
                    equipment_id, variable_data
                )
                created_variables[variable_data["key"]] = variable
            except Exception as e:
                logger.error(
                    f"Error processing variable '{variable_data.get('key')}' for equipment ID {equipment_id}: {e}",
                    exc_info=True,
                )

        logger.info(
            f"Processed {len(created_variables)} {'variables' if not category else category.lower() + 's'} "
            f"for equipment ID {equipment_id}."
        )
        return created_variables
