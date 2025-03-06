import os
from MQTT.protocol import Protocol
from service.production_order_handler_service import ProductionOrderHandlerService
from service.message_service import MessageService
from service.equipment_service import EquipmentService
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class MessageHandler:
    def __init__(self):
        self.production_order_handler = ProductionOrderHandlerService()
        self.message_service = MessageService()
        self.equipment_service = EquipmentService()
        self.topic_send = os.getenv("TOPIC_SEND")
        self.protocols = Protocol.get_jsonType(self)

    def handle_message(self, client, message):
        json_type = message.get("jsonType")

        if handler := self.protocols.get(json_type):
            handler(client, message)
        else:
            logger.warning(f"Unhandled jsonType: {json_type}. Message: {message}")

    def _process_message(self, client, message, handler, response_type):
        try:
            logger.info(f"Processing '{response_type}' message: {message}")

            handler(message)

            logger.info(f"Successfully handled '{response_type}'")

        except Exception as e:
            logger.error(
                f"Error processing '{response_type}' for jsonType {message.get('jsonType')}: {e}",
                exc_info=True,
            )

        finally:
            self._send_response(client, message, response_type)

    def _send_response(self, client, message, response_type):
        self.message_service.send_message_response(
            client, self.topic_send, message, f"{response_type}Response"
        )

    def _handle_configuration(self, client, message):
        self._process_message(
            client,
            message,
            self.equipment_service.update_equipment_variables,
            "Configuration",
        )

    def _handle_production_order_init(self, client, message):
        self._process_message(
            client,
            message,
            self.production_order_handler.process_production_order_init,
            "ProductionOrder",
        )

    def _handle_production_order_conclusion(self, client, message):
        self._process_message(
            client,
            message,
            self.production_order_handler.process_production_order_conclusion,
            "ProductionOrderConclusion",
        )

    def _handle_received_message(self, client, message):
        self.message_service.message_received(client, self.topic_send, message)
