import threading
import time

from service.PLC.plc_client import PLCClient
from snap7.exceptions import Snap7Exception
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class PlcConnectionManager:
    def __init__(self, plc_client_factory=PLCClient):
        self.plc_client_factory = plc_client_factory
        self.plc_clients = {}
        self.lock = threading.Lock()

    def get_plc_client(self, ip: str) -> PLCClient:
        with self.lock:
            if ip in self.plc_clients:
                return self.plc_clients[ip]

        client = self.plc_client_factory(ip)

        def try_connect_forever():
            while True:
                try:
                    client.connect()
                    with self.lock:
                        self.plc_clients[ip] = client
                    logger.info("PLC client connected successfully to %s.", ip)
                    break
                except (Snap7Exception, RuntimeError) as e:
                    logger.warning("Retrying connection to PLC %s: %s", ip, e)
                    time.sleep(60)

        threading.Thread(target=try_connect_forever, daemon=True).start()
        return client

    def disconnect_all(self):
        for ip, client in self.plc_clients.items():
            try:
                client.disconnect()
                logger.info("Disconnected from PLC %s.", ip)
            except Snap7Exception as e:
                logger.error("Failed to disconnect PLC %s: %s", ip, e)
        self.plc_clients.clear()
