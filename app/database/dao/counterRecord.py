import datetime
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

class CounterRecordDAO:
    def __init__(self, connection):
        self.connection = connection

    #inserir counter record
    def insertCounterRecord(self, id, value):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                ct = datetime.datetime.now()

                new_counter_record_query = """
                INSERT INTO counter_record (equipment_output_id, real_value, registered_at)
                VALUES (%s, %s, %s)
                """
                cursor.execute(new_counter_record_query, (id, value, ct))
                self.connection.commit()
                print("Insert counting_equipment")

        except Exception as err:
            logging.error("%s. insertCounterRecord failed", err)
        
    #get counter record by equipment_output_id
    def getCounterRecordTotalValueByEquipmentOutputId(self, data):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                check_counter_record_total_value_query = sql.SQL("""
                SELECT cr.equipment_output_id, SUM(cr.real_value) AS totalValue
                FROM counter_record cr
                JOIN equipment_output eo ON cr.equipment_output_id = eo.id
                WHERE cr.equipment_output_id = %s AND eo.disable = %s
                GROUP BY cr.equipment_output_id
                """)
                
                cursor.execute(check_counter_record_total_value_query, (data, 0))
                equipment_found = cursor.fetchone()
                return equipment_found
            
        except Exception as err:
            logging.error("%s. getCounterRecordTotalValueByEquipmentOutputId failed", err)

    #get last counter record by equipment_output_id
    def getLastCounterRecordByEquipmentOutputId(self, equipment_output_id):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                check_counter_record_total_value_query = sql.SQL("""
                SELECT *
                FROM counter_record 
                WHERE equipment_output_id = %s
                ORDER BY registered_at DESC
                """)
                
                cursor.execute(check_counter_record_total_value_query, (equipment_output_id,))
                equipment_found = cursor.fetchone()
                return equipment_found
            
        except Exception as err:
            logging.error("%s. getCounterRecordTotalValueByEquipmentOutputId failed", err)

    def getCounterRecordTotalValueByEquipmentOutput(self):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                check_counter_record_total_value_query = sql.SQL("""
                SELECT equipment_output_id, SUM(real_value) as totalValue
                FROM counter_record
                GROUP BY equipment_output_id
                """)
                cursor.execute(check_counter_record_total_value_query)
                equipment_found = cursor.fetchall()
                return equipment_found
            
        except Exception as err:
            logging.error("%s. getCounterRecordTotalValueByEquipmentOutput failed", err)