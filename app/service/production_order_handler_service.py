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
                f"Initializing production order '{production_order_code}' for equipment '{equipment_code}'"
            )

            equipment = self.equipment_service.get_equipment_by_code(equipment_code)
            if not equipment:
                raise NotFoundException(
                    f"Equipment with code '{equipment_code}' not found"
                )

            success = self.equipment_service.start_production_order(
                equipment.id, production_order_code
            )

            if success:
                self._save_and_write_plc(equipment, target_amount=3000, enabled=True)
                logger.info(
                    f"Production order '{production_order_code}' started for equipment '{equipment_code}'"
                )

        except Exception as e:
            logger.error(
                f"Error processing production order initialization: {e}", exc_info=True
            )
            raise ServiceException(
                "Failed to process production order initialization"
            ) from e

    def process_production_order_conclusion(self, client, topic_send, message: dict):
        try:
            equipment_code = message.get("equipmentCode")
            production_order_code = message.get("productionOrderCode")

            self._validate_message(equipment_code, production_order_code)

            logger.info(
                f"Completing production order '{production_order_code}' for equipment '{equipment_code}'"
            )

            equipment = self._get_equipment(equipment_code)

            success = self.equipment_service.complete_production_order(equipment.id)

            if success:
                self._save_and_write_plc(equipment, target_amount=0, enabled=False)
                logger.info(
                    f"Production order '{production_order_code}' completed for equipment '{equipment_code}'"
                )
                self.message_service.send_production_message(
                    client, topic_send, equipment
                )
            else:
                logger.warning(
                    f"Production order '{production_order_code}' is already completed or does not exist"
                )

        except Exception as e:
            logger.error(
                f"Error processing production order conclusion: {e}", exc_info=True
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
            raise NotFoundException(f"Equipment with code '{equipment_code}' not found")

    def _save_and_write_plc(self, equipment, target_amount: int, enabled: bool):
        variable_updates = {
            "targetAmount": target_amount,
            "isEquipmentEnabled": enabled,
        }

        for key, value in variable_updates.items():
            self.variable_service.update_variable_value(equipment.id, key, value)

        variables = (
            self.variable_service.get_variables_by_equipment_id_category_operation_type(
                equipment.id, "EQUIPMENT", "WRITE"
            )
        )

        plc_client = self.plc_service.get_plc_client(equipment.ip)

        if not plc_client:
            logger.error(f"PLC client unavailable for equipment '{equipment.code}'")
            return

        for variable in variables:
            if variable.type.upper() == "INT":
                plc_client.write_int(
                    variable.db_address, variable.offset_byte, variable.value
                )
            elif variable.type.upper() == "BOOL":
                plc_client.write_bool(
                    variable.db_address,
                    variable.offset_byte,
                    variable.offset_bit,
                    variable.value,
                )
            logger.info(
                f"Written '{variable.key}' with value '{variable.value}' to PLC for equipment '{equipment.code}'"
            )
