from dao.production_order_dao import ProductionOrderDAO
from model import ProductionOrder
from app.exception import NotFoundException, ServiceException
from app.utility.logger import Logger

logger = Logger.get_logger(__name__)


class ProductionOrderService:
    def __init__(self, production_order_dao: ProductionOrderDAO = None):
        self.production_order_dao = production_order_dao or ProductionOrderDAO()

    def get_production_order_by_id(self, order_id: int) -> ProductionOrder:
        try:
            order = self.production_order_dao.find_by_id(order_id)
            if not order:
                raise NotFoundException(
                    f"Production order with ID '{order_id}' not found"
                )
            return order
        except Exception as e:
            logger.error(
                f"Error fetching production order by ID '{order_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch production order.") from e

    def get_production_order_by_equipment_id_and_status(
        self, equipment_id: int, is_completed: bool
    ) -> list[ProductionOrder]:
        try:
            orders = self.production_order_dao.find_by_equipment_id(
                equipment_id, is_completed
            )
            return orders
        except Exception as e:
            logger.error(
                f"Error fetching production orders for equipment ID '{equipment_id}' with status '{is_completed}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch production orders.") from e

    def complete_production_order(self, order_id: int) -> bool:
        try:
            completed = self.production_order_dao.complete_production_order(order_id)
            if not completed:
                raise NotFoundException(
                    f"Production order with ID '{order_id}' not found or already completed"
                )

            logger.info(f"Completed production order with ID {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error completing production order: {e}", exc_info=True)
            raise ServiceException("Unable to complete production order.") from e

    def start_new_production_order(
        self, equipment_id: int, code: str
    ) -> ProductionOrder:
        try:
            new_order = self.production_order_dao.start_new_production_order(
                equipment_id, code
            )
            logger.info(
                f"Started new production order '{new_order.code}' for equipment ID {equipment_id}"
            )
            return new_order
        except Exception as e:
            logger.error(f"Error starting new production order: {e}", exc_info=True)
            raise ServiceException("Unable to start new production order.") from e

    def delete_production_order(self, order_id: int) -> bool:
        try:
            deleted = self.production_order_dao.delete(order_id)
            if not deleted:
                raise NotFoundException(
                    f"Production order with ID '{order_id}' not found"
                )

            logger.info(f"Deleted production order with ID {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting production order: {e}", exc_info=True)
            raise ServiceException("Unable to delete production order.") from e
