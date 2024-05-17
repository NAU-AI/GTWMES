import paho.mqtt.client as mqtt
import time
import json
import datetime

def on_message(client, userdata, msg):
    print(f"Received message: topic={msg.topic}, payload={msg.payload.decode()}")
    messageInput = input("Enter your message: ")

    if messageInput == "exit":
        client.on_unsubscribe = on_unsubscribe
        print("bye!")
        exit()
    else: 
        message = json.dumps(
            {
                "message": messageInput,
                "date_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )

    topicSend = "MASILVA/CRK/PROTOCOL_COUNT_V0/GTW"
    message = json.dumps(
        {
            "message": messageInput,
            "date_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    )
    client.publish(topicSend, message)
    print(f"Message sent. Waiting for some response...")

def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    client.disconnect()

def subscribe_mqtt(client, topic):
    client.subscribe(topic)
    client.on_message = on_message
    while True:
        client.loop()
        time.sleep(1)
        