from service.production_order_service import ProductionOrderService

from service.equipment_service import EquipmentService

from model import ProductionOrder

from app.exception import NotFoundException, ServiceException

from app.utility.logger import Logger


logger = Logger.get_logger(__name__)


class ProductionOrderHandlerService:
    def __init__(
        self,
        production_order_service: ProductionOrderService = None,
        equipment_service: EquipmentService = None,
    ):
        self.production_order_service = (
            production_order_service or ProductionOrderService()
        )

        self.equipment_service = equipment_service or EquipmentService()

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

    def process_production_order_conclusion(self, message: dict):
        try:
            equipment_code = message.get("equipmentCode")
            production_order_code = message.get("productionOrderCode")

            if not equipment_code or not production_order_code:
                raise ValueError(
                    "Missing 'equipmentCode' or 'productionOrderCode' in message"
                )

            logger.info(
                f"Completing production order '{production_order_code}' for equipment '{equipment_code}'"
            )

            equipment = self.equipment_service.get_equipment_by_code(equipment_code)
            if not equipment:
                raise NotFoundException(
                    f"Equipment with code '{equipment_code}' not found"
                )

            production_orders = self.production_order_service.get_production_order_by_equipment_id_and_status(
                equipment.id, is_completed=False
            )
            matching_order = next(
                (po for po in production_orders if po.code == production_order_code),
                None,
            )

            if not matching_order:
                raise NotFoundException(
                    f"Active production order with code '{production_order_code}' not found for equipment '{equipment_code}'"
                )

            self.production_order_service.complete_production_order(matching_order.id)

            logger.info(
                f"Production order '{matching_order.code}' marked as completed for equipment '{equipment.code}'"
            )

        except Exception as e:
            logger.error(
                f"Error processing production order conclusion: {e}", exc_info=True
            )
            raise ServiceException("Failed to complete production order") from e
