import os
from sqlalchemy.orm import Session
from mqtt.protocol import Protocol
from service.production_order_handler_service import ProductionOrderHandlerService
from service.message_service import MessageService
from service.equipment_service import EquipmentService
from service.configuration_handler_service import ConfigurationHandlerService
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
        response_message = self._build_response_message(message)
        self.message_service.send_message_response(
            client, self.topic_send, response_message
        )

    def _build_response_message(self, data: dict) -> dict:
        response_data = data.copy()

        if "jsonType" in response_data:
            response_data["jsonType"] = f"{response_data['jsonType']}Response"

        return response_data

    def _handle_configuration(self, client, message):
        self._process_message(
            client,
            message,
            lambda msg: self.configuration_handler_service.process_equipment_configuration(
                client, self.topic_send, msg
            ),
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
            lambda msg: self.production_order_handler.process_production_order_conclusion(
                client,
                self.topic_send,
                msg,
            ),
            "ProductionOrderConclusion",
        )

    def _handle_received_message(self, client, message):
        self.message_service.message_received(client, self.topic_send, message)
