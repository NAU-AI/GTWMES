import logging
from model.equipment_variables import EquipmentVariables
from exception.Exception import DatabaseException
from database.connection.db_connection import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EquipmentVariablesDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_equipment_variables_by_equipment_id(self, equipment_id):
        if not equipment_id:
            raise ValueError("equipment_id is required")
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT name, offset_byte, offset_bit, db_address, type
                        FROM equipment_variable
                        WHERE counting_equipment_id = %s;
                        """,
                        (equipment_id,),
                    )
                    rows = cursor.fetchall()
                    return rows
        except Exception as e:
            logger.error(
                f"Error fetching equipment variables for equipment_id {equipment_id}: {e}",
                exc_info=True,
            )
            raise DatabaseException(
                "An error occurred while fetching the equipment variables."
            ) from e

