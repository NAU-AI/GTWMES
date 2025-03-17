from service.equipment_service import EquipmentService
from service.message_service import MessageService
from exception.Exception import NotFoundException, ServiceException
from utility.logger import Logger
from sqlalchemy.orm import Session

logger = Logger.get_logger(__name__)


class ProductionOrderHandlerService:
    def __init__(self, session: Session):
        self.session = session
        self.equipment_service = EquipmentService(session)
        self.message_service = MessageService(session)

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
