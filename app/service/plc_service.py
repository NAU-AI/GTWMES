import logging
from service.equipment_service import EquipmentService
from service.PLC.plc_client import PLCClient
from service.variable_service import VariableService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class PlcService:
    def __init__(
        self,
        session: Session,
        variable_service=None,
        equipment_service=None,
        plc_client_factory=None,
    ):
        self.variable_service = variable_service or VariableService(session)
        self.equipment_service = equipment_service or EquipmentService(session)
        self.plc_client_factory = plc_client_factory or PLCClient
        self.plc_clients = {}

    def get_plc_client(self, ip):
        if ip not in self.plc_clients:
            self.plc_clients[ip] = self.plc_client_factory(ip)
            self.plc_clients[ip].connect()
        return self.plc_clients[ip]

    def disconnect_all(self):
        for client in self.plc_clients.values():
            client.disconnect()
        self.plc_clients.clear()

    def read_plc_data(self, equipment_id, equipment_ip):
        plc = self.get_plc_client(equipment_ip)
        if not plc.is_connected():
            logger.warning(f"PLC {equipment_ip} not connected.")
            return None

        variables = self.variable_service.get_by_equipment_id(equipment_id)
        if not variables:
            logger.warning(f"No variables found for equipment {equipment_id}.")
            return None

        data_package = [
            {
                "db": var.db_address,
                "byte": var.offset_byte,
                "bit": var.offset_bit,
                "type": var.type,
                "key": var.key,
            }
            for var in variables
        ]

        results = plc.read_data_package(data_package)

        if results:
            self._process_results(equipment_id, results, variables)

        logger.info("Successfully read PLC data.")
        return results

    def _process_results(self, equipment_id, results, variables):
        for key, value in results.items():
            try:
                variable = next(var for var in variables if var.key == key)

                self.variable_service.update_variable_value(
                    equipment_id, variable.key, value
                )

                logger.info(f"Updated variable '{variable.key}' with value {value}.")

            except Exception as e:
                logger.error(f"Error processing result for {key}: {e}", exc_info=True)

    def write_int(self, equipment_ip, db, byte, value):
        plc = self.get_plc_client(equipment_ip)
        plc.write_int(db, byte, value)
        logger.info(
            f"Integer {value} written to PLC {equipment_ip}, DB {db}, Byte {byte}"
        )

    def write_bool(self, equipment_ip, db, byte, bit, value):
        plc = self.get_plc_client(equipment_ip)
        plc.write_bool(db, byte, bit, value)
        logger.info(
            f"Boolean {value} written to PLC {equipment_ip}, DB {db}, Byte {byte}, Bit {bit}"
        )
