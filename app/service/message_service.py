import json

from sqlalchemy.orm import Session
from mqtt.constants.json_type import PRODUCTION_COUNT
from utility.scheduler import Scheduler
from utility.logger import Logger
from mqtt.mqtt_heart_beat import MqttHeartbeatMonitor
from service.production_count_service import ProductionCountService
from service.equipment_service import EquipmentService

logger = Logger.get_logger(__name__)


MAX_MQTT_MESSAGE_SIZE = 128 * 1024


class MessageService:
    def __init__(self, session: Session):
        self.session = session

        self.production_count_service = ProductionCountService(session=session)
        self.equipment_service = EquipmentService(session=session)
        self.mqtt_heart_beat = MqttHeartbeatMonitor(session=session)
        self.scheduler = Scheduler()

    def execute_production_count(self, client, topic_send):
        try:
            equipments = self.equipment_service.get_all_equipment()

            if not equipments:
                logger.warning("No equipment found for production count execution.")
                return

            for equipment in equipments:
                self.update_equipment_schedule(equipment, client, topic_send)

        except Exception as e:
            logger.error("Error executing production count: %s", e, exc_info=True)

    def send_production_message(
        self, client, topic_send, equipment, message_type=PRODUCTION_COUNT
    ):
        try:
            production_values = self.production_count_service.build_production_count(
                equipment_code=equipment.code,
                message_type=message_type,
            )

            if not production_values:
                logger.warning(
                    "No production values generated for equipment %s.", equipment.id
                )
                return

            self.send_message_response(client, topic_send, production_values)

            logger.info("Sent production message for equipment %s.", equipment.id)

        except Exception as e:
            logger.error(
                "Error sending production message for equipment %s: %s",
                equipment.id,
                e,
                exc_info=True,
            )

    @staticmethod
    def send_message_response(client, topic_send, data):
        try:
            serialized_message = json.dumps(data, default=str)

            message_size = len(serialized_message.encode("utf-8"))

            client.publish(topic_send, serialized_message, qos=1)

            logger.info(
                "Sent message to '%s' (Size: %d bytes): %s",
                topic_send,
                message_size,
                serialized_message,
            )

        except Exception as e:
            logger.error("Error while sending message response: %s", e, exc_info=True)

    def message_received(self, client, topic_send, data):
        try:
            equipment_code = data.get("equipmentCode")

            if not equipment_code:
                logger.warning("Message ignored: 'equipmentCode' missing.")
                return

            logger.info("Message received for equipmentCode: %s", equipment_code)

            self.mqtt_heart_beat.received_heartbeat(equipment_code)

        except Exception as e:
            logger.error("Error processing received message: %s", e, exc_info=True)

    def update_equipment_schedule(self, equipment, client, topic_send):
        task_id = f"equipment_{equipment.id}"

        if equipment.p_timer_communication_cycle is None:
            logger.warning(
                "Equipment %s has no communication cycle defined.", equipment.code
            )
            return

        current_metadata = self.scheduler.task_metadata.get(task_id)

        if current_metadata:
            current_interval = current_metadata["interval"] // 60

            if current_interval != equipment.p_timer_communication_cycle:
                logger.info(
                    "Updating scheduler for %s from %d to %d minutes.",
                    equipment.code,
                    current_interval,
                    equipment.p_timer_communication_cycle,
                )
                self.scheduler.cancel_task(task_id)

        self._schedule_equipment_task(equipment, client, topic_send)

    def _schedule_equipment_task(self, equipment, client, topic_send):
        task_id = f"equipment_{equipment.id}"

        logger.info(
            "Scheduling task for %s every %d minutes.",
            equipment.code,
            equipment.p_timer_communication_cycle,
        )

        self.scheduler.schedule_task(
            task_id=task_id,
            equipment=equipment,
            action=self.send_production_message,
            client=client,
            topic_send=topic_send,
        )
