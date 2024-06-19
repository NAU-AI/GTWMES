import os
import random
import sys
import time

from dao.counterRecord import CounterRecordDAO
from dao.configuration import ConfigurationDAO


sys.path.append(os.path.join(os.path.dirname(__file__), '../database'))
import connectDB
from config import load_config

def counterRecordsForThreadTests():
    config = load_config()
    conn = connectDB.connect(config)
          
    configuration_dao = ConfigurationDAO(conn)
    counter_record_dao = CounterRecordDAO(conn)




    while True:
        outputs = configuration_dao.getEquipmentOutput()
        
        for output in outputs:
            if output['code'] == "CRK001-001":
                counter_record_dao.insertCounterRecord(output["id"], random.randint(100, 1000))
            else:
                counter_record_dao.insertCounterRecord(output["id"], random.randint(1, 100))

        
        print("Counter records inserted")
        time.sleep(60)
