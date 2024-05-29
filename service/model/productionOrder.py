import json
import psycopg2
from psycopg2 import sql

from service.model.configuration import getEquipmentOutputByEquipmentId

def getProductionOrderByCodeAndCEquipmentId(equipment_id, data, cursor):
    check_if_PO_exists_query = sql.SQL("""
    SELECT *
    FROM production_order
    WHERE code = %s AND equipment_id = %s
    LIMIT 1
    """)
    cursor.execute(check_if_PO_exists_query, (data["productionOrderCode"], equipment_id))
    po_found = cursor.fetchall()
    return po_found

def getProductionOrderByCEquipmentId(equipment_id, cursor):
    check_if_PO_exists_query = sql.SQL("""
    SELECT *
    FROM production_order
    WHERE equipment_id = %s
    """)
    cursor.execute(check_if_PO_exists_query, (equipment_id,))
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
    outputs = getEquipmentOutputByEquipmentId(equipment_data[0][1], cursor)
    
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
    outputs = getEquipmentOutputByEquipmentId(equipment_data[0][1], cursor)
    
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