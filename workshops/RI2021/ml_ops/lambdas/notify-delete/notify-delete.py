import os
from boto3 import client

def get_message(event):
    message = 'Resource Delete: '
    if 'statesError' in event.keys():
        message += f"Internal error: {event['statesError']}"
    if 'serviceError' in event.keys():
        message += f"Service error: {event['statesError']}"
    if 'datasetGroupArn' in event.keys():
        message += f"DatasetGroup deleted: {event['datasetGroupArn']}"
    if 'Error' in event.keys():
        message += f"State machine failed: {event['Error']} : {event['Cause']}"
    return message


def lambda_handler(event, context):
    print("NOTIFY FUNCTION LOG --------")
    
    print(event)
    
    print("NOTIFY FUNCTION LOG END --------")
    
    return True
    
    
