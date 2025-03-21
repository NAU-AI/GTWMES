import os

from mqtt.protocol import Protocol
from service.configuration_handler_service import ConfigurationHandlerService
from service.equipment_service import EquipmentService
from service.message_service import MessageService
from service.production_order_handler_service import ProductionOrderHandlerService
from sqlalchemy.orm import Session
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class MessageHandler:
    def __init__(self, session: Session):
        self.session = session
        self.production_order_handler = ProductionOrderHandlerService(session)
        self.message_service = MessageService(session)
        self.equipment_service = EquipmentService(session)
        self.configuration_handler_service = ConfigurationHandlerService(session)
        self.topic_send = os.getenv("TOPIC_SEND")
        self.protocols = Protocol.get_jsonType(self)

    def handle_message(self, client, message):
        json_type = message.get("jsonType")

        handler = self.protocols.get(json_type)
        if handler:
            self._process_message(client, message, handler, json_type)
        else:
            logger.warning("Unhandled jsonType: %s. Message: %s", json_type, message)

    def _process_message(self, client, message, handler, message_type: str):
        try:
            logger.info("Processing '%s' message: %s", message_type, message)
            handler(client, message)
            logger.info("Successfully handled '%s'", message_type)
        except Exception as e:
            logger.error(
                "Error processing '%s' for jsonType %s: %s",
                message_type,
                message.get("jsonType"),
                e,
                exc_info=True,
            )

    def _handle_configuration(self, client, message):
        self.configuration_handler_service.process_equipment_configuration(
            client, self.topic_send, message
        )

    def _handle_production_order_init(self, client, message):
        self.production_order_handler.process_production_order_init(
            client, self.topic_send, message
        )

    def _handle_production_order_conclusion(self, client, message):
        self.production_order_handler.process_production_order_conclusion(
            client, self.topic_send, message
        )

    def _handle_received_message(self, client, message):
        self.message_service.message_received(client, self.topic_send, message)
