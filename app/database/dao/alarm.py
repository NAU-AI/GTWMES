import datetime
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

class AlarmDAO:
    def __init__(self, connection):
        self.connection = connection

    def getAlarmsByEquipmentId(self, equipment_id):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                get_alarms_by_equipmentId_query = sql.SQL("""SELECT * FROM alarm WHERE equipment_id = %s ORDER BY id DESC limit 1""")
                cursor.execute(get_alarms_by_equipmentId_query, (equipment_id,))
                alarms_found = cursor.fetchone()
                return alarms_found
            
        except Exception as err:
            logging.error("%s. getAlarmsByEquipmentId failed.", err)

    def insertAlarm(self, equipment_id, alarms):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                ct = datetime.datetime.now()
                new_alarm_query = sql.SQL("""
                INSERT INTO alarm (equipment_id, alarm_1, alarm_2, alarm_3, alarm_4, registered_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """)
                cursor.execute(new_alarm_query, (equipment_id, alarms["alarm_1"], alarms["alarm_2"], alarms["alarm_3"], alarms["alarm_4"], ct))
                self.connection.commit()
            
        except Exception as err:
            logging.error("%s. insertAlarm failed.", err)

    def updateAlarmByEquipmentId(self, equipment_id, alarms):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                ct = datetime.datetime.now()
                edit_alarm_query = sql.SQL("""
                UPDATE alarm 
                set alarm_1 = %s, alarm_2 = %s, alarm_3 = %s, alarm_4 = %s, registered_at = %s
                WHERE equipment_id = %s
                """)
                cursor.execute(edit_alarm_query, (alarms["alarm_1"], alarms["alarm_2"], alarms["alarm_3"], alarms["alarm_4"], ct, equipment_id))
                self.connection.commit()
            
        except Exception as err:
            logging.error("%s. updateAlarmByEquipmentId failed.", err)