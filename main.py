import logging
import sys
import os
import time
from dotenv import load_dotenv
load_dotenv() 

from service.client.connect.connect import connect_mqtt
broker_url = os.getenv("broker_url")
ca_cert = "./key/MES/AmazonRootCA1.pem"
certfile = "./key/MES/323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-certificate.pem.crt"
keyfile = "./key/MES/323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-private.pem.key"

sys.path.append(os.path.join(os.path.dirname(__file__), 'service/client'))
import publish_subscriber_MES

def main():

    #MQTT client initialization
    #client = connect_mqtt(broker_url, ca_cert, certfile, keyfile)
    #publish_subscriber_MES.subscribe(client)

    reconnect_count, reconnect_delay = 0, int(os.getenv("FIRST_RECONNECT_DELAY"))

    while True:
        logging.info("Connecting in %d seconds...", reconnect_delay)
        time.sleep(int(reconnect_delay))

        try:
            client = connect_mqtt(broker_url, ca_cert, certfile, keyfile)
            publish_subscriber_MES.subscribe(client)
            return
        except Exception as err:
            logging.error("%s. Connection failed. Retrying...", err)

        reconnect_delay *= int(os.getenv("RECONNECT_RATE"))
        reconnect_delay = min(reconnect_delay, int(os.getenv("MAX_RECONNECT_DELAY")))
        
    
    

if __name__ == '__main__':
    main()