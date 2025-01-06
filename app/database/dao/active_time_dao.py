import logging
from exception.Exception import DatabaseException
from model.active_time import ActiveTime
from database.connection.db_connection import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActiveTimeDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_active_time_by_equipment_id(self, equipment_id):
        if not equipment_id:
            raise ValueError("equipment_id cannot be null or empty")

        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT active_time 
                        FROM active_time 
                        WHERE equipment_id = %s 
                        ORDER BY id DESC LIMIT 1
                        """,
                        (equipment_id,),
                    )
                    row = cursor.fetchone()
                    return ActiveTime.from_dict(row) if row else None
        except Exception as e:
            logger.error(
                f"Failed to fetch active time for equipment_id {equipment_id}: {e}",
                exc_info=True,
            )
            raise DatabaseException(
                f"Error fetching active time for equipment_id {equipment_id}"
            )


    def insert_active_time(self, equipment_id, active_time):
        if not equipment_id or not active_time:
            raise ValueError("equipment_id and active_time cannot be null or empty")
        try:
             with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO active_time (equipment_id, active_time)
                        VALUES (%s,%s)
                        RETURNING id;
                        """,
                        (equipment_id, active_time),
                    )
                    active_time_id = cursor.fetchone()["id"]
                    conn.commit()
                    return active_time_id          

        except Exception as e:
            logger.error(
                f"Failed inserting active time for equipment_id {equipment_id}: {e}",
                exc_info=True,
            )
            raise DatabaseException(
                f"Error inserting active time for equipment_id {equipment_id}"
            )