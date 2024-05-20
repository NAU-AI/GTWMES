import json
import sys
import paho.mqtt.client as mqtt
import threading
import json

from connect import connect_mqtt

#this file is for MESCLOUD - this client is different from publish_subscriber_GTW.py file
#client_id = "iotconsole-d0d0f57f-f94b-4c46-95d5-a84bb43660cc"
broker_url = "a3sdserc3gohpq-ats.iot.eu-central-1.amazonaws.com"
ca_cert = "MES_keys/AmazonRootCA1.pem"
certfile = "MES_keys/323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-certificate.pem.crt"
keyfile = "MES_keys/323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-private.pem.key"
topicSend = "MASILVA/CRK/PROTOCOL_COUNT_V0/GTW"
topicReceive = "MASILVA/CRK/PROTOCOL_COUNT_V0/BE"

file = open('messages_MESCLOUD.json')
dataFile = json.load(file)
allMessages = []

for i in dataFile["messages"]:
    if i["jsonType"]:
        allMessages.append(i)
    else:
        allMessages = {
            "jsonType": "Não tem mensagens"
        }

file.close()

def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("Error when connecting: "+str(rc))
        sys.exit(0)
    else:
        client.subscribe(topicReceive)

def on_message(client, userdata, msg):
    print("Message received: " + msg.topic + " " + str(msg.payload))

def subscribe(client):
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()

def console_input(client):
    while True:
        messageInput = input("Enter your message: ")
        if messageInput.lower() == 'exit':
            client.disconnect()
            sys.exit(0)
        else:
            for i in allMessages:
                if i["jsonType"] == messageInput:
                    message = i
                    print("Message sent:" + json.dumps(message))
                    client.publish(topicSend, json.dumps(message))
                    break

client = connect_mqtt(broker_url, ca_cert, certfile, keyfile)

subscribe_thread = threading.Thread(target=subscribe, args=(client,))
subscribe_thread.start()

publish_thread = threading.Thread(target=console_input, args=(client,))
publish_thread.start()