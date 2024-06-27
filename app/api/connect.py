import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
load_dotenv() 

def connect_mqtt(broker_url, ca_cert, certfile, keyfile):
    #We need to use cliend_id in order to be able to receive messages that were sent when offline
    clientId = os.getenv("clientId")
    
    client = mqtt.Client(client_id=clientId, clean_session=False) #if you put the cliend_id inside the mqtt.Client(client_id=client_id) only the MQTT client test from AWS will catch the message
    client.tls_set(ca_certs=ca_cert,
                   certfile=certfile,
                   keyfile=keyfile)
    client.connect(broker_url, 8883)
    return client