import os
import sys

from service.message import sendResponseMessage
from dao.configuration import ConfigurationDAO  

sys.path.append(os.path.join(os.path.dirname(__file__), '../database'))
import connectDB
from config import load_config

def createConfiguration(client, topicSend, data):
    config = load_config()
    conn = connectDB.connect(config)
    cursor = conn.cursor()

    configuration_dao = ConfigurationDAO(conn)

    #check if exists some counting_equipment with this code
    equipment_found = configuration_dao.getCountingEquipmentByCode(data)

    if equipment_found != None:
        #if it doesn't exists, create a new one and the outputs
        inserted_counting_equipment_id = configuration_dao.insertCountingEquipment(data)
        #like this counting equipment didn't exist, we have to insert the outputs at equipment_output
        configuration_dao.insertEquipmentOutput(inserted_counting_equipment_id, data)

    else: 
        #if exists, we update it
        updated_counting_equipment_code = configuration_dao.updateCountingEquipment(data)
        #delete existing outputs in order to add the new ones
        configuration_dao.deleteEquipmentOutput(updated_counting_equipment_code)
        #now we have to insert the outputs at equipment_output
        configuration_dao.insertEquipmentOutput(updated_counting_equipment_code, data)
    
    sendResponseMessage(client, topicSend, data, "ConfigurationResponse", cursor, conn)
    cursor.close()
    conn.close()
    print("createConfiguration function done")
    print("Connection to the PostgreSQL server was closed")