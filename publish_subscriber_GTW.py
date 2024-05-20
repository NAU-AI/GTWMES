import datetime
import json
import sys
import paho.mqtt.client as mqtt
import threading
import json

from connect import connect_mqtt

#this file is for GTW - this client is different from publish_subscriber_MES.py file
client_id = "iotconsole-d0d0f57f-f94b-4c46-95d5-a84bb43660cc"
broker_url = "a3sdserc3gohpq-ats.iot.eu-central-1.amazonaws.com"
ca_cert = "GTW_keys/AmazonRootCA1.pem"
certfile = "GTW_keys/24cfb3755ce31e148199605aa4a12317d478532294c3d68ffe9270f39c4e51e5-certificate.pem.crt"
keyfile = "GTW_keys/24cfb3755ce31e148199605aa4a12317d478532294c3d68ffe9270f39c4e51e5-private.pem.key"
topicSend = "MASILVA/CRK/PROTOCOL_COUNT_V0/BE"
topicReceive = "MASILVA/CRK/PROTOCOL_COUNT_V0/GTW"

file = open('messages_GTW.json')
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

client = connect_mqtt(client_id, broker_url, ca_cert, certfile, keyfile)

subscribe_thread = threading.Thread(target=subscribe, args=(client,))
subscribe_thread.start()

publish_thread = threading.Thread(target=console_input, args=(client,))
publish_thread.start()