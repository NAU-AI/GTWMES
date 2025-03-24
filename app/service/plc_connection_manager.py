import time
from service.PLC.plc_client import PLCClient
from snap7.exceptions import Snap7Exception
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class PlcConnectionManager:
    def __init__(self, plc_client_factory=PLCClient):
        self.plc_client_factory = plc_client_factory
        self.plc_clients = {}

    def get_plc_client(self, ip: str) -> PLCClient:
        if ip not in self.plc_clients:
            while True:
                try:
                    client = self.plc_client_factory(ip)
                    client.connect()
                    self.plc_clients[ip] = client
                    logger.info("PLC client connected successfully to %s.", ip)
                    break
                except Snap7Exception as e:
                    logger.error(
                        "Failed to connect to PLC %s: %s. Retrying in 5 seconds...",
                        ip,
                        e,
                    )
                    time.sleep(5)
        return self.plc_clients[ip]

        return self.plc_clients[ip]

    def disconnect_all(self):
        for ip, client in self.plc_clients.items():
            try:
                client.disconnect()
                logger.info("Disconnected from PLC %s.", ip)
            except Snap7Exception as e:
                logger.error("Failed to disconnect PLC %s: %s", ip, e)
        self.plc_clients.clear()
