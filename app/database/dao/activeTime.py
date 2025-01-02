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

    def getLastActiveTimeByEquipmentId(self, equipment_id):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                get_last_active_time_by_equipmentId_query = sql.SQL("""
                SELECT *
                FROM active_time
                WHERE equipment_id = %s
                ORDER BY registered_at DESC
                """)
                cursor.execute(get_last_active_time_by_equipmentId_query, (equipment_id,))
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

    #get active_time by equipment_id
    def getActiveTimeTotalValueByEquipmentId(self, data):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                check_active_time_total_value_query = sql.SQL("""
                SELECT at.equipment_id, SUM(at.active_time) AS totalActiveValue
                FROM active_time at
                JOIN counting_equipment ce ON at.equipment_id = ce.id
                WHERE ce.id = %s
                GROUP BY at.equipment_id
                """)
                
                cursor.execute(check_active_time_total_value_query, (data, ))
                equipment_found = cursor.fetchone()
                return equipment_found
            
        except Exception as err:
            logging.error("%s. getCounterRecordTotalValueByEquipmentOutputId failed", err)