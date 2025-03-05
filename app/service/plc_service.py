import logging
from service.active_time_service import ActiveTimeService
from service.alarm_service import AlarmService
from service.counter_record_service import CounterRecordService
from service.counting_equipment_service import CountingEquipmentService
from service.equipment_output_service import EquipmentOutputService
from service.PLC.snap7 import (
    read_bool,
    read_int,
    read_real,
    write_alarms_data,
    read_uint,
    write_bool,
    write_int,
)
from service.PLC.snap7 import plc_connect, plc_disconnect
from variable_service import (
    EquipmentVariablesService,
)


class PlcService:
    def __init__(
        self,
        plc_client=None,
        equipment_variables_service=None,
        active_time_service=None,
        alarm_service=None,
        counting_equipment_service=None,
        equipment_output_service=None,
        counter_record_service=None,
    ):
        self.plc_client = plc_client or self._default_plc_client
        self.equipment_variables_service = (
            equipment_variables_service or EquipmentVariablesService()
        )
        self.alarm_service = alarm_service or AlarmService()
        self.counting_equipment_service = (
            counting_equipment_service or CountingEquipmentService()
        )
        self.equipment_output_service = (
            equipment_output_service or EquipmentOutputService()
        )
        self.active_time_service = active_time_service or ActiveTimeService()
        self.counter_record_service = counter_record_service or CounterRecordService()

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

    def read_plc_data(self, equipment_id):
        plc = None
        try:
            plc = self.plc_client()
            if not plc:
                logging.warning("PLC connection failed. Using default values.")

            variables = self.equipment_variables_service.get_equipment_variables(
                equipment_id
            )
            if variables:
                self._process_alarms(plc, equipment_id, variables["alarms"])
                self._process_equipment_status(
                    plc, equipment_id, variables["equipment_status"]
                )
                self._process_outputs(plc, equipment_id, variables["outputs"])
                self._process_active_time(plc, equipment_id, variables["active_time"])

            logging.info("Successfully read PLC data.")
            return variables
        except Exception as e:
            logging.error(f"Error while reading PLC data: {e}", exc_info=True)
        finally:
            if plc:
                self._disconnect_plc(plc)

    def _process_alarms(self, plc, equipment_id, alarms):
        if not plc:
            logging.warning("PLC connection failed. Using default values.")
        alarms = self._read_arrays(plc, alarms)
        if alarms is not None:
            existing_alarm = self.alarm_service.get_latest_alarm(equipment_id)
            if existing_alarm is None:
                self.alarm_service.insert_alarm(equipment_id, alarms)
            else:
                self.alarm_service.update_alarm(equipment_id, alarms)

    def _process_equipment_status(self, plc, equipment_id, equipment_status):
        if not plc:
            logging.warning("PLC connection failed. Using default values.")
        equipment_status = self._read_element(plc, equipment_status)
        if equipment_status is not None:
            self.counting_equipment_service.update_equipment_status(
                equipment_status, equipment_id
            )

    def _process_outputs(self, plc, equipment_id, outputs):
        if not plc:
            logging.warning("PLC connection failed. Using default values.")
        outputs = self._read_arrays(plc, outputs)
        if outputs is not None:
            equipment_outputs = self.equipment_output_service.get_by_equipment_id(
                equipment_id
            )
            if not equipment_outputs or len(equipment_outputs) != len(outputs):
                logging.error(
                    f"Mismatch between equipment_outputs (length: {len(equipment_outputs)}) "
                    f"and outputs (length: {len(outputs)}) for equipment_id: {equipment_id}."
                )
                return

            for equipment_output, output_value in zip(equipment_outputs, outputs):
                self.counter_record_service.insert_counter_record(
                    equipment_output.id, output_value
                )

    def _process_active_time(self, plc, equipment_id, active_time):
        if not plc:
            logging.warning("PLC connection failed. Using default values.")
        active_time = self._read_element(plc, active_time)
        if active_time is not None:
            self.active_time_service.insert_active_time(equipment_id, active_time)

    def _read_element(self, plc, variable):
        try:
            if not plc:
                logging.warning("PLC connection failed. Using default values.")
            variable = self._get_read_function(plc, variable, variable["type"])
            if variable is not None:
                return variable
            else:
                return 0
        except Exception as e:
            logging.error(f"Error reading variable data from PLC: {e}", exc_info=True)
            return 0

    def _read_arrays(self, plc, data_array):
        try:
            if not plc:
                logging.warning("PLC connection failed. Using default values.")
            final_array = []
            for data in data_array:
                value = self._get_read_function(plc, data, data["type"])
                if value is not None:
                    final_array.append(value)
                else:
                    final_array.append(0)
            return final_array
        except Exception as e:
            logging.error(f"Error reading data_array from PLC: {e}", exc_info=True)
            return [0] * len(data_array)

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
        finally:
            if plc:
                self._disconnect_plc(plc)

    def _read_uint(self, plc, data):
        return read_uint(plc, int(data["db_address"]), data["offset_byte"])

    def _read_int(self, plc, data):
        return read_int(plc, int(data["db_address"]), data["offset_byte"])

    def _read_bool(self, plc, data):
        return read_bool(
            plc, int(data["db_address"]), data["offset_byte"], data["offset_bit"]
        )

    def _read_real(self, plc, data):
        return read_real(plc, int(data["db_address"]), data["offset_byte"])

    def _get_read_function(self, plc, data, data_type):
        if data_type == "uint":
            return self._read_uint(plc, data)
        elif data_type == "int":
            return self._read_int(plc, data)
        elif data_type == "bool":
            return self._read_bool(plc, data)
        elif data_type == "real":
            return self._read_real(plc, data)
        else:
            raise ValueError(f"Unknown data type: {data_type}")

    def _write_int(self, data, value):
        try:
            plc = self.plc_client()
            if not plc:
                logging.error("Failed to connect to PLC. Cannot write data.")
                return False

            logging.info(f"Int data successfully written")
            return write_int(plc, int(data["db_address"]), data["offset_byte"], value)
        except Exception as e:
            logging.error(
                f"Error writing Int data - {e}",
                exc_info=True,
            )
        finally:
            if plc:
                self._disconnect_plc(plc)

    def _write_bool(self, data, value):
        try:
            plc = self.plc_client()
            if not plc:
                logging.error("Failed to connect to PLC. Cannot write data.")
                return False

            logging.info(f"Bool data successfully written")
            return write_bool(
                plc,
                int(data["db_address"]),
                data["offset_byte"],
                data["offset_bit"],
                value,
            )
        except Exception as e:
            logging.error(
                f"Error writing Bool data - {e}",
                exc_info=True,
            )
        finally:
            if plc:
                self._disconnect_plc(plc)

    def _get_write_function(self, data, data_type, value):
        if data_type == "int":
            return self._write_int(data, value)
        elif data_type == "bool":
            return self._write_bool(data, value)
        else:
            raise ValueError(f"Unknown data type: {data_type}")
