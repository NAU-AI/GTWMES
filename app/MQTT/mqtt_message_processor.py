import json
import threading

from MQTT.mqtt_message_handler import MessageHandler
from service.message_service import MessageService
from sqlalchemy.orm import Session
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class MessageProcessor:
    def __init__(self, session: Session, message_handler=None, message_service=None):
        self.message_handler = message_handler or MessageHandler(session)
        self.message_service = message_service or MessageService(session)

    def on_message(self, client, userdata, msg):
        try:
            message = json.loads(msg.payload)
            logger.info("Received message on topic '%s': %s", msg.topic, message)
            self.message_handler.handle_message(client, message)
        except json.JSONDecodeError as e:
            logger.error(
                "Error decoding message payload: %s. Error: %s", msg.payload, e
            )
        except Exception as e:
            logger.error("Error handling message: %s", e, exc_info=True)

    def start_periodic_messages(self, client, topic):
        try:
            periodically_messages_thread = threading.Thread(
                target=self.message_service.execute_production_count,
                args=(client, topic),
                daemon=True,
            )
            periodically_messages_thread.start()
            logger.info("Started periodic message sending thread.")
        except Exception as e:
            logger.error("Error starting periodic message thread: %s", e, exc_info=True)
