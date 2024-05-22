import json
import os
import sys
import psycopg2
from psycopg2 import sql


sys.path.append(os.path.join(os.path.dirname(__file__), '../../db'))
import connectDB
from config import load_config

def createConfiguration(client, topicSend, data):
    config = load_config()
    conn = connectDB.connect(config)
    cursor = conn.cursor()

    #check if exists some counting_equipment with this code
    equipment_found = getCountingEquipmentByCode(data, cursor)

    if len(equipment_found) == 0:
        #if it doesn't exists, create a new one and the outputs
        inserted_counting_equipment_id = insertCountingEquipment(data, conn, cursor)
        #like this counting equipment didn't exist, we have to insert the outputs at equipment_output
        insertEquipmentOutput(inserted_counting_equipment_id, data, conn, cursor)

    else: 
        #if exists, we update it
        updated_counting_equipment_id = updateCountingEquipment(data, conn, cursor)
        #delete existing outputs in order to add the new ones
        deleteEquipmentOutput(updated_counting_equipment_id, conn, cursor)
        #now we have to insert the outputs at equipment_output
        insertEquipmentOutput(updated_counting_equipment_id, data, conn, cursor)
    
    sendConfigurationResponse(client, topicSend, data, cursor)
    cursor.close()
    conn.close()
    print("createConfiguration function done")
    print("Connection to the PostgreSQL server was closed")


def getCountingEquipmentByCode(data, cursor):
    check_if_counting_equipment_exists_query = sql.SQL("""
    SELECT *
    FROM counting_equipment
    WHERE code = %s
    LIMIT 1
    """)
    cursor.execute(check_if_counting_equipment_exists_query, (data["equipmentCode"],))
    equipment_found = cursor.fetchall()
    return equipment_found

def insertCountingEquipment(data, conn, cursor):
    new_counting_equipment_query = """
    INSERT INTO counting_equipment (code, equipment_status, p_timer_communication_cycle)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    cursor.execute(new_counting_equipment_query, (data["equipmentCode"], 0, data["pTimerCommunicationCycle"]))
    inserted_counting_equipment_id = cursor.fetchone()[0]
    conn.commit()
    print("Insert counting_equipment: " + data["equipmentCode"])
    return inserted_counting_equipment_id

def updateCountingEquipment(data, conn, cursor):
    update_counting_equipment_query = sql.SQL("""
    UPDATE counting_equipment
    SET equipment_status = %s,
    p_timer_communication_cycle = %s
    WHERE code = %s
    RETURNING id
    """)
    cursor.execute(update_counting_equipment_query, (0, data["pTimerCommunicationCycle"], data["equipmentCode"]))
    updated_counting_equipment_id = cursor.fetchone()[0]
    conn.commit()
    print("Updated counting_equipment: " + data["equipmentCode"])
    return updated_counting_equipment_id

def getEquipmentOutputByEquipmentId(data, cursor):
    get_equipment_output_query = sql.SQL("""
    SELECT *
    FROM equipment_output
    WHERE counting_equipment_id = %s
    """)
    cursor.execute(get_equipment_output_query, (data,))
    equipment_output_found = cursor.fetchall()
    return equipment_output_found

def insertEquipmentOutput(inserted_ce_id, data, conn, cursor):
    new_equipment_output_query = """
        INSERT INTO equipment_output (counting_equipment_id, code)
        VALUES (%s, %s);
        """
    for output in data["outputCodes"]:
        cursor.execute(new_equipment_output_query, (inserted_ce_id, output))
        conn.commit()
        print("Insert equipment_output: " + output)

def deleteEquipmentOutput(updated_ce_id, conn, cursor):
    delete_existing_outputs = sql.SQL("""
    DELETE
    FROM equipment_output
    WHERE counting_equipment_id = %s
    """)
    cursor.execute(delete_existing_outputs, (updated_ce_id,))
    conn.commit()

def sendConfigurationResponse(client, topicSend, data, cursor):
    equipment_found = getCountingEquipmentByCode(data, cursor)
    outputs = getEquipmentOutputByEquipmentId(equipment_found[0][0], cursor)

    counters = []
    for output in outputs:
        counters.append({"outputCode": output[2], "value": 0})

    message = {
    "jsonType": "ConfigurationResponse",
    "equipmentCode": equipment_found[0][1], 
    "productionOrderCode": "",
    "equipmentStatus": equipment_found[0][2],
    "activeTime":0,
    "alarm":
    [
          "16#0000 0000 0000 0000",
          "16#0000 0000 0000 0000", 
          "16#0000 0000 0000 0000", 
          "16#0000 0000 0000 0000" 
    ],
    "counters": counters
    }

    client.publish(topicSend, json.dumps(message))
    print("ConfigurationResponse sent")