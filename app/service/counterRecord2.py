import os
import random
import sys
import time

from database.dao.counterRecord import CounterRecordDAO
from database.dao.configuration import ConfigurationDAO

import database.connectDB
from database.config import load_config

def counterRecordsForThreadTests():
    config = load_config()
    conn = database.connectDB.connect(config)
          
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
