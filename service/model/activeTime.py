import datetime
import psycopg2
from psycopg2 import sql


def getActiveTimeByEquipmentId(equipment_id, cursor):
    get_active_time_by_equipmentId_query = sql.SQL("""
    SELECT *
    FROM active_time
    WHERE equipment_id = %s
    """)
    cursor.execute(get_active_time_by_equipmentId_query, (equipment_id,))
    at_found = cursor.fetchall()
    return at_found

def insertActiveTime(equipment_id, active_time, conn, cursor):
    ct = datetime.datetime.now()

    insert_active_time_query = """
    INSERT INTO active_time (equipment_id, active_time, registered_at)
    VALUES (%s,%s,%s)
    """
    cursor.execute(insert_active_time_query, (equipment_id, active_time, ct))
    conn.commit()
    print("Active time inserted for equipment: " + str(equipment_id))


def setActiveTime(equipment_id, active_time, conn, cursor):
    ct = datetime.datetime.now()

    set_equipment_active_time_query = sql.SQL("""
    UPDATE active_time
    SET active_time = %s, registered_at = %s
    WHERE equipment_id = %s
    RETURNING id, equipment_id, active_time, registered_at
    """)
    cursor.execute(set_equipment_active_time_query, (active_time, ct, equipment_id))
    updated_at_equipment_id = cursor.fetchall()
    conn.commit()
    print("Updated active_time with equipment_id: " + str(equipment_id))
    return updated_at_equipment_id