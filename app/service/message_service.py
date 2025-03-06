import json


from utility.scheduler import Scheduler


from MQTT.mqtt_heart_beat import MqttHeartbeatMonitor


from service.production_count_service import ProductionCountService


from service.equipment_service import EquipmentService


from utility.logger import Logger


logger = Logger.get_logger(__name__)


PRODUCTION_COUNT_MESSAGE_TYPE = "ProductionCount"


MAX_MQTT_MESSAGE_SIZE = 128 * 1024  # 128 KB limit for AWS IoT Core


class MessageService:
    def __init__(
        self,
        production_count_service: ProductionCountService = None,
        equipment_service: EquipmentService = None,
        mqtt_heart_beat: MqttHeartbeatMonitor = None,
    ):
        self.production_count_service = (
            production_count_service or ProductionCountService()
        )

        self.equipment_service = equipment_service or EquipmentService()

        self.mqtt_heart_beat = mqtt_heart_beat or MqttHeartbeatMonitor()

        self.scheduler = Scheduler()

    def execute_production_count(self, client, topic_send):
        try:
            equipments = self.equipment_service.get_all_equipment()

            if not equipments:
                logger.warning("No equipment found for production count execution.")
                return

            for equipment in equipments:
                task_id = f"equipment_{equipment.id}"

                interval = equipment.p_timer_communication_cycle or 1

                self.scheduler.schedule_task(
                    task_id=task_id,
                    equipment=equipment,
                    action=self.send_production_message,
                    client=client,
                    topic_send=topic_send,
                )

                logger.info(
                    f"Scheduled production message for equipment {equipment.id} "
                    f"every {interval} minutes."
                )

        except Exception as e:
            logger.error(f"Error executing production count: {e}", exc_info=True)

    def send_production_message(self, client, topic_send, equipment):
        try:
            production_values = self.production_count_service.build_production_count(
                equipment_code=equipment.code,
                message_type=PRODUCTION_COUNT_MESSAGE_TYPE,
            )

            if not production_values:
                logger.warning(
                    f"No production values generated for equipment {equipment.id}."
                )
                return

            self.send_message_response(client, topic_send, production_values)

            logger.info(f"Sent production message for equipment {equipment.id}.")

        except Exception as e:
            logger.error(
                f"Error sending production message for equipment {equipment.id}: {e}",
                exc_info=True,
            )

    def send_message_response(self, client, topic_send, data):
        try:
            serialized_message = json.dumps(data, default=str)

            message_size = len(serialized_message.encode("utf-8"))

            client.publish(topic_send, serialized_message, qos=1)

            logger.info(
                f"Sent message to '{topic_send}' (Size: {message_size} bytes): {serialized_message}"
            )

        except Exception as e:
            logger.error(f"Error while sending message response: {e}", exc_info=True)

    def message_received(self, client, topic_send, data):
        try:
            equipment_code = data.get("equipmentCode")

            if not equipment_code:
                logger.warning("Message ignored: 'equipmentCode' missing.")
                return

            logger.info(f"Message received for equipmentCode: {equipment_code}")

            self.mqtt_heart_beat.received_heartbeat(equipment_code)

        except Exception as e:
            logger.error(f"Error processing received message: {e}", exc_info=True)
