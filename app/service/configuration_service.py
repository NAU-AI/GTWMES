import json
from model import Equipment, Variable, EquipmentOutput, AlarmRecord
from service.equipment_service import EquipmentService
from service.variable_service import VariableService
from service.equipment_output_service import EquipmentOutputService
from service.alarm_record_service import AlarmRecordService
from app.exception import ServiceException
from app.utility.logger import Logger

logger = Logger.get_logger(__name__)


class ConfigurationService:
    def __init__(
        self,
        equipment_service: EquipmentService = None,
        variable_service: VariableService = None,
        equipment_output_service: EquipmentOutputService = None,
        alarm_record_service: AlarmRecordService = None,
    ):
        self.equipment_service = equipment_service or EquipmentService()
        self.variable_service = variable_service or VariableService()
        self.equipment_output_service = (
            equipment_output_service or EquipmentOutputService()
        )
        self.alarm_record_service = alarm_record_service or AlarmRecordService()

    def process_configuration_message(self, message: dict):
        try:
            equipment_code = message.get("equipmentCode")
            if not equipment_code:
                raise ValueError("Missing 'equipmentCode' in configuration message")

            logger.info(f"Processing configuration for equipment '{equipment_code}'")

            equipment = self._get_or_create_equipment(message)

            if "variable" in message:
                self._process_variables(equipment, message["variable"])

            if "output" in message:
                self._process_outputs(equipment, message["output"])

            if "alarm" in message:
                self._process_alarms(equipment, message["alarm"])

            logger.info(
                f"Successfully processed configuration for equipment '{equipment.code}'"
            )

        except Exception as e:
            logger.error(f"Error processing configuration message: {e}", exc_info=True)
            raise ServiceException("Failed to process configuration message") from e

    def _get_or_create_equipment(self, data: dict) -> Equipment:
        equipment = self.equipment_service.get_equipment_by_code(data["equipmentCode"])
        if equipment:
            logger.info(f"Updating existing equipment '{equipment.code}'")
            equipment.ip = data.get("ip", equipment.ip)
            equipment.p_timer_communication_cycle = data.get(
                "pTimerCommunicationCycle", equipment.p_timer_communication_cycle
            )
            equipment = self.equipment_service.update_equipment(equipment)
        else:
            logger.info(f"Creating new equipment '{data['equipmentCode']}'")
            equipment = Equipment(
                code=data["equipmentCode"],
                ip=data.get("plcIp"),
                p_timer_communication_cycle=data.get("pTimerCommunicationCycle"),
            )
            equipment = self.equipment_service.insert_equipment(equipment)
        return equipment

    def _process_variables(self, equipment: Equipment, variables: list):
        for var_data in variables:
            self._create_and_save_variable(equipment, var_data["key"], var_data)

    def _process_outputs(self, equipment: Equipment, outputs: list):
        for output_data in outputs:
            saved_variable = self._create_and_save_variable(
                equipment, output_data["code"], output_data
            )

            output = EquipmentOutput(
                equipment_id=equipment.id,
                code=output_data["code"],
                variable_id=saved_variable.id,
            )
            self.equipment_output_service.create_equipment_output(output)

            logger.info(
                f"Saved equipment output '{output.code}' with linked variable '{saved_variable.key}' "
                f"for equipment '{equipment.code}'"
            )

    def _create_and_save_variable(
        self, equipment: Equipment, key: str, data: dict
    ) -> Variable:
        variable = Variable(
            equipment_id=equipment.id,
            key=key,
            db_address=data["dbAddress"],
            offset_byte=data["offsetByte"],
            offset_bit=data["offsetBit"],
            type=data["type"],
            operation_type=data["operationType"],
        )
        saved_variable = self.variable_service.save_variable(variable)

        logger.info(
            f"Saved variable '{saved_variable.key}' for equipment '{equipment.code}'"
        )
        return saved_variable

    def _process_alarms(self, equipment: Equipment, alarms: list):
        for alarm_data in alarms:
            saved_variable = self._create_and_save_variable(
                equipment, alarm_data["key"], alarm_data
            )

            alarm = AlarmRecord(
                variable_id=saved_variable.id,
                value=0,
            )
            self.alarm_record_service.create_alarm_record(alarm)

            logger.info(
                f"Saved alarm '{saved_variable.key}' for equipment '{equipment.code}'"
            )
