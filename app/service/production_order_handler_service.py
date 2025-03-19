from service.equipment_service import EquipmentService
from service.message_service import MessageService
from service.variable_service import VariableService
from service.plc_service import PlcService
from exception.Exception import NotFoundException, ServiceException
from utility.logger import Logger
from sqlalchemy.orm import Session

logger = Logger.get_logger(__name__)


class ProductionOrderHandlerService:
    def __init__(self, session: Session):
        self.session = session
        self.equipment_service = EquipmentService(session)
        self.message_service = MessageService(session)
        self.variable_service = VariableService(session)
        self.plc_service = PlcService(session)

    def process_production_order_init(self, message: dict):
        try:
            equipment_code = message.get("equipmentCode")
            production_order_code = message.get("productionOrderCode")

            if not equipment_code or not production_order_code:
                raise ValueError(
                    "Missing 'equipmentCode' or 'productionOrderCode' in message"
                )

            logger.info(
                "Initializing production order '%s' for equipment '%s'",
                production_order_code,
                equipment_code,
            )

            equipment = self.equipment_service.get_equipment_by_code(equipment_code)
            if not equipment:
                raise NotFoundException(
                    "Equipment with code '%s' not found" % equipment_code
                )

            success = self.equipment_service.start_production_order(
                equipment.id, production_order_code
            )

            if success:
                self._save_and_write_plc(equipment, target_amount=3000, enabled=True)
                logger.info(
                    "Production order '%s' started for equipment '%s'",
                    production_order_code,
                    equipment_code,
                )

        except Exception as e:
            logger.error(
                "Error processing production order initialization: %s", e, exc_info=True
            )
            raise ServiceException(
                "Failed to process production order initialization"
            ) from e

    def process_production_order_conclusion(self, client, topic_send, message: dict):
        try:
            equipment_code = message.get("equipmentCode")
            production_order_code = message.get("productionOrderCode")

            if production_order_code is None:
                raise ValueError("productionOrderCode cannot be None")
            if equipment_code is None or production_order_code is None:
                raise ValueError(
                    "Missing 'equipmentCode' or 'productionOrderCode' in message"
                )
            self._validate_message(equipment_code, production_order_code)

            logger.info(
                "Completing production order '%s' for equipment '%s'",
                production_order_code,
                equipment_code,
            )

            if equipment_code is None:
                raise ValueError("equipmentCode cannot be None")
            equipment = self._get_equipment(equipment_code)

            success = self.equipment_service.complete_production_order(equipment.id)

            if success:
                self._save_and_write_plc(equipment, target_amount=0, enabled=False)
                logger.info(
                    "Production order '%s' completed for equipment '%s'",
                    production_order_code,
                    equipment_code,
                )
                self.message_service.send_production_message(
                    client, topic_send, equipment
                )
            else:
                logger.warning(
                    "Production order '%s' is already completed or does not exist",
                    production_order_code,
                )

        except Exception as e:
            logger.error(
                "Error processing production order conclusion: %s", e, exc_info=True
            )
            raise ServiceException("Failed to complete production order") from e

    def _validate_message(self, equipment_code: str, production_order_code: str):
        if not equipment_code or not production_order_code:
            raise ValueError(
                "Missing 'equipmentCode' or 'productionOrderCode' in message"
            )

    def _get_equipment(self, equipment_code: str):
        if equipment := self.equipment_service.get_equipment_by_code(equipment_code):
            return equipment
        else:
            raise NotFoundException(
                "Equipment with code '%s' not found" % equipment_code
            )

    def _save_and_write_plc(self, equipment, target_amount: int, enabled: bool):
        try:
            variable_updates = {
                "targetAmount": target_amount,
                "isEquipmentEnabled": enabled,
            }

            for key, value in variable_updates.items():
                self.variable_service.update_variable_value(equipment.id, key, value)

            variables = self.variable_service.get_variables_by_equipment_id_category_operation_type(
                equipment.id, "EQUIPMENT", "WRITE"
            )

            self.plc_service.write_equipment_variables(equipment.ip, variables)

            logger.info(
                "Successfully wrote PLC variables for equipment '%s'", equipment.code
            )

        except Exception as e:
            logger.error(
                "Error saving and writing PLC for '%s': %s",
                equipment.code,
                e,
                exc_info=True,
            )
