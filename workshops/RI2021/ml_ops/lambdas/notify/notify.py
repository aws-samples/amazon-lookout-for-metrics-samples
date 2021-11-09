import os
from boto3 import client

def get_message(event):
    if 'statesError' in event.keys():
        return 'Internal error: {}'.format(event['statesError'])
    if 'serviceError' in event.keys():
        return 'Service error: {}'.format(event['statesError'])
    return 'Your Personalize Endpoint is ready!'

def lambda_handler(event, context):
    print("NOTIFY FUNCTION LOG --------")
    
    print(event)
    
    print("NOTIFY FUNCTION LOG END --------")
    
    return True