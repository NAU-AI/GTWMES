import logging
import datetime
from exception.Exception import DatabaseException
from model.counter_record import CounterRecord
from database.connection.db_connection import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CounterRecordDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def insert_counter_record(self, equipment_output_id, value):
        if not equipment_output_id or not value:
            raise ValueError("equipment_output_id and value cannot be null or empty")
        try:
             ct = datetime.datetime.now()
             with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO counter_record (equipment_output_id, real_value, registered_at)
                        VALUES (%s, %s, %s)
                        RETURNING id;
                        """,
                        (equipment_output_id, value, ct),
                    )
                    counter_record_id = cursor.fetchone()["id"]
                    conn.commit()
                    return counter_record_id          

        except Exception as e:
            logger.error(
                f"Failed inserting counter record for equipment_output_id {equipment_output_id}: {e}",
                exc_info=True,
            )
            raise DatabaseException(
                f"Error inserting counter record for equipment_output_id {equipment_output_id}"
            )

    def get_last_counter_record_by_equipment_output_id(self, equipment_output_id):
        if not equipment_output_id:
            raise ValueError("equipment_output_id is required")

        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT *
                        FROM counter_record
                        WHERE equipment_output_id = %s
                        ORDER BY id DESC LIMIT 1
                        """,
                        (equipment_output_id,),
                    )
                    row = cursor.fetchone()
                    return CounterRecord.from_dict(row) if row else None
        except Exception as e:
            logger.error(
                f"Error fetching counter record for equipment_output_id {equipment_output_id}: {e}",
                exc_info=True,
            )
            raise DatabaseException(
                "An error occurred while fetching the counter record."
            ) from e