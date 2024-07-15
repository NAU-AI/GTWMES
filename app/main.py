import logging
import sys
import os
import time
from dotenv import load_dotenv
load_dotenv() 

from api.connect import connect_mqtt
from variables import broker_url, ca_cert, certfile, keyfile, FIRST_RECONNECT_DELAY, RECONNECT_RATE, MAX_RECONNECT_DELAY
broker_url = broker_url
ca_cert = ca_cert
certfile = certfile
keyfile = keyfile

import api.publishSubscriberMES

def main():
    #MQTT client initialization
    reconnect_count, reconnect_delay = 0, int(FIRST_RECONNECT_DELAY)

    while True:
        logging.info("Connecting in %d seconds...", reconnect_delay)
        time.sleep(int(reconnect_delay))

        try:
            client = connect_mqtt(broker_url, ca_cert, certfile, keyfile)
            api.publishSubscriberMES.subscribe(client)
            return
        except Exception as err:
            logging.error("%s. Connection failed. Retrying...", err)

        reconnect_delay *= int(RECONNECT_RATE)
        reconnect_delay = min(reconnect_delay, int(MAX_RECONNECT_DELAY))
        

if __name__ == '__main__':
    main()