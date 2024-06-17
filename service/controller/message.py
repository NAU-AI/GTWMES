import json
from random import randint
from service.model.activeTime import getActiveTimeByEquipmentId
from service.model.configuration import getCountingEquipmentByCode, getEquipmentOutputByEquipmentId

def sendResponseMessage(client, topicSend, data, jsonType, cursor): 
 
    equipment_found = getCountingEquipmentByCode(data, cursor)  
    outputs = getEquipmentOutputByEquipmentId(equipment_found[0][1], cursor)

    active_time_data = getActiveTimeByEquipmentId(equipment_found[0][1], cursor)
    
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
    "activeTime":active_time_data[0][2],
    "alarms": alarm,
    "counters": counters
    }
    client.publish(topicSend, json.dumps(message), qos=1)
    print("Response message sent")



def sendProductionCount(client, topicSend, data, cursor): 
    outputs = getEquipmentOutputByEquipmentId(data[5], cursor)

    active_time_data = getActiveTimeByEquipmentId(data[1], cursor)
    
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
    "activeTime":active_time_data[0][2],
    "alarms": alarm,
    "counters": counters
    }

    client.publish(topicSend, json.dumps(message), qos=1)
    print("ProductionCount sent")