import sys

from database.connection.db_connection import DatabaseConnection
from mqtt_communication.mqtt_client_manager import ClientManager
from mqtt_communication.mqtt_heart_beat import MqttHeartbeatMonitor
from mqtt_communication.mqtt_message_processor import MessageProcessor
from service.plc_service import PlcService
from sqlalchemy import text
from utility.logger import Logger

logger = Logger.get_logger(__name__)

db_connection = DatabaseConnection()


class MESMain:
    def __init__(
        self,
        message_processor: MessageProcessor,
        client_manager: ClientManager,
        mqtt_heart_beat: MqttHeartbeatMonitor,
        plc_service: PlcService,
    ):
        self.logger = Logger.get_logger(self.__class__.__name__)
        self.mqtt_heart_beat = mqtt_heart_beat
        self.message_processor = message_processor
        self.client_manager = client_manager
        self.plc_service = plc_service

    def start(self):
        try:
            self.logger.info("Initializing MQTT connection...")
            self.client_manager.connect()

            self.logger.info("Connecting to PLCs at startup...")
            self.plc_service.connect_all_plcs()

            self.logger.info("Starting PLC periodic data reading...")
            self.plc_service.schedule_plc_readings()

            self.logger.info("Starting periodic message service...")
            self.message_processor.start_periodic_messages(
                self.client_manager.client, self.client_manager.topic_send
            )

            self.logger.info("Starting heartbeat monitoring...")
            self.mqtt_heart_beat.start_monitoring()

            self.logger.info("Starting MQTT client loop...")
            self.client_manager.start_loop()

        except KeyboardInterrupt:
            self.logger.warning(
                "Keyboard interrupt received. Shutting down gracefully..."
            )
            self.shutdown()

        except Exception as e:
            self.logger.error("Unexpected error: %s", e, exc_info=True)
            self.shutdown()

    def shutdown(self):
        self.logger.info("Shutting down application...")
        try:
            self.logger.info("Stopping heartbeat monitoring...")
            self.mqtt_heart_beat.stop_monitoring()

            self.logger.info("Disconnecting MQTT client...")
            self.client_manager.disconnect()

            self.logger.info("Disconnecting PLCs...")
            self.plc_service.shutdown()

            self.logger.info("Shutdown completed successfully.")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}", exc_info=True)
        finally:
            sys.exit(1)


def check_database_connection():
    if not db_connection.check_connection():
        logger.critical("Critical startup failure: Unable to connect to the database.")
        sys.exit(1)


def initialize_mes_service() -> MESMain:
    with db_connection.get_session() as session:
        message_processor = MessageProcessor(session=session)
        client_manager = ClientManager(message_processor)
        mqtt_heart_beat = MqttHeartbeatMonitor(session=session)
        plc_service = PlcService(session=session)

        return MESMain(
            message_processor=message_processor,
            client_manager=client_manager,
            mqtt_heart_beat=mqtt_heart_beat,
            plc_service=plc_service,
        )


def main():
    check_database_connection()
    mes_service = initialize_mes_service()
    mes_service.start()


if __name__ == "__main__":
    main()
