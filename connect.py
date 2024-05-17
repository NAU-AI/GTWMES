import paho.mqtt.client as mqtt
import ssl

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def connect_mqtt(client_id, broker_url, ca_cert, certfile, keyfile):
    client = mqtt.Client(client_id=client_id)
    client.tls_set(ca_certs=ca_cert,
                   certfile=certfile,
                   keyfile=keyfile)
    client.on_connect = on_connect
    client.connect(broker_url, 8883)
    return client