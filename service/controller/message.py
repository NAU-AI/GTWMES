import json
from service.model.configuration import getCountingEquipmentByCode, getEquipmentOutputByEquipmentId

def sendResponseMessage(client, topicSend, data, jsonType, cursor):  
    equipment_found = getCountingEquipmentByCode(data, cursor)  
    outputs = getEquipmentOutputByEquipmentId(equipment_found[0][1], cursor)
    
    counters = []
    for output in outputs:
        counters.append({"outputCode": output[2], "value": 0})

    if "productionOrderCode" in data:
        productionOrderCode = data["productionOrderCode"]
    else:
        productionOrderCode = ""

    alarm = [
          "16#0000 0000 0000 0000",
          "16#0000 0000 0000 0000", 
          "16#0000 0000 0000 0000", 
          "16#0000 0000 0000 0000" 
    ]

    message = {
    "jsonType": jsonType,
    "equipmentCode": equipment_found[0][1], 
    "productionOrderCode": productionOrderCode,
    "equipmentStatus": equipment_found[0][2],
    "activeTime":0,
    "alarm": alarm,
    "counters": counters
    }
    client.publish(topicSend, json.dumps(message))
    print("Response message sent")



def sendProductionCount(client, topicSend, data, cursor): 
    outputs = getEquipmentOutputByEquipmentId(data[5], cursor)
    
    counters = []
    for output in outputs:
        counters.append({"outputCode": output[2], "value": 0})

    alarm = [
          "16#0000 0000 0000 0000",
          "16#0000 0000 0000 0000", 
          "16#0000 0000 0000 0000", 
          "16#0000 0000 0000 0000" 
    ]

    message = {
    "jsonType": "ProductionCount",
    "equipmentCode": data[5], 
    "productionOrderCode": data[2],
    "equipmentStatus": data[4],
    "activeTime":0,
    "alarm": alarm,
    "counters": counters
    }
    client.publish(topicSend, json.dumps(message))
    print("ProductionCount sent")