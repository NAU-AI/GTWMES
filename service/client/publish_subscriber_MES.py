import json
import logging
import os
import sys
import time
import paho.mqtt.client as mqtt
import threading
import json
from dotenv import load_dotenv

from service.configuration.configuration import createConfiguration
load_dotenv() 

#this file is for MESCLOUD - this client is different from publish_subscriber_GTW.py file
#client_id = "iotconsole-d0d0f57f-f94b-4c46-95d5-a84bb43660cc"
topicSend = "MASILVA/CRK/PROTOCOL_COUNT_V0/GTW"
topicReceive = "MASILVA/CRK/PROTOCOL_COUNT_V0/BE"

def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("Error when connecting: "+str(rc))
        sys.exit(0)
        
        
def on_disconnect(client, userdata, rc): #it is used when internet connection is bad and it auto disconnects
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, os.getenv("FIRST_RECONNECT_DELAY")
    while reconnect_count < os.getenv("MAX_RECONNECT_COUNT"):
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= os.getenv("RECONNECT_RATE")
        reconnect_delay = min(reconnect_delay, os.getenv("MAX_RECONNECT_DELAY"))
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

def on_message(client, userdata, msg):
    message = json.loads(msg.payload)
    match message["jsonType"]:
        case "Configuration":
            createConfiguration(client, topicSend, message)

        case "Python":
            print("You can become a Data Scientist")

        case "PHP":
            print("You can become a backend developer")
    
        case "Solidity":
            print("You can become a Blockchain developer")

        case "Java":
            print("You can become a mobile app developer")
        case _:
            print("The language doesn't matter, what matters is solving problems.")


def subscribe(client):
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.subscribe(topicReceive)     
    while True:
        client.loop_start()
        time.sleep(1) 
   

#def console_input(client):
#    while True:
#        messageInput = input("Enter your message: ")
#        if messageInput.lower() == 'exit':
#            client.disconnect()
#            sys.exit(0)
#        else:
#            message = messageInput
#            print("Message sent:" + json.dumps(message))
#            client.publish(topicSend, json.dumps(message))

