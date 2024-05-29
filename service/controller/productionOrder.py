import os
import sys

from service.message.message import sendResponseMessage
from service.model.configuration import getCountingEquipmentByCode
from service.model.productionOrder import getProductionOrderByCodeAndCEquipmentId, insertProductionOrder, setEquipmentStatus

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

        setEquipmentStatus(equipment_data[0][0], 0, conn, cursor)
   
    #send response
    sendResponseMessage(client, topicSend, data, "ProductionOrderResponse", cursor)
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
    setEquipmentStatus(equipment_data[0][0], 0, conn, cursor)
    #send response
    sendResponseMessage(client, topicSend, data, "ProductionOrderConclusionResponse" , cursor)
    cursor.close()
    conn.close()
    print("ProductionConclusion function done")
    print("Connection to the PostgreSQL server was closed")