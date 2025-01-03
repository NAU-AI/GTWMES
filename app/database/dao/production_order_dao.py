import logging
from exception.Exception import DatabaseException
from model.production_order import ProductionOrder
from database.connection.db_connection import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionOrderDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_production_order_by_code_and_equipment_id(self, equipment_id, data):
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT *
                        FROM production_order
                        WHERE code = %s AND equipment_id = %s
                        """,
                        (data["productionOrderCode"], equipment_id),
                    )
                    row = cursor.fetchone()
                    return ProductionOrder.from_dict(row) if row else None
        except Exception as e:
            logger.error(
                f"Error fetching production order with code '{data.get('productionOrderCode', 'unknown')}' "
                f"from equipment {equipment_id}: {e}"
            )
            raise

    def get_all_production_order_by_equipment_id(self, equipment_id):
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT *
                        FROM production_order
                        WHERE equipment_id = %s
                        """,
                        (equipment_id,),
                    )
                    rows = cursor.fetchall()
                    return [ProductionOrder.from_dict(row) for row in rows]
        except Exception as e:
            logger.error(
                f"Error fetching all production orders for equipment ID {equipment_id}: {e}"
            )
            raise

    def get_production_order_by_equipment_id_and_status(self, equipment_id, status):
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT *
                        FROM production_order
                        WHERE equipment_id = %s AND is_completed = %s
                        """,
                        (equipment_id, status),
                    )
                    row = cursor.fetchone()
                    return ProductionOrder.from_dict(row) if row else None
        except Exception as e:
            logger.error(
                f"Error fetching production order for equipment {equipment_id} "
                f"with status={status}: {e}"
            )
            raise

    def insert_production_order(self, equipment_id, production_order_code):
        if equipment_id is None:
            raise ValueError("equipment_id cannot be null")
        if not production_order_code:
            raise ValueError("production_order_code cannot be empty")

        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO production_order (equipment_id, code, is_completed)
                        VALUES (%s, %s, %s)
                        RETURNING id;
                        """,
                        (
                            equipment_id,
                            production_order_code,
                            False,
                        ),
                    )
                    production_order_id = cursor.fetchone()["id"]
                    conn.commit()
                    logger.info(
                        f"Inserted production order with ID {production_order_id} for equipment {equipment_id}"
                    )
                    return production_order_id
        except Exception as e:
            logger.error(
                f"Error inserting production order for equipment {equipment_id}: {e}",
                exc_info=True,
            )
            raise DatabaseException("Failed to insert production order.") from e
        
    def update_production_order_status(self, equipment_id, status):
        if equipment_id is None:
            raise ValueError("equipment_id cannot be null")
        if not isinstance(status, bool):
            raise ValueError(
                "Invalid status. Only boolean values (True or False) are allowed."
            )

        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE production_order
                        SET is_completed = %s
                        WHERE equipment_id = %s
                        RETURNING id;
                        """,
                        (status, equipment_id),
                    )
                    result = cursor.fetchone()
                    if not result:
                        raise DatabaseException(
                            f"No production order found for equipment ID {equipment_id}"
                        )
                    production_order_id = result["id"]
                    conn.commit()
                    logger.info(
                        f"Updated production order status to {status} for equipment {equipment_id}."
                    )
                    return production_order_id
        except Exception as e:
            logger.error(
                f"Error changing production order status for equipment {equipment_id}: {e}",
                exc_info=True,
            )
            raise DatabaseException("Failed to update production order status.") from e