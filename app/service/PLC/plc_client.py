import snap7
from snap7 import types
import logging
from snap7.exceptions import Snap7Exception
from plc_utils import require_connection
from plc_types import TYPE_SPECS 

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
        except Snap7Exception as e:
            logger.error(f"Error connecting to PLC: {e}")

    def disconnect(self):
        try:
            self.plc.disconnect()
            logger.info(f"Disconnected from PLC at {self.ip}")
        except Snap7Exception as e:
            logger.error(f"Error disconnecting from PLC: {e}")

    def is_connected(self):
        return self.plc.get_connected()

    @require_connection
    def read_data_packet(self, data_packet):
        ctypes_items = []

        for item in data_packet:
            specs = TYPE_SPECS.get(item["type"])
            if not specs:
                logger.error(f"Unsupported type: {item['type']}")
                continue
            
            s7_item = types.S7DataItem()
            s7_item.Area = types.Areas.DB
            s7_item.DBNumber = item["db"]
            s7_item.Start = item["byte"]
            s7_item.Amount = specs["amount"]
            s7_item.WordLen = specs["wordlen"]
            ctypes_items.append(s7_item)

        ctypes_array = (types.S7DataItem * len(ctypes_items))(*ctypes_items)

        try:
            result = self.plc.read_multi_vars(ctypes_array)
            if result != 0:
                logger.error(f"read_multi_vars() failed with error code: {result}")
                return None
        except (Snap7Exception, ValueError) as e:
            logger.error(f"Error reading data packet: {e}")
            return None

        results = {}
        for i, item in enumerate(data_packet):
            key = item.get("key", f"{item['type']}_db{item['db']}_byte{item['byte']}")
            try:
                data = ctypes_array[i].Data
                if data is None:
                    raise ValueError("Data is None")

                specs = TYPE_SPECS.get(item["type"])
                results[key] = specs["convert"](data, item) if specs else None
            except (Snap7Exception, ValueError) as e:
                logger.error(f"Error reading {item}: {e}")
                results[key] = None
        
        return results
