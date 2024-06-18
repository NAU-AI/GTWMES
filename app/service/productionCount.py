import os
import sys
import time

from service.message import sendProductionCount
from dao.activeTime import ActiveTimeDAO 
from dao.productionCount import getPOs


sys.path.append(os.path.join(os.path.dirname(__file__), '../database'))
import connectDB
from config import load_config

def productionCount(client, topicSend):
    config = load_config()
    conn = connectDB.connect(config)
    cursor = conn.cursor()
    start = time.time()            
    final_pos = getPOs(conn)

    active_time_dao = ActiveTimeDAO(conn)

    while True:
        end = time.time()
        length = end - start
        for po in final_pos:
            if(round(round(length) % po['p_timer_communication_cycle']) == 0 and round(length) != 0):
                already_exist_this_equipmentId_at_active_time = active_time_dao.getActiveTimeByEquipmentId(po['equipment_id'])
        
                if len(already_exist_this_equipmentId_at_active_time) != 0:
                    #if exists, set equipment active time
                    active_time_dao.setActiveTime(po['equipment_id'], int(already_exist_this_equipmentId_at_active_time['active_time']) + po['p_timer_communication_cycle'])
                else:
                    #if not, create active time for this equipment 
                    active_time_dao.insertActiveTime(po['equipment_id'], round(length))
                
                sendProductionCount(client, topicSend, po, cursor, conn)

        final_pos = getPOs(conn)
        
        time.sleep(1)