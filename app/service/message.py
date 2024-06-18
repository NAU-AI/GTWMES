import json
from random import randint

from database.dao.activeTime import ActiveTimeDAO
from database.dao.configuration import ConfigurationDAO


def sendResponseMessage(client, topicSend, data, jsonType, cursor, conn): 
    configuration_dao = ConfigurationDAO(conn)
    
    equipment_found = configuration_dao.getCountingEquipmentByCode(data)  
    outputs = configuration_dao.getEquipmentOutputByEquipmentId(equipment_found[0][1])

    active_time_dao = ActiveTimeDAO(conn)
    active_time_data = active_time_dao.getActiveTimeByEquipmentId(equipment_found[0][0])

    if(len(active_time_data)) != 0:
        time = active_time_data["active_time"]
    else:
        time = 0
        
    
    counters = []
    for output in outputs:
        #counters.append({"outputCode": output[2], "value": 0})
        counters.append({"outputCode": output[2], "value": randint(1, 100)})

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
    "equipmentCode": equipment_found[0][1], 
    "productionOrderCode": productionOrderCode,
    "equipmentStatus": equipment_found[0][2],
    "activeTime":time,
    "alarms": alarm,
    "counters": counters
    }
    client.publish(topicSend, json.dumps(message), qos=1)
    print("Response message sent")



def sendProductionCount(client, topicSend, data, cursor, conn): 
    configuration_dao = ConfigurationDAO(conn)
    
    outputs = configuration_dao.getEquipmentOutputByEquipmentId(data[5], cursor)

    active_time_dao = ActiveTimeDAO(conn)
    active_time_data = active_time_dao.getActiveTimeByEquipmentId(data[1])
    
    if(len(active_time_data)) != 0:
        time = active_time_data["active_time"]
    else:
        time = 0

    counters = []
    for output in outputs:
        #counters.append({"outputCode": output[2], "value": 0})
        counters.append({"outputCode": output[2], "value": randint(1, 100)})


    alarm = [
          0,
          0, 
          0, 
          0 
    ]

    message = {
    "jsonType": "ProductionCount",
    "equipmentCode": data[5], 
    "productionOrderCode": data[2],
    "equipmentStatus": data[4],
    "activeTime":time,
    "alarms": alarm,
    "counters": counters
    }

    client.publish(topicSend, json.dumps(message), qos=1)
    print("ProductionCount sent")