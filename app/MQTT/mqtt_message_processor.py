import json
import logging
import threading

from service.message_service import MessageService
from MQTT.mqtt_message_handler import MessageHandler


class MessageProcessor:
    def __init__(self, message_handler=None, message_service=None):
        self.message_handler = message_handler or MessageHandler()
        self.message_service = message_service or MessageService()

    def on_message(self, client, userdata, msg):
        try:
            message = json.loads(msg.payload)
            logging.info(f"Received message on topic {msg.topic}: {message}")
            self.message_handler.handle_message(client, message)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding message payload: {msg.payload}. Error: {e}")
        except Exception as e:
            logging.error(f"Error handling message: {e}")

    def start_periodic_messages(self, client, topic):
        try:
            periodically_messages_thread = threading.Thread(
                target=self.message_service.execute_production_count,
                args=(client, topic),
                daemon=True,
            )
            periodically_messages_thread.start()
            logging.info("Started periodic message sending thread.")
        except Exception as e:
            logging.error(f"Error starting periodic message thread: {e}")
