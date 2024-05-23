import json

def messageReceived(client, topicSend, data):
    print("Message received: " + json.dumps(data))
    print("Receive message function done")