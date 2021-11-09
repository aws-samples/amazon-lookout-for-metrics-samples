from os import environ
import actions
import boto3
from loader import Loader

LOADER = Loader()


def lambda_handler(event, context):
    # Logging
    print(event)
    # Connect to L4M:
    l4m = boto3.client( "lookoutmetrics")
    
    # Create Detector
    response = l4m.create_anomaly_detector( 
        AnomalyDetectorName = event['project'] + "-detector",
        AnomalyDetectorDescription = event['detector_description'],
        AnomalyDetectorConfig = {
            "AnomalyDetectorFrequency" : event['detector_frequency'],
        },
    )

    anomaly_detector_arn = response["AnomalyDetectorArn"]

    # Configure the Metricset
    params = {
        "AnomalyDetectorArn": anomaly_detector_arn,
        "MetricSetName" : event['project'] + '-metric-set-1',
        "MetricList" : event['metrics_set'],

        "DimensionList" : event['dimension_list'],

        "TimestampColumn" : event['timestamp_column'],

        "MetricSetFrequency" : event['detector_frequency'],

        "MetricSource" : event['metric_source'],
    }
    anomaly_detector_metric_set_arn = l4m.create_metric_set(**params)

    # Activate the Detector
    l4m.back_test_anomaly_detector(AnomalyDetectorArn=anomaly_detector_arn)

    #actions.take_action(status['status'])
    return_dict = {}
    return_dict['anomaly_detector_arn'] = anomaly_detector_arn
    return_dict['anomaly_detector_metric_set_arn'] = anomaly_detector_metric_set_arn
    return return_dict
