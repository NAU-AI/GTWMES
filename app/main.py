from MQTT.mqtt_heart_beat import MqttHeartbeatMonitor
from MQTT.mqtt_message_processor import MessageProcessor
from MQTT.mqtt_client_manager import ClientManager
from utility.logger import Logger
from database.connection.db_connection import SessionLocal
from sqlalchemy.sql import text


class MESMain:
    def __init__(
        self, message_processor=None, client_manager=None, mqtt_heart_beat=None
    ):
        self.logger = Logger.get_logger(self.__class__.__name__)

        self.mqtt_heart_beat = mqtt_heart_beat or MqttHeartbeatMonitor()
        self.message_processor = message_processor or MessageProcessor()
        self.client_manager = client_manager or ClientManager(self.message_processor)

    def start(self):
        try:
            self.logger.info("Initializing MQTT connection...")
            self.client_manager.connect()

            self.logger.info("Starting periodic message service...")
            self.message_processor.start_periodic_messages(
                self.client_manager.client, self.client_manager.topic_send
            )

            self.logger.info("Starting heartbeat monitoring...")
            self.mqtt_heart_beat.start_monitoring()

            self.logger.info("Starting MQTT client loop...")
            self.client_manager.start_loop()

        except KeyboardInterrupt:
            self.shutdown()

        except Exception as e:
            self.logger.error(f" Unexpected error: {e}", exc_info=True)
            self.shutdown()

    def shutdown(self):
        self.logger.info(" Shutting down application...")
        try:
            self.mqtt_heart_beat.stop_monitoring()
            self.client_manager.disconnect()
            self.logger.info("Shutdown completed successfully.")
        except Exception as e:
            self.logger.error(f" Error during shutdown: {e}", exc_info=True)


def main():
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        mes_service = MESMain()
        mes_service.start()
    except Exception as e:
        Logger.get_logger(__name__).error(
            f"Critical startup failure: {e}", exc_info=True
        )
        exit(1)


if __name__ == "__main__":
    main()
