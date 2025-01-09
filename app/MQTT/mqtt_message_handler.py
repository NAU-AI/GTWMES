import logging
import os

from MQTT.protocol import Protocol
from service.production_order_service import ProductionOrderService
from service.message_service import MessageService
from service.counting_equipment_service import CountingEquipmentService

class MessageHandler:
    def __init__(self):
        self.production_order_service = ProductionOrderService()
        self.message_service = MessageService()
        self.counting_equipment_service = CountingEquipmentService()
        self.topic_send = os.getenv("TOPIC_SEND")
        self.protocols = Protocol.get_jsonType(self)

    def handle_message(self, client, message):
        json_type = message.get("jsonType")
        handler = self.protocols.get(json_type)
        if handler:
            handler(client, message)
        else:
            logging.warning(f"Unhandled jsonType: {json_type}. Message: {message}")

    def _process_message(self, client, message, handler, response_type):
        try:
            logging.info(f"Processing '{response_type}' message: {message}")
            handler(message)
        except Exception as e:
            logging.error(
                f"Error processing '{response_type}' for jsonType {message.get('jsonType')}: {e}"
            )
        else:
            logging.info(f"Successfully handled '{response_type}'")
        finally:
            self.message_service.send_message_response(
                client, self.topic_send, message, f"{response_type}Response"
            )

    def _handle_configuration(self, client, message):
        self._process_message(
            client,
            message,
            self.counting_equipment_service.update_equipment_configuration,
            "Configuration",
        )

    def _handle_production_order(self, client, message):
        self._process_message(
            client,
            message,
            self.production_order_service.production_order_init,
            "ProductionOrder",
        )

    def _handle_production_order_conclusion(self, client, message):
        self._process_message(
            client,
            message,
            self.production_order_service.production_order_conclusion,
            "ProductionOrderConclusion",
        )

    def _handle_received_message(self, client, message):
        self.message_service.message_received(client, self.topic_send, message)
