import json
import logging
from datetime import datetime
from exception.Exception import DatabaseException
from model.alarm import Alarm
from database.connection.db_connection import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlarmDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_alarm_by_equipment_id(self, equipment_id):
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT *
                        FROM alarm
                        WHERE equipment_id = %s 
                        ORDER BY id DESC LIMIT 1
                        """,
                        (equipment_id,),
                    )
                    row = cursor.fetchone()
                    return Alarm.from_dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching alarms for equipment_id {equipment_id}: {e}")
            raise DatabaseException("Failed to fetch alarms")

    def insert_alarm_by_equipment_id(self, equipment_id, alarms):
        try:
            registered_at = datetime.now()
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO alarm (equipment_id, alarm_0, alarm_1, alarm_2, alarm_3, registered_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id;
                        """,
                        (equipment_id, alarms[0], alarms[1], alarms[2], alarms[3], registered_at),
                    )
                    alarm_id = cursor.fetchone()["id"]
                    conn.commit()
                    return alarm_id
        except Exception as e:
            logger.error(f"Error inserting alarm for equipment_id {equipment_id}: {e}")
            raise DatabaseException("Failed to insert alarms")
            
        except Exception as err:
            logging.error("%s. insertAlarm failed.", err)

    def update_alarm_by_equipment_id(self, equipment_id, alarms):
        try:
            registered_at = datetime.now()
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE alarm
                        SET alarm_0 = %s, alarm_1 = %s, alarm_2 = %s, alarm_3 = %s, registered_at = %s
                        WHERE equipment_id = %s
                        RETURNING id;
                        """,
                        (alarms[0], alarms[1], alarms[2], alarms[3], registered_at, equipment_id),
                    )
                    alarm_id = cursor.fetchone()["id"]
                    conn.commit()
                    return alarm_id
        except Exception as e:
            logger.error(f"Error updating alarm for equipment_id {equipment_id}: {e}")
            raise DatabaseException("Failed to update alarms")