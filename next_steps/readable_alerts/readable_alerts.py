import json
import os
import datetime
from dateutil.parser import parse
import boto3

# Read in the topic as provided in an environment variable
topic_arn = os.getenv('topic_arn')


def send_to_sns(message):
    # This takes in a string and simply sends it onto SNS as a message, subject provided for Email clients
    sns = boto3.client("sns")
    sns.publish(TopicArn=topic_arn, 
            Message=message, 
            Subject="Lookout for Metrics Alert Update")


def create_anomaly_string(input_json):
    """
    This function does most of the work, it takes in the entire message of the alert from Lookout for Metrics, then converts it into a readable and actionable message. Steps are commented below, feel free to update as needed.
    """
    # The time is a critical bit of informatin to sort first, this obtains the time and gets it ready for the message
    timestamp = parse(input_json['timestamp'], fuzzy_with_tokens=True)[0]
    timestamp1 = timestamp.strftime("%B %d %Y")
    timestamp2 = timestamp.strftime("%H:%M")
    # Write the first bit about the anomaly, what happened and when.
    response = "An anomaly in " + str(input_json['impactedMetric']['metricName']) + " was detected on " + timestamp1 + ' at ' + timestamp2 + ".\n"
    # Next grab the list of impacted time series
    num_of_time_series = len(input_json['impactedMetric']['relevantTimeSeries'])
    # Report the number of impacted time series to your user
    response += str(num_of_time_series) + " time series was impacted.\n\n"

    # Iterate over each time series, listing the dimensions and their value
    for ts in range(num_of_time_series):
        response += "TimeSeries: " + str(num_of_time_series) + " was impacted on the following dimensions and values:\n"
        for item in input_json['impactedMetric']['relevantTimeSeries'][ts]['dimensions']:
            response += "\t" + item['dimensionName'] + " - " + item['dimensionValue'] + "\n"
            
    # Report the anomaly score
    response += "\nThe Anomaly  score was: " + str(input_json['anomalyScore']) + "\n"
    
    # Generate a link to the console for the user to learn more
    response += "To learn more visit the Lookout for Metrics console at: " + input_json['consoleUrl'] + " \n"
    return response

def lambda_handler(event, context):
    # Call the create string function
    response = create_anomaly_string(input_json=event)
    # Send the string to SNS
    send_to_sns(message=response)
    # Report completed
    return {
        'statusCode': 200,
        'body': json.dumps('Message Delivered!')
    }