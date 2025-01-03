import logging
import os
import threading
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

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
            logging.info(
                f"Connecting to MQTT broker at {self.broker_url}:{self.mqtt_port}"
            )
            self.client.connect(self.broker_url, self.mqtt_port)
        except Exception as e:
            logging.error(f"Initial connection failed: {e}. Triggering reconnection.")
            self.start_reconnect_loop()

    def start_reconnect_loop(self):
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            logging.warning("Reconnection thread already running.")
            return

        self.stop_reconnect_event.clear()

        def reconnect_loop():
            delay = self.reconnect_delay
            while not self.stop_reconnect_event.is_set():
                try:
                    logging.info("Attempting to reconnect to MQTT broker...")
                    self.client.reconnect()
                    logging.info("Reconnected to MQTT broker.")
                    break
                except Exception as e:
                    logging.error(f"Reconnection failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay = min(delay * self.reconnect_rate, self.max_reconnect_delay)

        self.reconnect_thread = threading.Thread(target=reconnect_loop, daemon=True)
        self.reconnect_thread.start()

    def stop_reconnect_loop(self):
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            logging.info("Stopping reconnection loop.")
            self.stop_reconnect_event.set()
            self.reconnect_thread.join()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT broker.")
            self.stop_reconnect_loop()
            self.subscribe()
        else:
            logging.error(f"Connection failed with result code {rc}. Retrying...")
            self.start_reconnect_loop()

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logging.warning(f"Unexpected disconnection. Reason code: {rc}")
            self.start_reconnect_loop()
        else:
            logging.info("Disconnected from MQTT broker.")

    def subscribe(self):
        if not self.topic_receive:
            logging.error("No topic specified for subscription. Exiting...")
            return

        try:
            self.client.subscribe(self.topic_receive, qos=1)
            logging.info(f"Subscribed to topic: {self.topic_receive}")
        except Exception as e:
            logging.error(f"Error during subscription: {e}")

    def start_loop(self):
        try:
            logging.info("Starting MQTT client loop...")
            self.client.loop_forever()
        except KeyboardInterrupt:
            logging.info("Ctrl+C pressed. Shutting down MQTT client.")
            self.disconnect()
        except Exception as e:
            logging.error(f"Unexpected error in MQTT client loop: {e}")

    def disconnect(self):
        try:
            logging.info("Disconnecting from MQTT broker...")
            self.stop_reconnect_loop()
            self.client.disconnect()
            logging.info("Successfully disconnected from MQTT broker.")
        except Exception as e:
            logging.error(
                f"Error occurred during MQTT disconnection: {e}", exc_info=True
            )
