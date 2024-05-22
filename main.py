import sys
import os
from dotenv import load_dotenv
load_dotenv() 

from service.client.connect.connect import connect_mqtt
broker_url = os.getenv("broker_url")
ca_cert = "./key/MES/AmazonRootCA1.pem"
certfile = "./key/MES/323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-certificate.pem.crt"
keyfile = "./key/MES/323d7c3fe3ed141225b1846da88ba2b9d587165ab60ac6965ff316d4203f0140-private.pem.key"

#sys.path.append(os.path.join(os.path.dirname(__file__), 'db'))
#import connectDB
#from config import load_config

sys.path.append(os.path.join(os.path.dirname(__file__), 'service/client'))
import publish_subscriber_MES

def main():
    #database initialization
    #config = load_config()
    #conn = connectDB.connect(config)
    #cursor = conn.cursor()
    #print(cursor.execute("SELECT * FROM alarm"))

    #MQTT client initialization
    client = connect_mqtt(broker_url, ca_cert, certfile, keyfile)
    publish_subscriber_MES.subscribe(client)
    

if __name__ == '__main__':
    main()