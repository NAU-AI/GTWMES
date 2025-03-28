import sys
from service.container_management import ContainerManagement
from database.connection.db_connection import DatabaseConnection

from utility.logger import Logger

logger = Logger.get_logger(__name__)


class MESMain:
    def __init__(
        self,
        message_processor,
        client_manager,
        mqtt_heart_beat,
        plc_service,
    ):
        self.logger = Logger.get_logger(self.__class__.__name__)
        self.message_processor = message_processor
        self.client_manager = client_manager
        self.mqtt_heart_beat = mqtt_heart_beat
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


def check_database_connection(db_connection: DatabaseConnection):
    if not db_connection.check_connection():
        logger.critical("Critical startup failure: Unable to connect to the database.")
        sys.exit(1)


def main():
    # Initialize the DI container
    container = ContainerManagement()

    # Check database connection
    check_database_connection(container.db_connection())

    # Resolve dependencies
    message_processor = container.message_processor()
    client_manager = container.client_manager()
    mqtt_heart_beat = container.mqtt_heart_beat()
    plc_service = container.plc_service()

    # Initialize and start the MES service
    mes_service = MESMain(
        message_processor=message_processor,
        client_manager=client_manager,
        mqtt_heart_beat=mqtt_heart_beat,
        plc_service=plc_service,
    )
    mes_service.start()


if __name__ == "__main__":
    main()
