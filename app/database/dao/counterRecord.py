import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

class CounterRecordDAO:
    def __init__(self, connection):
        self.connection = connection

    #inserir counter record
    def insertCounterRecord(self, id, value):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            ct = datetime.datetime.now()

            new_counter_record_query = """
            INSERT INTO counter_record (equipment_output_id, real_value, registered_at)
            VALUES (%s, %s, %s)
            """
            cursor.execute(new_counter_record_query, (id, value, ct))
            self.connection.commit()
            print("Insert counting_equipment")
        
    #get counter record por equipment_output_id
    def getCounterRecordTotalValueByEquipmentOutputId(self, data):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            check_counter_record_total_value_query = sql.SQL("""
            SELECT equipment_output_id, SUM(real_value) as totalValue
            FROM counter_record
            WHERE equipment_output_id = %s AND disable = %s
            GROUP BY equipment_output_id
            """)
            cursor.execute(check_counter_record_total_value_query, (data, 0))
            equipment_found = cursor.fetchone()
            return equipment_found

    def getCounterRecordTotalValueByEquipmentOutput(self):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            check_counter_record_total_value_query = sql.SQL("""
            SELECT equipment_output_id, SUM(real_value) as totalValue
            FROM counter_record
            GROUP BY equipment_output_id
            """)
            cursor.execute(check_counter_record_total_value_query)
            equipment_found = cursor.fetchall()
            return equipment_found