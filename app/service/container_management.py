from dependency_injector import containers, providers
from database.connection.db_connection import DatabaseConnection
from database.dao.equipment_dao import EquipmentDAO
from database.dao.variable_dao import VariableDAO
from mqtt_communication.mqtt_client_manager import ClientManager
from mqtt_communication.mqtt_heart_beat import MqttHeartbeatMonitor
from mqtt_communication.mqtt_message_handler import MessageHandler
from mqtt_communication.mqtt_message_processor import MessageProcessor
from service.configuration_handler_service import ConfigurationHandlerService
from service.equipment_service import EquipmentService
from service.message_service import MessageService
from service.plc_service import PlcService
from service.production_count_service import ProductionCountService
from service.production_order_handler_service import ProductionOrderHandlerService
from service.variable_service import VariableService


class ContainerManagement(containers.DeclarativeContainer):
    """Corrected Dependency Injection Container."""

    wiring_config = containers.WiringConfiguration(packages=["."])

    # Database connection
    db_connection = providers.Singleton(DatabaseConnection)

    # DAOs
    equipment_dao = providers.Factory(EquipmentDAO, db_connection=db_connection)
    variable_dao = providers.Factory(VariableDAO, db_connection=db_connection)

    # Core services
    equipment_service = providers.Factory(EquipmentService, equipment_dao=equipment_dao)
    variable_service = providers.Factory(VariableService, variable_dao=variable_dao)

    # Specialized services
    production_count_service = providers.Factory(
        ProductionCountService,
        variable_service=variable_service,
        equipment_service=equipment_service,
    )

    plc_service = providers.Factory(
        PlcService,
        equipment_service=equipment_service,
        variable_service=variable_service,
    )

    mqtt_heart_beat = providers.Factory(
        MqttHeartbeatMonitor,
        equipment_service=equipment_service,
        plc_service=plc_service,
    )

    message_service = providers.Factory(
        MessageService,
        equipment_service=equipment_service,
        production_count_service=production_count_service,
        mqtt_heart_beat=mqtt_heart_beat,
    )

    configuration_handler_service = providers.Factory(
        ConfigurationHandlerService,
        equipment_service=equipment_service,
        variable_service=variable_service,
        message_service=message_service,
        plc_service=plc_service,
    )

    production_order_handler_service = providers.Factory(
        ProductionOrderHandlerService,
        equipment_service=equipment_service,
        message_service=message_service,
        variable_service=variable_service,
        plc_service=plc_service,
    )

    message_handler = providers.Factory(
        MessageHandler,
        production_order_handler=production_order_handler_service,
        message_service=message_service,
        equipment_service=equipment_service,
        configuration_handler_service=configuration_handler_service,
    )

    message_processor = providers.Factory(
        MessageProcessor,
        message_handler=message_handler,
        message_service=message_service,
    )

    client_manager = providers.Factory(
        ClientManager,
        message_processor=message_processor,
    )
