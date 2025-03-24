from service.plc_connection_manager import PlcConnectionManager
from service.equipment_service import EquipmentService
from service.variable_service import VariableService
from utility.logger import Logger
from utility.scheduler import Scheduler
from sqlalchemy.orm import Session
from snap7.exceptions import Snap7Exception

logger = Logger.get_logger(__name__)


class PlcService:
    def __init__(
        self,
        session: Session,
        variable_service=None,
        equipment_service=None,
    ):
        self.variable_service = variable_service or VariableService(session)
        self.equipment_service = equipment_service or EquipmentService(session)
        self.scheduler = Scheduler()
        self.plc_connection_manager = PlcConnectionManager()

    def connect_all_plcs(self):
        equipments = self.equipment_service.get_all_equipment()
        for equipment in equipments:
            if equipment.ip:
                logger.info("Attempting to connect to PLC at %s...", equipment.ip)
                self.plc_connection_manager.get_plc_client(equipment.ip)
                logger.info("Connected to PLC %s on startup.", equipment.ip)

    def read_plc_data(self, equipment_id, equipment_ip):
        plc = self.plc_connection_manager.get_plc_client(equipment_ip)
        if not plc or not plc.is_connected():
            logger.error("PLC %s is not connected.", equipment_ip)
            return None

        variables = self.variable_service.get_by_equipment_id_and_operation_type(
            equipment_id, "READ"
        )
        if not variables:
            logger.warning("No variables found for equipment %s.", equipment_id)
            return None

        data_package = [
            {
                "key": var.key,
                "type": var.type,
                "db": var.db_address,
                "byte": var.offset_byte,
                "bit": var.offset_bit,
            }
            for var in variables
        ]

        try:
            results = plc.read_data_package(data_package)
            if results:
                self._process_results(equipment_id, results, variables)
                logger.info("Successfully read PLC data for %s.", equipment_id)
            return results
        except Snap7Exception as e:
            logger.error("Error reading PLC data for %s: %s", equipment_id, e)
            return None

    def _process_results(self, equipment_id, results, variables):
        for key, value in results.items():
            try:
                variable = next((var for var in variables if var.key == key), None)
                if variable:
                    self.variable_service.update_variable_value(
                        equipment_id, variable.key, value
                    )
                    logger.debug(
                        "Updated variable '%s' with value %s.", variable.key, value
                    )
                else:
                    logger.warning("Variable '%s' not found in database.", key)
            except Exception as e:
                logger.error(
                    "Error processing result for %s: %s", key, e, exc_info=True
                )

    def write_int(self, equipment_ip, db, byte, value):
        plc = self.plc_connection_manager.get_plc_client(equipment_ip)
        if plc:
            plc.write_int(db, byte, value)
            logger.info(
                "Integer %s written to PLC %s, DB %s, Byte %s.",
                value,
                equipment_ip,
                db,
                byte,
            )

    def write_bool(self, equipment_ip, db, byte, bit, value):
        plc = self.plc_connection_manager.get_plc_client(equipment_ip)
        if plc:
            plc.write_bool(db, byte, bit, value)
            logger.info(
                "Boolean %s written to PLC %s, DB %s, Byte %s, Bit %s.",
                value,
                equipment_ip,
                db,
                byte,
                bit,
            )

    def write_alarm_status_by_key(self, equipment_code, key, status: bool):
        try:
            equipment = self.equipment_service.get_equipment_by_code(equipment_code)
            if not equipment:
                logger.error("Equipment with code %s not found.", equipment_code)
                return

            alarm_variable = self.variable_service.get_by_equipment_id_and_key(
                equipment.id, key
            )
            if not alarm_variable:
                logger.error(
                    "No variable '%s' found for equipment %s.", key, equipment_code
                )
                return

            equipment_ip = equipment.ip
            if not equipment_ip:
                logger.error("IP address not found for equipment %s.", equipment_code)
                return

            plc_client = self.plc_connection_manager.get_plc_client(equipment_ip)
            if plc_client:
                plc_client.write_bool(
                    alarm_variable.db_address,
                    alarm_variable.offset_byte,
                    alarm_variable.offset_bit,
                    value=status,
                )
                logger.info(
                    "Alarm written to PLC for %s (IP %s): DB %s, Byte %s, Bit %s, Value %s",
                    equipment_code,
                    equipment_ip,
                    alarm_variable.db_address,
                    alarm_variable.offset_byte,
                    alarm_variable.offset_bit,
                    status,
                )
        except Exception as e:
            logger.error(
                "Failed to write alarm for %s: %s", equipment_code, e, exc_info=True
            )

    def write_equipment_variables(self, equipment_ip, variables):
        plc_client = self.plc_connection_manager.get_plc_client(equipment_ip)

        if not plc_client:
            logger.error("PLC client unavailable for equipment at '%s'", equipment_ip)
            return

        for variable in variables:
            try:
                if variable.type.upper() == "INT":
                    plc_client.write_int(
                        variable.db_address, variable.offset_byte, variable.value
                    )
                elif variable.type.upper() == "BOOL":
                    plc_client.write_bool(
                        variable.db_address,
                        variable.offset_byte,
                        variable.offset_bit,
                        variable.value,
                    )

                logger.info(
                    "Written '%s' with value '%s' to PLC for equipment at '%s'",
                    variable.key,
                    variable.value,
                    equipment_ip,
                )

            except Exception as e:
                logger.error(
                    "Failed to write '%s' to PLC for equipment at '%s': %s",
                    variable.key,
                    equipment_ip,
                    e,
                    exc_info=True,
                )

    def schedule_plc_readings(self):
        equipments = self.equipment_service.get_all_equipment()
        for equipment in equipments:
            task_id = f"plc_read_{equipment.id}"
            self.scheduler.schedule_task(
                task_id=task_id,
                equipment=equipment,
                action=self._read_plc_data_task,
                client=None,
                topic_send=None,
                interval=60,
            )
            logger.info(
                "Scheduled PLC data reading for %s every 1 minute.", equipment.code
            )

    def _read_plc_data_task(self, client, topic_send, equipment):
        try:
            self.read_plc_data(equipment.id, equipment.ip)
        except Exception as e:
            logger.error("Error during PLC data reading for %s: %s", equipment.id, e)

    def shutdown(self):
        logger.info("Disconnecting all PLCs...")
        self.plc_connection_manager.disconnect_all()
