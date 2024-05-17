import paho.mqtt.client as mqtt
import json
import datetime

from connect import connect_mqtt
from subscribe import subscribe_mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def publish_mqtt(client, topic, message):
    client.publish(topic=topic, payload=message)

def main():
    client_id = "iotconsole-d0d0f57f-f94b-4c46-95d5-a84bb43660cc"
    broker_url = "a3sdserc3gohpq-ats.iot.eu-central-1.amazonaws.com"
    ca_cert = "AmazonRootCA1.pem"
    certfile = "323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-certificate.pem.crt"
    keyfile = "323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-private.pem.key"
    topicReceive = "MASILVA/CRK/PROTOCOL_COUNT_V0/BE"
    topicSend = "MASILVA/CRK/PROTOCOL_COUNT_V0/GTW"


    messageInput = input("Enter your message: ")

    if messageInput == "exit":
        print("bye!")
        exit()
    else: 
        message = json.dumps(
            {
                "message": messageInput,
                "date_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )

    client = connect_mqtt(client_id, broker_url, ca_cert, certfile, keyfile)
    client.on_connect = on_connect
    client.connect(broker_url, 8883)
    client.publish(topicSend, message)
    subscribe_mqtt(client, topicReceive)

if __name__ == "__main__":
    main()