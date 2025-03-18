from service.plc_connection_manager import PlcConnectionManager
from utility.logger import Logger
from utility.scheduler import Scheduler
from service.equipment_service import EquipmentService
from service.variable_service import VariableService
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
                client = self.plc_connection_manager.get_plc_client(equipment.ip)
                if not client:
                    logger.error(
                        f"Unable to connect to PLC {equipment.ip}. Skipping..."
                    )
                    continue
            logger.info(f"Connected to PLC {equipment.ip} on startup.")

    def read_plc_data(self, equipment_id, equipment_ip):
        plc = self.plc_connection_manager.get_plc_client(equipment_ip)
        if not plc or not plc.is_connected():
            logger.error(f"PLC {equipment_ip} is not connected.")
            return None

        variables = self.variable_service.get_by_equipment_id_and_operation_type(
            equipment_id, "READ"
        )
        if not variables:
            logger.warning(f"No variables found for equipment {equipment_id}.")
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
                logger.info(f"Successfully read PLC data for {equipment_id}.")
            return results
        except Snap7Exception as e:
            logger.error(f"Error reading PLC data for {equipment_id}: {e}")
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
                        f"Updated variable '{variable.key}' with value {value}."
                    )
                else:
                    logger.warning(f"Variable '{key}' not found in database.")
            except Exception as e:
                logger.error(f"Error processing result for {key}: {e}", exc_info=True)

    def write_int(self, equipment_ip, db, byte, value):
        plc = self.plc_connection_manager.get_plc_client(equipment_ip)
        if plc:
            plc.write_int(db, byte, value)
            logger.info(
                f"Integer {value} written to PLC {equipment_ip}, DB {db}, Byte {byte}."
            )

    def write_bool(self, equipment_ip, db, byte, bit, value):
        plc = self.plc_connection_manager.get_plc_client(equipment_ip)
        if plc:
            plc.write_bool(db, byte, bit, value)
            logger.info(
                f"Boolean {value} written to PLC {equipment_ip}, DB {db}, Byte {byte}, Bit {bit}."
            )

    def write_alarm_status_by_key(self, equipment_code, key, status: bool):
        try:
            equipment = self.equipment_service.get_equipment_by_code(equipment_code)
            if not equipment:
                logger.error(f"Equipment with code {equipment_code} not found.")
                return

            alarm_variable = self.variable_service.get_by_equipment_id_and_key(
                equipment.id, key
            )
            if not alarm_variable:
                logger.error(
                    f"No variable '{key}' found for equipment {equipment_code}."
                )
                return

            equipment_ip = equipment.ip
            if not equipment_ip:
                logger.error(f"IP address not found for equipment {equipment_code}.")
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
                    f"Alarm written to PLC for {equipment_code} (IP {equipment_ip}): "
                    f"DB {alarm_variable.db_address}, Byte {alarm_variable.offset_byte}, "
                    f"Bit {alarm_variable.offset_bit}, Value {status}"
                )
        except Exception as e:
            logger.error(
                f"Failed to write alarm for {equipment_code}: {e}", exc_info=True
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
                f"Scheduled PLC data reading for {equipment.code} every 1 minute."
            )

    def _read_plc_data_task(self, client, topic_send, equipment):
        try:
            self.read_plc_data(equipment.id, equipment.ip)
        except Exception as e:
            logger.error(f"Error during PLC data reading for {equipment.id}: {e}")

    def shutdown(self):
        logger.info("Disconnecting all PLCs...")
        self.plc_connection_manager.disconnect_all()
