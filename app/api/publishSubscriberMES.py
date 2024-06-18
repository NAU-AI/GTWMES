import json
import logging
import os
import sys
import time
import paho.mqtt.client as mqtt
import threading
import json
from dotenv import load_dotenv
load_dotenv() 

from service.productionOrder import productionOrderConclusion, productionOrderInit
from service.productionCount import productionCount
from service.configuration import createConfiguration
from service.received import messageReceived

topicReceive = "MASILVA/CRK/PROTOCOL_COUNT_V0/PLC"
topicSend = "MASILVA/CRK/PROTOCOL_COUNT_V0/BE"

def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("Error when connecting: "+str(rc))
        sys.exit(0)
        
        
def on_disconnect(client, userdata, rc): #it is used when internet connection is bad and it auto disconnects
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, int(os.getenv("FIRST_RECONNECT_DELAY"))

    while True:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(int(reconnect_delay))

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= int(os.getenv("RECONNECT_RATE"))
        reconnect_delay = min(reconnect_delay, int(os.getenv("MAX_RECONNECT_DELAY")))

def on_message(client, userdata, msg):
    message = json.loads(msg.payload)
    print(message)
    match message["jsonType"]:
        case "Configuration":
            createConfiguration(client, topicSend, message)

        case "ProductionOrder":
            productionOrderInit(client, topicSend, message)

        case "ProductionOrderConclusion":
            productionOrderConclusion(client, topicSend, message)
        
        case "Received":
            messageReceived(client, topicSend, message)
        
        case _:
            print("This code is not prepared to resolve this request.")


def subscribe(client):
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.subscribe(topicReceive, qos=1)   

    periodically_messages_thread = threading.Thread(target=productionCount, args=(client, topicSend ))
    periodically_messages_thread.daemon = True
    periodically_messages_thread.start()  
    
    try:
        while True:
            client.loop_start()
            time.sleep(1) 
    except KeyboardInterrupt:
        print("Ctrl+C pressed... Shutting down.")
    return 0

