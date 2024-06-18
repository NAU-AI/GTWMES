import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

class ProductionOrderDAO:
    def __init__(self, connection):
        self.connection = connection

    def getProductionOrderByCodeAndCEquipmentId(self, equipment_id, data):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            check_if_PO_exists_query = sql.SQL("""
            SELECT *
            FROM production_order
            WHERE code = %s AND equipment_id = %s
            LIMIT 1
            """)
            cursor.execute(check_if_PO_exists_query, (data["productionOrderCode"], equipment_id))
            po_found = cursor.fetchone()
            return po_found

    def getProductionOrderByCEquipmentId(self, equipment_id):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            check_if_PO_exists_query = sql.SQL("""
            SELECT *
            FROM production_order
            WHERE equipment_id = %s
            """)
            cursor.execute(check_if_PO_exists_query, (equipment_id,))
            po_found = cursor.fetchall()
            return po_found

    def insertProductionOrder(self, equipment_id, data):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            productionOrderInit_query = """
            INSERT INTO production_order (equipment_id, code)
            VALUES (%s, %s)
            """
            cursor.execute(productionOrderInit_query, (equipment_id, data["productionOrderCode"]))
            self.connection.commit()
            print("Production order started with code: " + data["productionOrderCode"])

    def setEquipmentStatus(self, equipment_id, equipment_status):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            set_equipment_status_query = sql.SQL("""
            UPDATE counting_equipment
            SET equipment_status = %s
            WHERE id = %s
            RETURNING id, code, equipment_status, p_timer_communication_cycle
            """)
            cursor.execute(set_equipment_status_query, (equipment_status, equipment_id))
            updated_counting_equipment_id = cursor.fetchall()
            self.connection.commit()
            print("Updated counting_equipment with id: " + str(equipment_id))
            return updated_counting_equipment_id