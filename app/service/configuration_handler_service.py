import logging
from service.equipment_service import EquipmentService
from service.variable_service import VariableService
from service.equipment_output_service import EquipmentOutputService
from service.alarm_record_service import AlarmRecordService
from service.message_service import MessageService

logger = logging.getLogger(__name__)


class ConfigurationHandlerService:
    def __init__(
        self,
        equipment_service: EquipmentService = None,
        variable_service: VariableService = None,
        output_service: EquipmentOutputService = None,
        alarm_service: AlarmRecordService = None,
        message_service: MessageService = None,
    ):
        self.equipment_service = equipment_service or EquipmentService()
        self.variable_service = variable_service or VariableService()
        self.output_service = output_service or EquipmentOutputService()
        self.alarm_service = alarm_service or AlarmRecordService()
        self.message_service = message_service or MessageService()

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

            self.create_or_update_outputs(equipment.id, outputs, created_variables)

            self.create_or_update_alarms(equipment.id, alarms, created_variables)

            logger.info(f"Configuration successfully processed for '{equipment_code}'.")

        except Exception as e:
            logger.error(
                f"Error processing equipment configuration: {e}", exc_info=True
            )

    def create_or_update_variables(
        self, equipment_id: int, variables: list[dict]
    ) -> dict:
        created_variables = {}
        for var in variables:
            try:
                variable = self.variable_service.create_or_update_variable(
                    equipment_id, var
                )
                created_variables[var["key"]] = variable
            except Exception as e:
                logger.error(
                    f"Error processing variable '{var.get('key')}' for equipment ID {equipment_id}: {e}",
                    exc_info=True,
                )
        logger.info(
            f"Processed {len(created_variables)} variables for equipment ID {equipment_id}."
        )
        return created_variables

    def create_or_update_outputs(
        self, equipment_id: int, outputs: list[dict], created_variables: dict
    ):
        for output_data in outputs:
            try:
                existing_output = self.output_service.find_by_equipment_id_and_code(
                    equipment_id, output_data["code"]
                )

                variable = self.variable_service.create_or_update_variable(
                    equipment_id, output_data, variable_key=output_data["code"]
                )
                created_variables[output_data["code"]] = variable

                if existing_output:
                    existing_output.variable_id = variable.id
                    self.output_service.save(existing_output)
                else:
                    output = self.output_service.create_output(
                        equipment_id, output_data
                    )
                    output.variable_id = variable.id
                    self.output_service.save(output)

            except Exception as e:
                logger.error(
                    f"Error processing output '{output_data.get('code')}' for equipment ID {equipment_id}: {e}",
                    exc_info=True,
                )

        logger.info(
            f"Processed {len(outputs)} outputs for equipment ID {equipment_id}."
        )

    def create_or_update_alarms(
        self, equipment_id: int, alarms: list[dict], created_variables: dict
    ):
        for alarm_data in alarms:
            try:
                # Create or update the variable for the alarm
                variable = self.variable_service.create_or_update_variable(
                    equipment_id, alarm_data, variable_key=alarm_data["key"]
                )
                created_variables[alarm_data["key"]] = variable

                self.alarm_service.create_or_update_alarm(variable.id, alarm_data)

            except Exception as e:
                logger.error(
                    f"Error processing alarm '{alarm_data.get('key')}' for equipment ID {equipment_id}: {e}",
                    exc_info=True,
                )

        logger.info(f"Processed {len(alarms)} alarms for equipment ID {equipment_id}.")
