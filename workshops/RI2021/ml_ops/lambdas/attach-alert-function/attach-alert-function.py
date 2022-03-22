from os import environ
import actions
import boto3
from loader import Loader
import time

LOADER = Loader()


def lambda_handler(event, context):
    # Logging
    print(event)
    # Connect to L4M:
    l4m = boto3.client( "lookoutmetrics")
    
    # Connect to Lambda:
    client = boto3.client('lambda')

    # Get the ARN
    time.sleep(60)
    response = client.get_function(FunctionName=event['params']['alert_lambda_name'])
    lambda_arn = response['Configuration']['FunctionArn']

    # Attach Function to Detector
    response = l4m.create_alert(
        AlertName = event['params']['alert_name'],
        AlertSensitivityThreshold = event['params']['alert_threshold'],
        AlertDescription = event['params']['alert_description'],
        AnomalyDetectorArn = event['DetectorArn']['anomaly_detector_arn'],
        Action={
            'LambdaConfiguration': {
                'RoleArn': event['params']['metric_source']['S3SourceConfig']['RoleArn'],
                'LambdaArn':lambda_arn
            }
        }
    )

    # Next update the OS Environ variables of the lambda
    
    response = client.update_function_configuration(
            FunctionName=event['params']['alert_lambda_name'],
            Environment={
                'Variables': {
                    'S3_BUCKET': event['params']['s3_bucket'],
                    'METRIC_SET_ARN': event['DetectorArn']['anomaly_detector_metric_set_arn']['MetricSetArn']
                }
            }
        )
    return response
