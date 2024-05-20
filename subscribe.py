import paho.mqtt.client as mqtt
import time
import json
import datetime

from connect import connect_mqtt

client_id = "iotconsole-d0d0f57f-f94b-4c46-95d5-a84bb43660cc"
broker_url = "a3sdserc3gohpq-ats.iot.eu-central-1.amazonaws.com"
ca_cert = "AmazonRootCA1.pem"
certfile = "323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-certificate.pem.crt"
keyfile = "323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-private.pem.key"
topicReceive = "MASILVA/CRK/PROTOCOL_COUNT_V0/BE"

def on_message(client, userdata, msg):
    print(f"Received message: topic={msg.topic}, payload={msg.payload.decode()}")

def subscribe_mqtt(client, topic):
    client.subscribe(topic)
    client.on_message = on_message
    while True:
        client.loop_forever()
        time.sleep(1)

client = connect_mqtt(client_id, broker_url, ca_cert, certfile, keyfile)
subscribe_mqtt(client, topicReceive)