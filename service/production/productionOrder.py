import json
import os
import sys
import psycopg2
from psycopg2 import sql

from service.configuration.configuration import getCountingEquipmentByCode, getEquipmentOutputByEquipmentId


sys.path.append(os.path.join(os.path.dirname(__file__), '../../db'))
import connectDB
from config import load_config

def productionOrderInit(client, topicSend, data):
    config = load_config()
    conn = connectDB.connect(config)
    cursor = conn.cursor()

    #check if exists some counting_equipment with this code and get this id
    equipment_data = getCountingEquipmentByCode(data, cursor)

    already_exist_this_production_order = getProductionOrderByCodeAndCEquipmentId(equipment_data[0][0], data, cursor)
    
    if len(already_exist_this_production_order) == 0:
        #create new production order
        insertProductionOrder(equipment_data[0][0], data, conn, cursor)

        #setting equipment status using isEquipmentEnabled property from MQTT message
        if data["isEquipmentEnabled"]:
            equipment_status = 1
        else:
            equipment_status = 0

        updated_equipment_state = setEquipmentStatus(equipment_data[0][0], equipment_status, conn, cursor)
        #send response
        sendProductionOrderConclusionResponse(client, topicSend, data, updated_equipment_state, cursor)
    cursor.close()
    conn.close()
    print("ProductionInit function done")
    print("Connection to the PostgreSQL server was closed")

def productionOrderConclusion(client, topicSend, data):
    config = load_config()
    conn = connectDB.connect(config)
    cursor = conn.cursor()

    #check if exists some counting_equipment with this code and get this id
    equipment_data = getCountingEquipmentByCode(data, cursor)

    #setting equipment status using isEquipmentEnabled property from MQTT message
    updated_equipment_state = setEquipmentStatus(equipment_data[0][0], 0, conn, cursor)
    #send response
    sendProductionOrderInitResponse(client, topicSend, data, updated_equipment_state, cursor)
    cursor.close()
    conn.close()
    print("ProductionConclusion function done")
    print("Connection to the PostgreSQL server was closed")


def getProductionOrderByCodeAndCEquipmentId(equipment_id, data, cursor):
    print(equipment_id)
    print(data)
    check_if_PO_exists_query = sql.SQL("""
    SELECT *
    FROM production_order
    WHERE code = %s AND equipment_id = %s
    LIMIT 1
    """)
    cursor.execute(check_if_PO_exists_query, (data["productionOrderCode"], equipment_id))
    po_found = cursor.fetchall()
    return po_found

def insertProductionOrder(equipment_id, data, conn, cursor):
    productionOrderInit_query = """
    INSERT INTO production_order (equipment_id, code)
    VALUES (%s, %s)
    """
    cursor.execute(productionOrderInit_query, (equipment_id, data["productionOrderCode"]))
    conn.commit()
    print("Production order started with code: " + data["productionOrderCode"])

def setEquipmentStatus(equipment_id, equipment_status, conn, cursor):
    set_equipment_status_query = sql.SQL("""
    UPDATE counting_equipment
    SET equipment_status = %s
    WHERE id = %s
    RETURNING id, code, equipment_status, p_timer_communication_cycle
    """)
    cursor.execute(set_equipment_status_query, (equipment_status, equipment_id))
    updated_counting_equipment_id = cursor.fetchall()
    conn.commit()
    print("Updated counting_equipment with id: " + str(equipment_id))
    return updated_counting_equipment_id

def sendProductionOrderInitResponse(client, topicSend, data, equipment_data, cursor):   
    outputs = getEquipmentOutputByEquipmentId(equipment_data[0][0], cursor)
    
    counters = []
    for output in outputs:
        counters.append({"outputCode": output[2], "value": 0})

    message = {
    "jsonType": "ProductionOrderResponse",
    "equipmentCode": equipment_data[0][1], 
    "productionOrderCode": data["productionOrderCode"],
    "equipmentStatus": equipment_data[0][2],
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
    print("ProductionOrderInitResponse sent")

def sendProductionOrderConclusionResponse(client, topicSend, data, equipment_data, cursor):   
    outputs = getEquipmentOutputByEquipmentId(equipment_data[0][0], cursor)
    
    counters = []
    for output in outputs:
        counters.append({"outputCode": output[2], "value": 0})

    message = {
    "jsonType": "ProductionOrderConclusionResponse",
    "equipmentCode": equipment_data[0][1], 
    "productionOrderCode": data["productionOrderCode"],
    "equipmentStatus": equipment_data[0][2],
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
    print("ProductionOrderConclusionResponse sent")