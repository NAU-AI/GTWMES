import logging
from exception.Exception import DatabaseException
from model.equipment_output import EquipmentOutput
from database.connection.db_connection import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EquipmentOutputDAO:
    def __init__(self, db_connection=None):
        self.db = db_connection or DatabaseConnection()

    def get_output_by_equipment_id(self, equipment_id):
        if not equipment_id:
            raise ValueError("equipment_id cannot be empty")

        query = """
            SELECT *
            FROM equipment_output
            WHERE counting_equipment_id = %s
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (equipment_id,))
                    rows = cursor.fetchall()
                    return [EquipmentOutput.from_dict(row) for row in rows]
        except Exception as e:
            logger.error(
                f"Error fetching equipment outputs for equipment ID {equipment_id}: {e}",
                exc_info=True,
            )
            raise DatabaseException("Failed to fetch equipment outputs.") from e

    def get_output_by_equipment_id_and_code(self, equipment_id, code):
        if not equipment_id or not code:
            raise ValueError("equipment_id and code cannot be empty")

        query = """
            SELECT *
            FROM equipment_output
            WHERE counting_equipment_id = %s AND code = %s
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (equipment_id, code))
                    rows = cursor.fetchall()
                    return [EquipmentOutput.from_dict(row) for row in rows]
        except Exception as e:
            logger.error(
                f"Error fetching equipment outputs for equipment ID {equipment_id} with code {code}: {e}",
                exc_info=True,
            )
            raise DatabaseException(
                "Failed to fetch equipment outputs by ID and code."
            ) from e

    def get_equipment_output(self):
        query = "SELECT * FROM equipment_output"
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    return [EquipmentOutput.from_dict(row) for row in rows]
        except Exception as e:
            logger.error("Error fetching all equipment_output records.", exc_info=True)
            raise DatabaseException("Failed to fetch all equipment outputs.") from e

    def insert_equipment_output(self, counting_equipment_id, output_codes):
        if not counting_equipment_id or not output_codes:
            raise ValueError("counting_equipment_id and output_codes are required")

        query = """
            INSERT INTO equipment_output (counting_equipment_id, code)
            VALUES (%s, %s)
            RETURNING id;
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    equipment_output_ids = []
                    for code in output_codes:
                        cursor.execute(query, (counting_equipment_id, code))
                        equipment_output_id = cursor.fetchone()["id"]
                        equipment_output_ids.append(equipment_output_id)
                    conn.commit()
                    logger.info(
                        f"Inserted equipment outputs for counting_equipment_id {counting_equipment_id}"
                    )
                    return equipment_output_ids
        except Exception as e:
            logger.error(
                f"Error inserting equipment outputs for counting_equipment_id {counting_equipment_id}: {e}",
                exc_info=True,
            )
            raise DatabaseException("Failed to insert equipment outputs.") from e
