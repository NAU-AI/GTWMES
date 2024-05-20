import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def connect_mqtt(broker_url, ca_cert, certfile, keyfile):
    client = mqtt.Client() #if you put the cliend_id inside the mqtt.Client(client_id=client_id) only the MQTT client test from AWS will catch the message
    client.tls_set(ca_certs=ca_cert,
                   certfile=certfile,
                   keyfile=keyfile)
    client.on_connect = on_connect
    client.connect(broker_url, 8883)
    return client