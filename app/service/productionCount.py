import os
import sys
import time

from database.dao.counterRecord import CounterRecordDAO
from service.message import MessageService
from database.dao.activeTime import ActiveTimeDAO 
from database.dao.configuration import ConfigurationDAO
from database.dao.productionCount import ProductionCountDAO


sys.path.append(os.path.join(os.path.dirname(__file__), '../database'))
import database.connectDB
from database.config import load_config

def productionCount(client, topicSend):
    config = load_config()
    conn = database.connectDB.connect(config)
    start = time.time()            
    

    configuration_dao = ConfigurationDAO(conn)
    active_time_dao = ActiveTimeDAO(conn)
    production_count_dao = ProductionCountDAO(conn)
    counter_record_dao = CounterRecordDAO(conn)

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

        final_pos = production_count_dao.getPOs()
        
        time.sleep(1)