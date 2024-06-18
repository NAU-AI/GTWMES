import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

class ConfigurationDAO:
    def __init__(self, connection):
        self.connection = connection

    def getCountingEquipmentByCode(self, data):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            check_if_counting_equipment_exists_query = sql.SQL("""
            SELECT *
            FROM counting_equipment
            WHERE code = %s
            LIMIT 1
            """)
            cursor.execute(check_if_counting_equipment_exists_query, (data["equipmentCode"],))
            equipment_found = cursor.fetchone()
            return equipment_found

    def getCountingEquipmentAll(self):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            get_all_counting_equipment_query = sql.SQL("""
            SELECT *
            FROM counting_equipment
            """)
            cursor.execute(get_all_counting_equipment_query)
            equipment_found = cursor.fetchall()
            return equipment_found

    def insertCountingEquipment(self, data):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            new_counting_equipment_query = """
            INSERT INTO counting_equipment (code, equipment_status, p_timer_communication_cycle)
            VALUES (%s, %s, %s)
            RETURNING id;
            """
            cursor.execute(new_counting_equipment_query, (data["equipmentCode"], 0, data["pTimerCommunicationCycle"]))
            inserted_counting_equipment_id = cursor.fetchone()[0]
            self.connection.commit()
            print("Insert counting_equipment: " + data["equipmentCode"])
            return inserted_counting_equipment_id

    def updateCountingEquipment(self, data):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            update_counting_equipment_query = sql.SQL("""
            UPDATE counting_equipment
            SET equipment_status = %s,
            p_timer_communication_cycle = %s
            WHERE code = %s
            RETURNING code
            """)
            cursor.execute(update_counting_equipment_query, (0, data["pTimerCommunicationCycle"], data["equipmentCode"]))
            updated_counting_equipment_id = cursor.fetchone()[0]
            self.connection.commit()
            print("Updated counting_equipment: " + data["equipmentCode"])
            return updated_counting_equipment_id

    def getEquipmentOutputByEquipmentId(self, data):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            get_equipment_output_query = sql.SQL("""
            SELECT *
            FROM equipment_output
            WHERE equipment_code = %s
            """)
            cursor.execute(get_equipment_output_query, (data,))
            equipment_output_found = cursor.fetchall()
            return equipment_output_found

    def insertEquipmentOutput(self, inserted_ce_code, data):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            new_equipment_output_query = """
                INSERT INTO equipment_output (equipment_code, code)
                VALUES (%s, %s);
                """
            for output in data["outputCodes"]:
                cursor.execute(new_equipment_output_query, (inserted_ce_code, output))
                self.connection.commit()
                print("Insert equipment_output: " + output)

    def deleteEquipmentOutput(self, updated_ce_code):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            delete_existing_outputs = sql.SQL("""
            DELETE
            FROM equipment_output
            WHERE equipment_code = %s
            """)
            cursor.execute(delete_existing_outputs, (updated_ce_code,))
            self.connection.commit()

