import os
from random import randint
import sys
import time

from dao.counterRecord import CounterRecordDAO
from dao.configuration import ConfigurationDAO


sys.path.append(os.path.join(os.path.dirname(__file__), '../database'))
import connectDB
from config import load_config

def counterRecordsForThreadTests(client, topicSend):
    config = load_config()
    conn = connectDB.connect(config)
          
    configuration_dao = ConfigurationDAO(conn)
    counter_record_dao = CounterRecordDAO(conn)




    while True:
        outputs = configuration_dao.getEquipmentOutput()
        allOutputsWithValue = counter_record_dao.getCounterRecordTotalValueByEquipmentOutput()

        for output in outputs:
            for outWithValue in allOutputsWithValue:
                if outWithValue["equipment_output_id"] == output["id"]:
                    print(outWithValue["totalvalue"])
                    outputTotal = outWithValue["totalvalue"]
                    counter_record_dao.insertCounterRecord(output["id"], outputTotal + randint(1, 100))
        
        print("Counter records inserted")
        time.sleep(60)
