import os
import sys
import time

from service.controller.message import sendProductionCount
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
            if(round(length % po[3]) == 0 and round(length) != 0):
                sendProductionCount(client, topicSend, po, cursor)

        final_pos = getPOs(cursor)
        
        time.sleep(1)