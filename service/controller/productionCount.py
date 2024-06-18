import os
import sys
import time

from service.controller.message import sendProductionCount
from service.model.activeTime import getActiveTimeByEquipmentId, insertActiveTime, setActiveTime
from service.model.productionCount import getPOs

sys.path.append(os.path.join(os.path.dirname(__file__), '../../db'))
import connectDB
from config import load_config

def productionCount(client, topicSend):
    config = load_config()
    conn = connectDB.connect(config)
    cursor = conn.cursor()
    start = time.time()            
    final_pos = getPOs(cursor)


    while True:
        end = time.time()
        length = end - start

        for po in final_pos:
            if(round(round(length) % po[3]) == 0 and round(length) != 0):
                already_exist_this_equipmentId_at_active_time = getActiveTimeByEquipmentId(po[1], cursor)
                
                if len(already_exist_this_equipmentId_at_active_time) != 0:
                    #if exists, set equipment active time
                    setActiveTime(po[1], int(already_exist_this_equipmentId_at_active_time[0][2]) + po[3], conn, cursor)
                else:
                    #if not, create active time for this equipment 
                    insertActiveTime(po[1], round(length), conn, cursor)
                
                sendProductionCount(client, topicSend, po, cursor)

        final_pos = getPOs(cursor)
        
        time.sleep(1)