from datetime import datetime
import json
import logging

from utility.scheduler import Scheduler
from MQTT.mqtt_heart_beat import MqttHeartbeatMonitor
from service.production_count_service import (
    ProductionCountService,
)

PRODUCTION_COUNT_MESSAGE_TYPE = "ProductionCount"


class MessageService:
    def __init__(self, production_count_service=None, mqtt_heart_beat=None):
        self.production_count_service = (
            production_count_service or ProductionCountService()
        )
        self.mqtt_heart_beat = mqtt_heart_beat or MqttHeartbeatMonitor()
        self.scheduler = Scheduler()

    def execute_production_count(self, client, topic_send):
        equipments = self.production_count_service.get_all_equipment()
        for equipment in equipments:
            task_id = f"equipment_{equipment.id}"
            self.scheduler.schedule_task(
                task_id=task_id,
                equipment=equipment,
                action=self.send_production_message,
                client=client,
                topic_send=topic_send,
            )
        logging.info("All equipment schedules initialized.")

    def send_production_message(self, client, topic_send, equipment):
        try:
            production_values = self.production_count_service.get_production_values(
                equipment
            )
            if not production_values:
                logging.warning(
                    f"No production values generated for equipment {equipment.id}."
                )
                return

            self.send_message_response(
                client, topic_send, production_values, PRODUCTION_COUNT_MESSAGE_TYPE
            )
            logging.info(f"Sent production message for equipment {equipment.id}.")
        except Exception as e:
            logging.error(
                f"Error sending production message for equipment {equipment.id}: {e}",
                exc_info=True,
            )

    def send_message_response(
        self, client, topic_send, data, message_type, default_production_order_code=""
    ):
        try:
            message = self.production_count_service.build_production_count(
                data=data,
                message_type=message_type,
                default_production_order_code=default_production_order_code,
            )
            if not message:
                logging.warning("No message generated. Skipping sending response.")
                return

            serialized_message = json.dumps(message, default=self._serialize_message)
            message_size = len(serialized_message.encode("utf-8"))

            max_size = 128 * 1024  # 128 KB limit for AWS IoT Core
            if message_size > max_size:
                logging.warning(
                    f"Message size {message_size} bytes exceeds AWS IoT Core limit of {max_size} bytes. "
                    "Truncating message."
                )
                # Truncate the message
                truncated_message = self.truncate_json_to_limit(message, max_size)
                serialized_message = json.dumps(truncated_message)
                message_size = len(serialized_message.encode("utf-8"))

            client.publish(topic_send, serialized_message, qos=1)
            logging.info(
                f"{message_type} message sent to topic '{topic_send}' (Size: {message_size} bytes)."
                f"{message_type} message sent to topic '{topic_send}': {serialized_message}"
            )
        except Exception as e:
            logging.error(f"Error while sending message response: {e}", exc_info=True)

    def truncate_json_to_limit(self, json_data, max_bytes):
        return self._fit_json(json_data, max_bytes)

    def _fit_json(self, data, limit_bytes):
        serialized = json.dumps(data)
        if len(serialized.encode("utf-8")) <= limit_bytes:
            return data

        if isinstance(data, dict):
            truncated = {}
            for key, value in data.items():
                reduced_value = self._fit_json(value, limit_bytes)
                temp_truncated = {**truncated, key: reduced_value}

                if len(json.dumps(temp_truncated).encode("utf-8")) > limit_bytes:
                    break

                truncated[key] = reduced_value
            return truncated

        if isinstance(data, list):
            truncated = []
            for item in data:
                reduced_item = self._fit_json(item, limit_bytes)
                temp_truncated = truncated + [reduced_item]

                if len(json.dumps(temp_truncated).encode("utf-8")) > limit_bytes:
                    break

                truncated.append(reduced_item)
            return truncated

        return data

    def message_received(self, client, topic_send, data):
        try:
            equipment_code = data.get("equipmentCode")
            if not equipment_code:
                logging.warning("Message ignored: 'equipmentCode' missing from data.")
                return

            logging.info(f"Message received for equipmentCode: {equipment_code}")
            self.mqtt_heart_beat.received_heartbeat(equipment_code)

        except Exception as e:
            logging.error(f"Error processing received message: {e}", exc_info=True)

    def _serialize_message(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError("Unserializable object encountered")
