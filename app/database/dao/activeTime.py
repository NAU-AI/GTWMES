import datetime
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


class ActiveTimeDAO:
    def __init__(self, connection):
        self.connection = connection

    def getActiveTimeByEquipmentId(self, equipment_id):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                get_active_time_by_equipmentId_query = sql.SQL("""
                SELECT *
                FROM active_time
                WHERE equipment_id = %s
                """)
                cursor.execute(get_active_time_by_equipmentId_query, (equipment_id,))
                at_found = cursor.fetchone()
                return at_found
            
        except Exception as err:
            logging.error("%s. getActiveTimeByEquipmentId failed.", err)

    def insertActiveTime(self, equipment_id, active_time):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                ct = datetime.datetime.now()

                insert_active_time_query = """
                INSERT INTO active_time (equipment_id, active_time, registered_at)
                VALUES (%s,%s,%s)
                """
                cursor.execute(insert_active_time_query, (equipment_id, active_time, ct))
                self.connection.commit()
                print("Active time inserted for equipment: " + str(equipment_id))

        except Exception as err:
            logging.error("%s. insertActiveTime failed", err)

    def setActiveTime(self, equipment_id, active_time):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                ct = datetime.datetime.now()

                set_equipment_active_time_query = sql.SQL("""
                UPDATE active_time
                SET active_time = %s, registered_at = %s
                WHERE equipment_id = %s
                RETURNING id, equipment_id, active_time, registered_at
                """)
                cursor.execute(set_equipment_active_time_query, (active_time, ct, equipment_id))
                updated_at_equipment_id = cursor.fetchone()
                self.connection.commit()
                print("Updated active_time with equipment_id: " + str(equipment_id))
                return updated_at_equipment_id
            
        except Exception as err:
            logging.error("%s. setActiveTime failed", err)