from service.PLC.snap7 import write_alarms_data, plc_connect, plc_disconnect
from app.utility.logger import Logger

logger = Logger.get_logger(__name__)


class PlcService:
    def __init__(self, plc_client=None, variable_service=None):
        self.plc_client = plc_client or self._default_plc_client

    def _default_plc_client(self):
        try:
            plc = plc_connect()
            if plc:
                return plc
            logger.warning("PLC client connection failed.")
        except Exception as e:
            logger.error(f"Failed to connect PLC client: {e}", exc_info=True)
        return None

    def write_alarm(self, db_address, byte, bit, value):
        plc = self.plc_client()
        if not plc:
            logger.error("Failed to connect to PLC. Cannot write alarm data.")
            return False

        try:
            result = write_alarms_data(db_address, byte, bit, value, plc)
            logger.info(
                f"Alarm data successfully written: Byte {byte}, Bit {bit}, Value {value}"
            )
            return result
        except Exception as e:
            logger.error(
                f"Error writing alarm data: Byte {byte}, Bit {bit}, Value {value} - {e}",
                exc_info=True,
            )
            return False
        finally:
            self._disconnect_plc(plc)

    def _disconnect_plc(self, plc):
        try:
            if plc:
                plc_disconnect(plc)
                logger.info("PLC connection successfully closed.")
        except Exception as e:
            logger.error(f"Error during PLC disconnection: {e}", exc_info=True)
