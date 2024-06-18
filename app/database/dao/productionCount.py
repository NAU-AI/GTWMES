import json
from database.dao.configuration import ConfigurationDAO  
from database.dao.productionOrder import ProductionOrderDAO 


def getPOs(conn):
    configuration_dao = ConfigurationDAO(conn)
    production_order_dao = ProductionOrderDAO(conn)

    counting_equipment = configuration_dao.getCountingEquipmentAll()

    pos = []
    for ce in counting_equipment:
        pos = pos + production_order_dao.getProductionOrderByCEquipmentId(ce['id'])
        
    final_pos = []
    for po in pos:
        for ce in counting_equipment:
            if ce['id'] == po['equipment_id']:
                temp_list = json.dumps(po, indent = 4)
                temp_list = json.loads(temp_list)
                temp_list.update({"p_timer_communication_cycle": ce['p_timer_communication_cycle']})
                temp_list.update({"equipment_status": ce['equipment_status']})
                temp_list.update({"equipment_code": ce['code']})
                final_pos.append(temp_list)
    return final_pos

