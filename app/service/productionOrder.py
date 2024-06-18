import os
import sys

from database.dao.activeTime import ActiveTimeDAO
from database.dao.configuration import ConfigurationDAO
from database.dao.productionOrder import ProductionOrderDAO  
from service.message import sendResponseMessage


sys.path.append(os.path.join(os.path.dirname(__file__), '../database'))
import connectDB
from config import load_config

def productionOrderInit(client, topicSend, data):
    config = load_config()
    conn = connectDB.connect(config)
    cursor = conn.cursor()

    configuration_dao = ConfigurationDAO(conn)
    production_order_dao = ProductionOrderDAO(conn)

    #check if exists some counting_equipment with this code and get this id
    equipment_data = configuration_dao.getCountingEquipmentByCode(data)

    already_exist_this_production_order = production_order_dao.getProductionOrderByCodeAndCEquipmentId(equipment_data['id'], data)

    active_time_dao = ActiveTimeDAO(conn)
    
    if len(already_exist_this_production_order) == 0:
        #create new production order
        production_order_dao.insertProductionOrder(equipment_data['id'], data)

        production_order_dao.setEquipmentStatus(equipment_data['id'], 0)

        already_exist_this_equipmentId_at_active_time = active_time_dao.getActiveTimeByEquipmentId(equipment_data['id'])

        if len(already_exist_this_equipmentId_at_active_time) != 0:
            #if exists, set equipment active time to zero
            active_time_dao.setActiveTime(equipment_data['id'], 0)
        else:
            #if not, create active time for this equipment 
            active_time_dao.insertActiveTime(equipment_data['id'], 0)
   
    #send response
    sendResponseMessage(client, topicSend, data, "ProductionOrderResponse", cursor, conn)
    cursor.close()
    conn.close()
    print("ProductionInit function done")
    print("Connection to the PostgreSQL server was closed")

def productionOrderConclusion(client, topicSend, data):
    config = load_config()
    conn = connectDB.connect(config)
    cursor = conn.cursor()

    configuration_dao = ConfigurationDAO(conn)
    production_order_dao = ProductionOrderDAO(conn)

    #check if exists some counting_equipment with this code and get this id
    equipment_data = configuration_dao.getCountingEquipmentByCode(data)

    #setting equipment status using isEquipmentEnabled property from MQTT message
    production_order_dao.setEquipmentStatus(equipment_data['id'], 0)

    #setting equipment active time to zero
    active_time_dao = ActiveTimeDAO(conn)
    active_time_dao.setActiveTime(equipment_data['id'], 0)

    #send response
    sendResponseMessage(client, topicSend, data, "ProductionOrderConclusionResponse" , cursor, conn)
    cursor.close()
    conn.close()
    print("ProductionConclusion function done")
    print("Connection to the PostgreSQL server was closed")