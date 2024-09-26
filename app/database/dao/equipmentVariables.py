import datetime
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

class EquipmentVariablesDAO:
    def __init__(self, connection):
        self.connection = connection

    #inserir counter record
    def getEquipmentVariablesByEquipmentId(self, id):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                get_equipment_variables_query = sql.SQL("""
                SELECT * 
                FROM equipment_variable
                WHERE equipment_id = %s;
                """)
                
                cursor.execute(get_equipment_variables_query, (id, ))
                equipment_variables_found = cursor.fetchall()
                return equipment_variables_found
            
        except Exception as err:
            logging.error("%s. getEquipmentVariablesByEquipmentId failed", err)