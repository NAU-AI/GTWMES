import logging
from service.PLC.snap7 import read_status_data, read_alarms, write_alarms_data
from service.PLC.snap7 import plc_connect, plc_disconnect

# we need to change this functions because now we have a table on DB with the addresses of the PLC parameters
class PlcService:
    def __init__(self, plc_client=None):
        self.plc_client = plc_client or self._default_plc_client

    def _default_plc_client(self):
        try:
            plc = plc_connect()
            if not plc:
                logging.warning("PLC client connection failed.")
                return None
            return plc
        except Exception as e:
            logging.warning(f"Failed to connect PLC client: {e}")
            return None

    def read_plc_data(self):
        plc = None
        try:
            plc = self.plc_client()
            if not plc:
                logging.warning("PLC connection failed. Using default values.")

            alarms = self._read_alarms(plc)
            equipment_status = self._read_status_data(plc)
            logging.info("Successfully read PLC data.")
            return alarms, equipment_status
        except Exception as e:
            logging.error(f"Error while reading PLC data: {e}", exc_info=True)
        finally:
            if plc:
                self._disconnect_plc(plc)

    def _read_alarms(self, plc):
        try:
            return read_alarms(plc, 8, 8)
        except Exception as e:
            logging.error(f"Error reading alarms from PLC: {e}", exc_info=True)
            return [0, 0, 0, 0]

    def _read_status_data(self, plc):
        try:
            return read_status_data(plc)
        except Exception as e:
            logging.error(f"Error reading status data from PLC: {e}", exc_info=True)
            return 0

    def _disconnect_plc(self, plc):
        try:
            plc_disconnect(plc)
            logging.info("PLC connection successfully closed.")
        except Exception as e:
            logging.error(f"Error during PLC disconnection: {e}", exc_info=True)

    def _write_alarm(self, db_address, byte, bit, value):
        try:
            plc = self.plc_client()
            if not plc:
                logging.error("Failed to connect to PLC. Cannot write alarm data.")
                return False

            result = write_alarms_data(db_address, byte, bit, value, plc)
            logging.info(
                f"Alarm data successfully written: Byte {byte}, Bit {bit}, Value {value}"
            )
            return result
        except Exception as e:
            logging.error(
                f"Error writing alarm data: Byte {byte}, Bit {bit}, Value {value} - {e}",
                exc_info=True,
            )
