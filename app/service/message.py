import json
from random import randint

from database.dao.activeTime import ActiveTimeDAO
from database.dao.configuration import ConfigurationDAO


def sendResponseMessage(client, topicSend, data, jsonType, conn): 
    configuration_dao = ConfigurationDAO(conn)
    
    equipment_found = configuration_dao.getCountingEquipmentByCode(data)  

    outputs = configuration_dao.getEquipmentOutputByEquipmentId(equipment_found['code'])

    active_time_dao = ActiveTimeDAO(conn)
    active_time_data = active_time_dao.getActiveTimeByEquipmentId(equipment_found['id'])
    print(active_time_data)
    if active_time_data != None:
        time = active_time_data["active_time"]
    else:
        time = 0
        
    counters = []
    for output in outputs:
        #counters.append({"outputCode": output[2], "value": 0})
        counters.append({"outputCode": output['code'], "value": randint(1, 100)})

    if "productionOrderCode" in data:
        productionOrderCode = data["productionOrderCode"]
    else:
        productionOrderCode = ""

    alarm = [
          0,
          0, 
          0, 
          0 
    ]

    message = {
    "jsonType": jsonType,
    "equipmentCode": equipment_found['code'], 
    "productionOrderCode": productionOrderCode,
    "equipmentStatus": equipment_found['equipment_status'],
    "activeTime":time,
    "alarms": alarm,
    "counters": counters
    }
    client.publish(topicSend, json.dumps(message), qos=1)
    print("Response message sent")



def sendProductionCount(client, topicSend, data, cursor, conn): 
    configuration_dao = ConfigurationDAO(conn)
    active_time_dao = ActiveTimeDAO(conn)

    outputs = configuration_dao.getEquipmentOutputByEquipmentId(data['equipment_code'])
    active_time_data = active_time_dao.getActiveTimeByEquipmentId(data['equipment_id'])
    
    if active_time_data != None:
        time = active_time_data["active_time"]
    else:
        time = 0

    counters = []
    for output in outputs:
        #counters.append({"outputCode": output[2], "value": 0})
        counters.append({"outputCode": output['code'], "value": randint(1, 100)})


    alarm = [
          0,
          0, 
          0, 
          0 
    ]

    message = {
    "jsonType": "ProductionCount",
    "equipmentCode": data['equipment_code'], 
    "productionOrderCode": data['code'],
    "equipmentStatus": data['equipment_status'],
    "activeTime":time,
    "alarms": alarm,
    "counters": counters
    }

    client.publish(topicSend, json.dumps(message), qos=1)
    print("ProductionCount sent")