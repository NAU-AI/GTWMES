import os
import boto3
import json
from dotenv import load_dotenv 
load_dotenv() 

thingArn = ''
thingId = ''
thingName = os.getenv("CLIENT_ID").strip()
defaultPolicyName = 'ALL2' #I can create policies with python too, if needed. But I think that all devices will have the same permissions.

def createThing():
    global thingClient
    thingResponse = thingClient.create_thing(
        thingName = thingName
    )
    data = json.loads(json.dumps(thingResponse, sort_keys=False, indent=4))
    for element in data: 
        if element == 'thingArn':
            thingArn = data['thingArn']
        elif element == 'thingId':
            thingId = data['thingId']
    createCertificate()

def createCertificate():
	global thingClient
	certResponse = thingClient.create_keys_and_certificate(
			setAsActive = True
	)
	data = json.loads(json.dumps(certResponse, sort_keys=False, indent=4))
	for element in data: 
			if element == 'certificateArn':
					certificateArn = data['certificateArn']
			elif element == 'keyPair':
					PublicKey = data['keyPair']['PublicKey']
					PrivateKey = data['keyPair']['PrivateKey']
			elif element == 'certificatePem':
					certificatePem = data['certificatePem']
			elif element == 'certificateId':
					certificateId = data['certificateId']

	with open('public.key', 'w') as outfile:
			outfile.write(PublicKey)
	with open('private.key', 'w') as outfile:
			outfile.write(PrivateKey)
	with open('cert.pem', 'w') as outfile:
			outfile.write(certificatePem)

	response = thingClient.attach_policy(
			policyName = defaultPolicyName,
			target = certificateArn
	)
	response = thingClient.attach_thing_principal(
			thingName = thingName,
			principal = certificateArn
	)

thingClient = boto3.client(
	'iot', 
	aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
	region_name=os.environ.get("REGION_NAME"))

createThing()
