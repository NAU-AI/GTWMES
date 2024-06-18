from service.model.configuration import getCountingEquipmentAll
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

