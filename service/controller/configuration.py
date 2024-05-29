import os
import sys

from service.message.message import sendResponseMessage
from service.model.configuration import deleteEquipmentOutput, getCountingEquipmentByCode, insertCountingEquipment, insertEquipmentOutput, updateCountingEquipment

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
        updated_counting_equipment_code = updateCountingEquipment(data, conn, cursor)
        #delete existing outputs in order to add the new ones
        deleteEquipmentOutput(updated_counting_equipment_code, conn, cursor)
        #now we have to insert the outputs at equipment_output
        insertEquipmentOutput(updated_counting_equipment_code, data, conn, cursor)
    
    sendResponseMessage(client, topicSend, data, "ConfigurationResponse", cursor)
    cursor.close()
    conn.close()
    print("createConfiguration function done")
    print("Connection to the PostgreSQL server was closed")