import json
import os
import sys
import time

from database.dao.counterRecord import CounterRecordDAO
from service.message import MessageService
from database.dao.activeTime import ActiveTimeDAO 
from database.dao.configuration import ConfigurationDAO
from database.dao.alarm import AlarmDAO
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
    production_order_dao = ProductionOrderDAO(conn)
    counter_record_dao = CounterRecordDAO(conn)
    alarm_dao = AlarmDAO(conn)

    while True:
        end = time.time()
        length = end - start
        equipments = configuration_dao.getCountingEquipmentAll()
        for equipment in equipments:
            if(round(round(length) % equipment['p_timer_communication_cycle']) == 0 and round(length) != 0):
                existPO = production_order_dao.getProductionOrderByCEquipmentIdIfNotFinished(equipment['id'])
                if not existPO:
                    temp_list = json.dumps({}, indent = 4)
                    temp_list = json.loads(temp_list)
                    temp_list.update({"code": ""})
                    temp_list.update({"equipment_code": equipment['code']})
                    temp_list.update({"equipment_id": equipment['id']})
                    temp_list.update({"equipment_status": equipment['equipment_status']})
                    
                    message_service = MessageService(configuration_dao, active_time_dao, counter_record_dao, alarm_dao)
                    message_service.sendProductionCount(client, topicSend, temp_list)
                else:
                    active_time_dao.insertActiveTime(equipment['id'], equipment['p_timer_communication_cycle'])
                    temp_list = json.dumps(existPO, indent = 4)
                    temp_list = json.loads(temp_list)
                    temp_list.update({"p_timer_communication_cycle": equipment['p_timer_communication_cycle']})
                    temp_list.update({"equipment_code": equipment['code']})
                    temp_list.update({"equipment_id": equipment['id']})
                    temp_list.update({"equipment_status": equipment['equipment_status']})
                    
                    message_service = MessageService(configuration_dao, active_time_dao, counter_record_dao, alarm_dao)
                    message_service.sendProductionCount(client, topicSend, temp_list)
                    
        time.sleep(1)