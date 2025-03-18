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
            try:
                client = self.plc_client_factory(ip)
                client.connect()
                self.plc_clients[ip] = client
                logger.info(f"PLC client connected successfully to {ip}.")
            except Snap7Exception as e:
                logger.error(f"Failed to connect to PLC {ip}: {e}")
                return None

        return self.plc_clients[ip]

    def disconnect_all(self):
        for ip, client in self.plc_clients.items():
            try:
                client.disconnect()
                logger.info(f"Disconnected from PLC {ip}.")
            except Snap7Exception as e:
                logger.error(f"Failed to disconnect PLC {ip}: {e}")
        self.plc_clients.clear()
