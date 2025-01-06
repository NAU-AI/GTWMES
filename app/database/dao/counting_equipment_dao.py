import logging
from exception.Exception import DatabaseException
from model.counting_equipment import CountingEquipment
from database.connection.db_connection import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CountingEquipmentDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_equipment_by_code(self, code):
        if not code:
            raise ValueError("code cannot be empty")

        query = """
            SELECT id, code, equipment_status
            FROM counting_equipment
            WHERE code = %s
            LIMIT 1
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (code,))
                    row = cursor.fetchone()
                    return CountingEquipment.from_dict(row) if row else None
        except Exception as e:
            logger.error(
                f"Error fetching counting_equipment with code '{code}': {e}",
                exc_info=True,
            )
            raise DatabaseException("Failed to fetch counting equipment.") from e

    def get_all_equipment(self):
        query = """
            SELECT id, code, p_timer_communication_cycle
            FROM counting_equipment
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    return [CountingEquipment.from_dict(row) for row in rows]
        except Exception as e:
            logger.error(
                "Error fetching all counting equipment records.", exc_info=True
            )
            raise DatabaseException("Failed to fetch all counting equipment.") from e

    def insert_counting_equipment(self, data):
        self._validate_insert_data(data)

        query = """
            INSERT INTO counting_equipment (code, p_timer_communication_cycle)
            VALUES (%s, %s)
            RETURNING id;
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        query, (data["equipmentCode"], data["pTimerCommunicationCycle"])
                    )
                    counting_equipment_id = cursor.fetchone()["id"]
                    conn.commit()
                    logger.info(
                        f"Inserted counting equipment with ID {counting_equipment_id}."
                    )
                    return counting_equipment_id
        except Exception as e:
            logger.error(
                f"Error inserting counting equipment with code '{data.get('equipmentCode', 'unknown')}': {e}",
                exc_info=True,
            )
            raise DatabaseException("Failed to insert counting equipment.") from e

    def update_counting_equipment(self, data):
        self._validate_update_data(data)

        query = """
            UPDATE counting_equipment
            SET p_timer_communication_cycle = %s
            WHERE code = %s
            RETURNING id;
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        query, (data["pTimerCommunicationCycle"], data["equipmentCode"])
                    )
                    counting_equipment_id = cursor.fetchone()["id"]
                    conn.commit()
                    logger.info(
                        f"Updated counting equipment with ID {counting_equipment_id}."
                    )
                    return counting_equipment_id
        except Exception as e:
            logger.error(
                f"Error updating counting equipment with code '{data.get('equipmentCode', 'unknown')}': {e}",
                exc_info=True,
            )
            raise DatabaseException("Failed to update counting equipment.") from e
        
    def update_counting_equipment_status(self, equipment_status, equipment_id):
        if not equipment_status:
            raise ValueError("equipment_status cannot be empty")
        if not equipment_id:
            raise ValueError("equipment_id cannot be empty")

        query = """
            UPDATE counting_equipment
            SET equipment_status = %s
            WHERE id = %s
            RETURNING id;
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        query, (equipment_status, equipment_id)
                    )
                    counting_equipment_id = cursor.fetchone()["id"]
                    conn.commit()
                    logger.info(
                        f"Updated counting equipment status with ID {counting_equipment_id}."
                    )
                    return counting_equipment_id
        except Exception as e:
            logger.error(
                f"Error updating counting equipment status with id '{equipment_id}': {e}",
                exc_info=True,
            )
            raise DatabaseException("Failed to update counting equipment status.") from e

    def get_equipment_by_id(self, equipment_id):
        query = """
            SELECT id, code, equipment_status, p_timer_communication_cycle
            FROM counting_equipment
            WHERE id = %s
            LIMIT 1
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (equipment_id,))
                    row = cursor.fetchone()
                    return CountingEquipment.from_dict(row) if row else None
        except Exception as e:
            logger.error(
                f"Error fetching counting equipment with ID '{equipment_id}': {e}",
                exc_info=True,
            )
            raise DatabaseException("Failed to fetch counting equipment by ID.") from e

    @staticmethod
    def _validate_insert_data(data):
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")
        if "equipmentCode" not in data or not data["equipmentCode"]:
            raise ValueError("equipmentCode is required.")
        if "pTimerCommunicationCycle" not in data or not isinstance(
            data["pTimerCommunicationCycle"], int
        ):
            raise ValueError("pTimerCommunicationCycle must be an integer.")

    @staticmethod
    def _validate_update_data(data):
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")
        if "equipmentCode" not in data or not data["equipmentCode"]:
            raise ValueError("equipmentCode is required.")
        if "pTimerCommunicationCycle" not in data or not isinstance(
            data["pTimerCommunicationCycle"], int
        ):
            raise ValueError("pTimerCommunicationCycle must be an integer.")
