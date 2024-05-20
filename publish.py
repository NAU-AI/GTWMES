import time
import paho.mqtt.client as mqtt
import json
import datetime

from connect import connect_mqtt

client_id = "iotconsole-d0d0f57f-f94b-4c46-95d5-a84bb43660cc"
broker_url = "a3sdserc3gohpq-ats.iot.eu-central-1.amazonaws.com"
ca_cert = "AmazonRootCA1.pem"
certfile = "323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-certificate.pem.crt"
keyfile = "323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-private.pem.key"
topicSend = "MASILVA/CRK/PROTOCOL_COUNT_V0/GTW"

client = connect_mqtt(client_id, broker_url, ca_cert, certfile, keyfile)

def send_message_mqtt(topicSend, message):
    messageInput = input("Enter your message: ")
    if messageInput == "exit":
        print("bye!")
        client.disconnect()
        exit()
    else: 
        message = json.dumps(
            {
                "message": messageInput,
                "date_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        client.publish(topicSend, message)
    

def publish_mqtt(client, topicSend):
    while True:
        send_message_mqtt(topicSend, client)

publish_mqtt(client, topicSend)