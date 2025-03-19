import json
import threading
from sqlalchemy.orm import Session
from service.message_service import MessageService
from mqtt.mqtt_message_handler import MessageHandler
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class MessageProcessor:
    def __init__(self, session: Session, message_handler=None, message_service=None):
        self.message_handler = message_handler or MessageHandler(session)
        self.message_service = message_service or MessageService(session)

    def on_message(self, client, userdata, msg):
        try:
            message = json.loads(msg.payload)
            logger.info(f"Received message on topic '{msg.topic}': {message}")
            self.message_handler.handle_message(client, message)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding message payload: {msg.payload}. Error: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)

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
            logger.error(f"Error starting periodic message thread: {e}", exc_info=True)
