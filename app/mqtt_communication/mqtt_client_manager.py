import os
import threading
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from utility.logger import Logger

logger = Logger.get_logger(__name__)

load_dotenv()

RECONNECT_DELAY = 60


class ClientManager:
    def __init__(self, message_processor):
        self.client_id = os.getenv("CLIENT_ID")
        self.broker_url = os.getenv("BROKER_URL")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 8883))
        self.topic_receive = os.getenv("TOPIC_RECEIVE")
        self.topic_send = os.getenv("TOPIC_SEND")
        self.reconnect_delay = int(os.getenv("FIRST_RECONNECT_DELAY", 1))
        self.max_reconnect_delay = int(os.getenv("MAX_RECONNECT_DELAY", 30))
        self.reconnect_rate = int(os.getenv("RECONNECT_RATE", 2))

        self._validate_environment()

        self.client = mqtt.Client(client_id=self.client_id)
        self.client.tls_set(
            ca_certs=os.getenv("CA_CERT"),
            certfile=os.getenv("CERTFILE"),
            keyfile=os.getenv("KEYFILE"),
        )

        self.message_processor = message_processor
        self.client.on_connect = self.on_connect
        self.client.on_message = self.message_processor.on_message
        self.client.on_disconnect = self.on_disconnect

        self.reconnect_thread = None
        self.stop_reconnect_event = threading.Event()

    def _validate_environment(self):
        if not self.broker_url:
            raise EnvironmentError(
                "Environment variable 'broker_url' is missing or invalid."
            )
        if not self.topic_receive:
            raise EnvironmentError(
                "Environment variable 'topicReceive' is missing or invalid."
            )
        if not self.topic_send:
            raise EnvironmentError(
                "Environment variable 'topicSend' is missing or invalid."
            )

    def connect(self):
        try:
            logger.info(
                "Connecting to MQTT broker at %s:%s", self.broker_url, self.mqtt_port
            )
            self.client.connect(self.broker_url, self.mqtt_port)
        except Exception as e:
            logger.error("Initial connection failed: %s. Triggering reconnection.", e)
            self.start_reconnect_loop()

    def start_reconnect_loop(self):
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            logger.warning("Reconnection thread already running.")
            return

        self.stop_reconnect_event.clear()

        def reconnect_loop():
            delay = self.reconnect_delay
            while not self.stop_reconnect_event.is_set():
                try:
                    logger.info("Attempting to reconnect to MQTT broker...")
                    self.client.reconnect()
                    logger.info("Reconnected to MQTT broker.")
                    break
                except Exception as e:
                    logger.error(
                        "Reconnection failed: %s. Retrying in %s seconds...", e, delay
                    )
                    time.sleep(delay)
                    delay = min(delay * self.reconnect_rate, self.max_reconnect_delay)

        self.reconnect_thread = threading.Thread(target=reconnect_loop, daemon=True)
        self.reconnect_thread.start()

    def stop_reconnect_loop(self):
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            logger.info("Stopping reconnection loop.")
            self.stop_reconnect_event.set()
            self.reconnect_thread.join()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker.")
            self.stop_reconnect_loop()
            self.subscribe()
        else:
            logger.error("Connection failed with result code %s. Retrying...", rc)
            self.start_reconnect_loop()

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning("Unexpected disconnection. Reason code: %s", rc)
            self.start_reconnect_loop()
        else:
            logger.info("Disconnected from MQTT broker.")

    def subscribe(self):
        if not self.topic_receive:
            logger.error("No topic specified for subscription. Exiting...")
            return

        try:
            self.client.subscribe(self.topic_receive, qos=1)
            logger.info("Subscribed to topic: %s", self.topic_receive)
        except Exception as e:
            logger.error("Error during subscription: %s", e)

    def start_loop(self):
        try:
            logger.info("Starting MQTT client loop...")
            self.client.loop_forever()
        except KeyboardInterrupt:
            logger.info("Ctrl+C pressed. Shutting down MQTT client.")
            self.disconnect()
        except Exception as e:
            logger.error("Unexpected error in MQTT client loop: %s", e)

    def disconnect(self):
        try:
            logger.info("Disconnecting from MQTT broker...")
            self.stop_reconnect_loop()
            self.client.disconnect()
            logger.info("Successfully disconnected from MQTT broker.")
        except Exception as e:
            logger.error(
                "Error occurred during MQTT disconnection: %s", e, exc_info=True
            )
