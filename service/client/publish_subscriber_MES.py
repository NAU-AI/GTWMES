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

from connect.connect import connect_mqtt 

#this file is for MESCLOUD - this client is different from publish_subscriber_GTW.py file
#client_id = "iotconsole-d0d0f57f-f94b-4c46-95d5-a84bb43660cc"
broker_url = os.getenv("broker_url")
ca_cert = "../../key/MES/AmazonRootCA1.pem"
certfile = "../../key/MES/323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-certificate.pem.crt"
keyfile = "../../key/MES/323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-private.pem.key"
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
    print("Message received: " + msg.topic + " " + str(msg.payload))

def subscribe(client):
    client.on_connect = on_connect
    client.on_message = on_message
    client.subscribe(topicReceive)

def console_input(client):
    while True:
        messageInput = input("Enter your message: ")
        if messageInput.lower() == 'exit':
            client.disconnect()
            sys.exit(0)
        else:
            message = messageInput
            print("Message sent:" + json.dumps(message))
            client.publish(topicSend, json.dumps(message))
            break

client = connect_mqtt(broker_url, ca_cert, certfile, keyfile)
client.on_disconnect = on_disconnect

subscribe_thread = threading.Thread(target=subscribe, args=(client,))
subscribe_thread.start()

publish_thread = threading.Thread(target=console_input, args=(client,))
publish_thread.start()

client.loop_start()