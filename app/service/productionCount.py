import json
import os
import sys
import time

from database.dao.counterRecord import CounterRecordDAO
from service.message import MessageService
from database.dao.activeTime import ActiveTimeDAO 
from database.dao.configuration import ConfigurationDAO
from database.dao.productionCount import ProductionCountDAO
from database.dao.productionOrder import ProductionOrderDAO

import database.connectDB
from database.config import load_config

def productionCount(client, topicSend):
    config = load_config()
    conn = database.connectDB.connect(config)
    start = time.time()            
    

    configuration_dao = ConfigurationDAO(conn)
    active_time_dao = ActiveTimeDAO(conn)
    production_count_dao = ProductionCountDAO(conn)
    production_order_dao = ProductionOrderDAO(conn)
    counter_record_dao = CounterRecordDAO(conn)

    equipments = configuration_dao.getCountingEquipmentAll()
    final_pos = production_count_dao.getPOs()

    while True:
        end = time.time()
        length = end - start
        for po in final_pos:
            if(round(round(length) % po['p_timer_communication_cycle']) == 0 and round(length) != 0 and po['finished'] != 1):
                #if not, create active time for this equipment 
                active_time_dao.insertActiveTime(po['equipment_id'], po['p_timer_communication_cycle'])
                
                message_service = MessageService(configuration_dao, active_time_dao, counter_record_dao)
                message_service.sendProductionCount(client, topicSend, po)

        for equipment in equipments:
            if equipment['equipment_status'] == 1:
                existPO = production_order_dao.getProductionOrderByCEquipmentIdIfNotFinished(equipment['id'])
                if not existPO:
                    final_pos = []

                    temp_list = json.dumps({}, indent = 4)
                    temp_list = json.loads(temp_list)
                    temp_list.update({"code": ""})
                    temp_list.update({"equipment_code": equipment['code']})
                    temp_list.update({"equipment_id": equipment['id']})
                    temp_list.update({"equipment_status": equipment['equipment_status']})
                    
                    message_service = MessageService(configuration_dao, active_time_dao, counter_record_dao)
                    message_service.sendProductionCount(client, topicSend, temp_list)


        final_pos = production_count_dao.getPOs()
        
        time.sleep(1)