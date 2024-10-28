import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

class ProductionOrderDAO:
    def __init__(self, connection):
        self.connection = connection

    def getProductionOrderByCodeAndCEquipmentId(self, equipment_id, data):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                check_if_PO_exists_query = sql.SQL("""
                SELECT *
                FROM production_order
                WHERE code = %s AND equipment_id = %s AND finished = %s
                """)
                cursor.execute(check_if_PO_exists_query, (data["productionOrderCode"], equipment_id, 0))
                po_found = cursor.fetchone()
                return po_found
            
        except Exception as err:
            logging.error("%s. getProductionOrderByCodeAndCEquipmentId failed", err)

    def getProductionOrderByCEquipmentId(self, equipment_id):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                check_if_PO_exists_query = sql.SQL("""
                SELECT *
                FROM production_order
                WHERE equipment_id = %s
                """)
                cursor.execute(check_if_PO_exists_query, (equipment_id,))
                po_found = cursor.fetchall()
                return po_found
            
        except Exception as err:
            logging.error("%s. getProductionOrderByCEquipmentId failed", err)

    def getProductionOrderByCEquipmentIdIfNotFinished(self, equipment_id):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                check_if_PO_exists_query = sql.SQL("""
                SELECT *
                FROM production_order
                WHERE equipment_id = %s AND finished = %s
                ORDER BY id DESC
                """)
                cursor.execute(check_if_PO_exists_query, (equipment_id,0))
                po_found = cursor.fetchone()
                return po_found
            
        except Exception as err:
            logging.error("%s. getProductionOrderByCEquipmentId failed", err)

    def insertProductionOrder(self, equipment_id, data):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                productionOrderInit_query = """
                INSERT INTO production_order (equipment_id, code)
                VALUES (%s, %s)
                """
                cursor.execute(productionOrderInit_query, (equipment_id, data["productionOrderCode"]))
                self.connection.commit()
                print("Production order started with code: " + data["productionOrderCode"])

        except Exception as err:
            logging.error("%s. insertProductionOrder failed", err)

    def setEquipmentStatus(self, equipment_id, equipment_status):
        try:
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
            
        except Exception as err:
            logging.error("%s. setEquipmentStatus failed", err)
        
    def setPOFinished(self, equipment_id):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                set_po_finished_query = sql.SQL("""
                UPDATE production_order
                SET finished = %s
                WHERE equipment_id = %s
                """)
                cursor.execute(set_po_finished_query, (1, equipment_id))
                self.connection.commit()
                print("PO finished for equipment_id: " + str(equipment_id))
        
        except Exception as err:
            logging.error("%s. setPOFinished failed", err)

    def updatePOcode(self, equipment_id, code):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                update_po_code_query = sql.SQL("""
                UPDATE production_order
                SET code = %s
                WHERE equipment_id = %s AND finished = %s
                """)
                cursor.execute(update_po_code_query, (code, equipment_id, 0))
                self.connection.commit()
                print("PO edited for equipment_id: " + str(equipment_id))
        
        except Exception as err:
            logging.error("%s. setPOFinished failed", err)