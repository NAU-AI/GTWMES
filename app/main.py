from MQTT.mqtt_heart_beat import MqttHeartbeatMonitor
from MQTT.mqtt_message_processor import MessageProcessor
from MQTT.mqtt_client_manager import ClientManager
from app.utility.logger import Logger
from connection.db_connection import DatabaseConnection


class MESMain:
    logger = Logger.get_logger(__name__)

    def __init__(
        self, message_processor=None, client_manager=None, mqtt_heart_beat=None
    ):
        self.mqtt_heart_beat = mqtt_heart_beat or MqttHeartbeatMonitor()
        self.message_processor = message_processor or MessageProcessor()
        self.client_manager = client_manager or ClientManager(self.message_processor)

    def start(self):
        try:
            self.logger.info("Starting MQTT connection.")
            self.client_manager.connect()
            self.logger.info("Initializing periodic message service.")
            self.message_processor.start_periodic_messages(
                self.client_manager.client, self.client_manager.topic_send
            )
            self.logger.info("Starting heartbeat monitoring.")
            self.mqtt_heart_beat.start_monitoring()
            self.logger.info("Starting MQTT client loop.")
            self.client_manager.start_loop()
        except KeyboardInterrupt:
            self.logger.info("Shutting down application.")
            self.mqtt_heart_beat.stop_monitoring()
            self.client_manager.disconnect()
            DatabaseConnection.close_pool()


def main():
    DatabaseConnection.initialize(minconn=1, maxconn=10)
    mqtt_service = MESMain()
    mqtt_service.start()


if __name__ == "__main__":
    main()
