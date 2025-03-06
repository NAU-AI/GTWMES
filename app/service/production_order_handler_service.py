from service.production_order_service import ProductionOrderService

from service.equipment_service import EquipmentService
from service.message_service import MessageService
from exception.Exception import NotFoundException, ServiceException

from utility.logger import Logger


logger = Logger.get_logger(__name__)


class ProductionOrderHandlerService:
    def __init__(
        self,
        production_order_service: ProductionOrderService = None,
        equipment_service: EquipmentService = None,
        message_service: MessageService = None,
    ):
        self.production_order_service = (
            production_order_service or ProductionOrderService()
        )

        self.equipment_service = equipment_service or EquipmentService()
        self.message_service = message_service or MessageService()

    def process_production_order_init(self, message: dict):
        try:
            equipment_code = message.get("equipmentCode")

            production_order_code = message.get("productionOrderCode")

            if not equipment_code or not production_order_code:
                raise ValueError(
                    "Missing 'equipmentCode' or 'productionOrderCode' in message"
                )

            logger.info(
                f"Initializing new production order '{production_order_code}' for equipment '{equipment_code}'"
            )

            equipment = self.equipment_service.get_equipment_by_code(equipment_code)

            if not equipment:
                raise NotFoundException(
                    f"Equipment with code '{equipment_code}' not found"
                )

            new_production_order = (
                self.production_order_service.start_new_production_order(
                    equipment_id=equipment.id, code=production_order_code
                )
            )

            logger.info(
                f"Started production order '{new_production_order.code}' for equipment '{equipment.code}'"
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
            production_order = self._get_production_order(production_order_code)

            self.message_service.send_production_message(client, topic_send, equipment)

            completed = self.production_order_service.complete_production_order(
                production_order.id
            )

            if completed:
                logger.info(
                    f"Production order '{production_order.code}' was successfully marked as completed for equipment '{equipment.code}'."
                )
            else:
                logger.warning(
                    f"Production order '{production_order.code}' was already completed or does not exist for equipment '{equipment.code}'."
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

    def _get_production_order(self, production_order_code: str):
        return self.production_order_service.get_production_order_by_code(
            production_order_code
        )
