import json
from database.dao.configuration import ConfigurationDAO  
from database.dao.productionOrder import ProductionOrderDAO 

class ProductionCountDAO:
    def __init__(self, connection):
        self.connection = connection

    def getPOs(self):
        configuration_dao = ConfigurationDAO(self.connection)
        production_order_dao = ProductionOrderDAO(self.connection)

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

