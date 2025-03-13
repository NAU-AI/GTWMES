import snap7
from snap7 import types, util
import logging
from plc_utils import require_connection

logger = logging.getLogger(__name__)

class PLCClient:
    def __init__(self, ip, rack=0, slot=1):
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.plc = snap7.client.Client()

    def connect(self):
        try:
            self.plc.connect(self.ip, self.rack, self.slot)
            logger.info(f"Connected to PLC at {self.ip}")
        except snap7.exceptions.Snap7Exception as e:
            logger.error(f"Error connecting to PLC: {e}")

    def disconnect(self):
        try:
            self.plc.disconnect()
            logger.info(f"Disconnected from PLC at {self.ip}")
        except snap7.exceptions.Snap7Exception as e:
            logger.error(f"Error disconnecting from PLC: {e}")

    def is_connected(self):
        return self.plc.get_connected()

    @require_connection
    def read_bool(self, db_number, byte_offset, bit_offset):
        try:
            data = self.plc.read_area(types.Areas.DB, db_number, byte_offset, 1)
            return bool(data[0] & (1 << bit_offset))
        except snap7.exceptions.Snap7Exception as e:
            logger.error(f"Error reading Boolean: {e}")
            return None

    @require_connection
    def write_bool(self, db_number, byte_offset, bit_offset, value):
        try:
            data = self.plc.read_area(types.Areas.DB, db_number, byte_offset, 1)
            if data is None or len(data) == 0:
                logger.error(f"Failed to read byte for modifying bit at DB {db_number}, Byte {byte_offset}")
                return

            modified_data = bytearray(data)
            if value:
                modified_data[0] |= (1 << bit_offset)
            else:
                modified_data[0] &= ~(1 << bit_offset)

            self.plc.write_area(types.Areas.DB, db_number, byte_offset, modified_data)
            logger.info(f"Boolean value at DB {db_number}, Byte {byte_offset}, Bit {bit_offset} set to {value}")
        except snap7.exceptions.Snap7Exception as e:
            logger.error(f"Error writing Boolean: {e}")

    @require_connection
    def read_int(self, db_number, byte_offset):
        try:
            data = self.plc.read_area(types.Areas.DB, db_number, byte_offset, 2)
            return util.get_int(data, 0)
        except snap7.exceptions.Snap7Exception as e:
            logger.error(f"Error reading integer: {e}")
            return None

    @require_connection
    def write_int(self, db_number, byte_offset, value):
        try:
            data = bytearray(2)
            util.set_int(data, 0, value)
            self.plc.write_area(types.Areas.DB, db_number, byte_offset, data)
            logger.info(f"Integer value at DB {db_number}, Byte {byte_offset} set to {value}")
        except snap7.exceptions.Snap7Exception as e:
            logger.error(f"Error writing integer: {e}")

    @require_connection
    def read_real(self, db_number, byte_offset):
        try:
            data = self.plc.read_area(types.Areas.DB, db_number, byte_offset, 4)
            return util.get_real(data, 0)
        except snap7.exceptions.Snap7Exception as e:
            logger.error(f"Error reading real value: {e}")
            return None

    @require_connection
    def write_real(self, db_number, byte_offset, value):
        try:
            data = bytearray(4)
            util.set_real(data, 0, value)
            self.plc.write_area(types.Areas.DB, db_number, byte_offset, data)
            logger.info(f"Real value at DB {db_number}, Byte {byte_offset} set to {value}")
        except snap7.exceptions.Snap7Exception as e:
            logger.error(f"Error writing real value: {e}")

    @require_connection
    def read_data_packet(self, data_packet):
        if not self.is_connected():
            logger.error("PLC is not connected.")
            return None

        ctypes_items = [types.S7DataItem() for _ in data_packet]

        for i, item in enumerate(data_packet):
            ctypes_items[i].Area = types.Areas.DB
            ctypes_items[i].DBNumber = item["db"]
            ctypes_items[i].Start = item["byte"]
            ctypes_items[i].Amount = 1 if item["type"] == "bool" else (2 if item["type"] == "int" else 4)
            ctypes_items[i].WordLen = types.S7WLByte if item["type"] == "bool" else (
                types.S7WLWord if item["type"] == "int" else types.S7WLReal
            )

        ctypes_array = (types.S7DataItem * len(ctypes_items))(*ctypes_items)
        result = self.plc.read_multi_vars(ctypes_array)

        if result != 0:
            logger.error(f"read_multi_vars() failed with error code: {result}")
            return None

        results = {}

        for i, item in enumerate(data_packet):
            try:
                data = ctypes_array[i].Data
                if data is None:
                    raise ValueError("Data is None")

                if item["type"] == "bool":
                    value = bool(data[0] & (1 << item["bit"]))
                elif item["type"] == "int":
                    value = util.get_int(data, 0)
                elif item["type"] == "real":
                    value = util.get_real(data, 0)
                else:
                    logger.error(f"Unsupported data type: {item['type']}")
                    value = None

                key = item.get("key", f"{item['type']}_db{item['db']}_byte{item['byte']}")
                results[key] = value
            except Exception as e:
                logger.error(f"Error reading {item}: {e}")
                results[item.get("key", f"{item['type']}_db{item['db']}_byte{item['byte']}")] = None

        return results

