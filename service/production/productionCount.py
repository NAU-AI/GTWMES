import json
import os
import sys
import psycopg2
from psycopg2 import sql
import time

from service.production.productionOrder import getProductionOrderByCEquipmentId
from service.configuration.configuration import getCountingEquipmentAll, getEquipmentOutputByEquipmentId

sys.path.append(os.path.join(os.path.dirname(__file__), '../../db'))
import connectDB
from config import load_config

def productionCount(client, topicSend):
    config = load_config()
    conn = connectDB.connect(config)
    cursor = conn.cursor()
    start = time.time()            
    final_pos = getPOs(cursor)


    while True:
        end = time.time()
        length = end - start

        for po in final_pos:
            if(round(length % po[3]) == 0 and round(length) != 0):
                sendProductionCount(client, topicSend, po, cursor)

        final_pos = getPOs(cursor)
        
        time.sleep(1)


def getPOs(cursor):
    counting_equipment = getCountingEquipmentAll(cursor)

    pos = []
    for ce in counting_equipment:
        pos = pos + getProductionOrderByCEquipmentId(ce[0], cursor)
        
    final_pos = []
    for po in pos:
        for ce in counting_equipment:
            if ce[0] == po[1]:
                temp_list = list(po)
                temp_list.append(ce[3])
                temp_list.append(ce[2])
                temp_list.append(ce[1])
                po = tuple(temp_list)
                final_pos.append(po)  
    return final_pos

def sendProductionCount(client, topicSend, data, cursor): 
    outputs = getEquipmentOutputByEquipmentId(data[5], cursor)
    
    counters = []
    for output in outputs:
        counters.append({"outputCode": output[2], "value": 0})

    message = {
    "jsonType": "ProductionCount",
    "equipmentCode": data[5], 
    "productionOrderCode": data[2],
    "equipmentStatus": data[4],
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
    print("ProductionCount sent")