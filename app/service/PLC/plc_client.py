import snap7
from snap7 import types, util
from snap7.exceptions import Snap7Exception
from service.PLC.plc_utils import require_connection
from service.PLC.plc_types import TYPE_SPECS
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class PLCClient:
    def __init__(self, ip, rack=0, slot=1):
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.plc = snap7.client.Client()

    def connect(self):
        try:
            self.plc.connect(self.ip, self.rack, self.slot)
            logger.info("Connected to PLC at %s", self.ip)
        except Snap7Exception as e:
            logger.error("Error connecting to PLC: %s", e)

    def disconnect(self):
        try:
            self.plc.disconnect()
            logger.info("Disconnected from PLC at %s", self.ip)
        except Snap7Exception as e:
            logger.error("Error disconnecting from PLC: %s", e)

    def is_connected(self):
        return self.plc.get_connected()

    @require_connection
    def read_data_package(self, data_package):
        if not data_package:
            logger.warning("Data package is empty. No data will be read.")
            return {}

        grouped_by_db = {}
        for item in data_package:
            grouped_by_db.setdefault(item["db"], []).append(item)

        results = {}

        for db_number, items in grouped_by_db.items():
            try:
                max_byte_offset = max(
                    item["byte"] + TYPE_SPECS[item["type"]]["amount"] for item in items
                )
                data = self.plc.read_area(
                    snap7.types.Areas.DB, db_number, 0, max_byte_offset
                )

                for item in items:
                    key = item.get(
                        "key",
                        "%s_db%s_byte%s" % (item["type"], db_number, item["byte"]),
                    )
                    try:
                        specs = TYPE_SPECS.get(item["type"])
                        if not specs:
                            logger.error("Unsupported type: %s", item["type"])
                            continue

                        extracted_data = data[
                            item["byte"] : item["byte"] + specs["amount"]
                        ]
                        results[key] = specs["convert"](extracted_data, item)

                    except (Snap7Exception, ValueError) as e:
                        logger.error("Error processing %s: %s", item, e)
                        results[key] = None

            except Snap7Exception as e:
                logger.error("Error reading DB %s: %s", db_number, e)
                continue

        return results

    @require_connection
    def read_bool(self, db_number, byte_offset, bit_offset):
        try:
            data = self.plc.read_area(types.Areas.DB, db_number, byte_offset, 1)
            return bool(data[0] & (1 << bit_offset))
        except Snap7Exception as e:
            logger.error("Error reading Boolean: %s", e)
            return None

    @require_connection
    def write_bool(self, db_number, byte_offset, bit_offset, value):
        try:
            data = self.plc.read_area(types.Areas.DB, db_number, byte_offset, 1)

            if value:
                data[0] |= 1 << bit_offset
            else:
                data[0] &= ~(1 << bit_offset)

            self.plc.write_area(types.Areas.DB, db_number, byte_offset, data)
            logger.info(
                "Boolean value at DB %s, Byte %s, Bit %s set to %s",
                db_number,
                byte_offset,
                bit_offset,
                value,
            )
        except Snap7Exception as e:
            logger.error("Error writing Boolean: %s", e)

    @require_connection
    def read_int(self, db_number, byte_offset):
        try:
            data = self.plc.read_area(types.Areas.DB, db_number, byte_offset, 2)
            return util.get_int(data, 0)
        except Snap7Exception as e:
            logger.error("Error reading integer: %s", e)
            return None

    @require_connection
    def write_int(self, db_number, byte_offset, value):
        try:
            data = bytearray(2)
            data[0] = (value >> 8) & 0xFF  # High byte
            data[1] = value & 0xFF  # Low byte
            self.plc.write_area(types.Areas.DB, db_number, byte_offset, data)
            logger.info(
                "Integer value at DB %s, Byte %s set to %s",
                db_number,
                byte_offset,
                value,
            )
        except Snap7Exception as e:
            logger.error("Error writing integer: %s", e)

    @require_connection
    def read_real(self, db_number, byte_offset):
        try:
            data = self.plc.read_area(types.Areas.DB, db_number, byte_offset, 4)
            return util.get_real(data, 0)
        except Snap7Exception as e:
            logger.error("Error reading real value: %s", e)
            return None

    @require_connection
    def write_real(self, db_number, byte_offset, value):
        try:
            data = bytearray(4)
            util.set_real(data, 0, value)
            self.plc.write_area(types.Areas.DB, db_number, byte_offset, data)
            logger.info(
                "Real value at DB %s, Byte %s set to %s", db_number, byte_offset, value
            )
        except Snap7Exception as e:
            logger.error("Error writing real value: %s", e)
