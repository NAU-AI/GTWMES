import json

from service.model.configuration import getCountingEquipmentAll, getEquipmentOutputByEquipmentId
from service.model.productionOrder import getProductionOrderByCEquipmentId

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