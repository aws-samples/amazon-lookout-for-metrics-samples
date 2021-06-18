import re
import json
import datetime

import boto3

# ----

# Configure email addresses
src_email_address = "your@email.address"
dst_email_address = "your@email.address"

# ----

# Parse anomaly detector ARN and extract components
def parse_anomaly_detector_arn( anomaly_detector_arn ):
    re_result = re.match( r"arn:aws:lookoutmetrics:([a-z0-9-]+):([0-9]+):AnomalyDetector:(.*)", anomaly_detector_arn )
    region_name = re_result.group(1)
    account_id = re_result.group(2)
    anomaly_detector_name = re_result.group(3)
    return region_name, account_id, anomaly_detector_name
    
# Parse L4M's timestamp string and construct a datetime object
def parse_l4m_timestamp(s):
    re_result = re.match( r"([0-9]+)\-([0-9]+)\-([0-9]+)T([0-9]+):([0-9]+)Z\[(.+)\]", s )
    t = datetime.datetime( 
        int(re_result.group(1)), 
        int(re_result.group(2)), 
        int(re_result.group(3)), 
        int(re_result.group(4)), 
        int(re_result.group(5)), 
    )
    return t

# Format anomaly group detail page URL
def create_url_to_console( anomaly_detector_arn, anomaly_group_id ):
    region_name, _, _ = parse_anomaly_detector_arn(anomaly_detector_arn)
    url = f"https://{region_name}.console.aws.amazon.com/lookoutmetrics/home?region={region_name}#{anomaly_detector_arn}/anomalies/anomaly/{anomaly_group_id}"
    return url

# Look up the anomaly group which matches the received alert, and gather details
def lookup_anomaly_group_and_get_details( anomaly_detector_arn, alert_timestamp, alert_metric_name ):

    relevant_time_series = []

    # Extract region name from detector ARN
    region_name, _, _ = parse_anomaly_detector_arn(anomaly_detector_arn)

    # Create L4M client
    lookoutmetrics_client = boto3.client( "lookoutmetrics", region_name=region_name )

    # Find the anomaly group by checking metric names and timestamps
    anomaly_group_id = None
    next_token = None
    while True:
        params = {
            "AnomalyDetectorArn" : anomaly_detector_arn,
            "SensitivityThreshold" : 0,
            "MaxResults" : 100,
        }

        if next_token:
            params["NextToken"] = next_token

        response = lookoutmetrics_client.list_anomaly_group_summaries( **params )

        for anomaly_group in response["AnomalyGroupSummaryList"]:
            
            anomaly_group_metric_name = anomaly_group['PrimaryMetricName']
            anomaly_group_start_time = parse_l4m_timestamp( anomaly_group["StartTime"] )
            anomaly_group_end_time = parse_l4m_timestamp( anomaly_group["EndTime"] )

            # Check if this AnomalyGroup matches
            if alert_metric_name == anomaly_group_metric_name:
                if anomaly_group_start_time<=alert_timestamp and alert_timestamp<=anomaly_group_end_time:
                    anomaly_group_id = anomaly_group["AnomalyGroupId"]
                    break

        # Exit loop when found
        if anomaly_group_id:
            break

        # Loop continues when NextToken is included in the response
        if "NextToken" in response:
            next_token = response["NextToken"]
            continue
        
        # Not found
        break

    # If anomaly group was found, gather all relevant time series
    if anomaly_group_id:

        next_token = None
        while True:

            params = {
                "AnomalyDetectorArn" : anomaly_detector_arn,
                "AnomalyGroupId" : anomaly_group_id,
                "MetricName" : alert_metric_name,
                "MaxResults" : 100,
            }

            if next_token:
                params["NextToken"] = next_token

            response = lookoutmetrics_client.list_anomaly_group_time_series( **params )
            
            # Gather relevant time series
            for time_series in response["TimeSeriesList"]:
                relevant_time_series.append( time_series["DimensionList"] )

            # Loop continues when NextToken is included in the response
            if "NextToken" in response:
                next_token = response["NextToken"]
                continue

            break
    
    else:
        raise KeyError("AnomalyGroup not found")
    
    # Return anomaly group id, and list of relevant time series
    return anomaly_group_id, relevant_time_series


# Compile email subject and HTML body from gathered information
def create_email_contents( anomaly_detector_arn, alert_timestamp, alert_metric_name, anomaly_score, anomaly_group_id, relevant_time_series ):
    
    # Format email subject
    subject = "L4M Alert - %s - %s" % ( alert_metric_name, alert_timestamp.strftime("%Y-%m-%d %H:%M") )

    # Begin formatting HTML body
    html_body = '<body style="font-family:Helvetica; font-size: 11pt;">\n'

    # Table of summary
    html_body += '<table>\n'
    html_body += "<tr> <td>%s</td> <td>%s</td> </tr>\n" % ( "Measure name :", alert_metric_name )
    html_body += "<tr> <td>%s</td> <td>%s</td> </tr>\n" % ( "Timestamp :", alert_timestamp.strftime("%Y-%m-%d %H:%M") )
    html_body += "<tr> <td>%s</td> <td>%s</td> </tr>\n" % ( "Anomaly score :", "%.2f" % anomaly_score )
    html_body += "<tr> <td>%s</td> <td>%s</td> </tr>\n" % ( "Num relevant time series :", "%d" % len(relevant_time_series) )
    html_body += '</table>\n'

    html_body += "<br>\n"

    # Prepare list of dimension names for the relevant time series table (to be consistently sorted)
    dimension_names = [ dimension["DimensionName"] for dimension in relevant_time_series[0] ]
    
    # Table of relevant time series
    html_body += '<table border="1" >\n'
    html_body += '<caption>List of relevant time series</caption>\n'

    # Header row with dimension names
    html_body += '<tr bgcolor="#ccccff">'
    for dimension_name in dimension_names:
        html_body += "<th>%s</th>" % dimension_name
    html_body += "</tr>\n"

    # Data rows with dimension values
    for dimension_list in relevant_time_series:
        
        # Converting to python dictionary to easily lookup
        dimension_name_value_map = {}
        for dimension_name_value in dimension_list:
            dimension_name_value_map[ dimension_name_value["DimensionName"] ] = dimension_name_value["DimensionValue"]

        html_body += "<tr>"
        for dimension_name in dimension_names:
            html_body += "<td>%s</td>" % dimension_name_value_map[dimension_name]
        html_body += "</tr>\n"

    html_body += '</table>\n'

    html_body += "<br>\n"

    # Direct link to anomaly group detail page
    console_url = create_url_to_console( anomaly_detector_arn, anomaly_group_id )
    html_body += '<a href="%s">Link to Lookout for Metrics console</a>\n' % console_url

    html_body += "</body>"

    # Return compiled email contents
    return subject, html_body


# Send the HTML formatted email via SES
def send_email( subject, html_body ):

    ses_client = boto3.client( "ses" )

    params = {
        "Destination" : {
            "ToAddresses" : [
                dst_email_address
            ]
        },
        "Message" : {
            "Subject" : {
                "Charset" : "UTF-8",
                "Data" : subject,
            },
            "Body" : {
                "Html" : {
                    "Charset" : "UTF-8",
                    "Data" : html_body
                }
            },
        },
        "Source" : src_email_address,
    }

    ses_client.send_email( ** params )


# Lambda entrypoint
def lambda_handler(event, context):
    
    # Get necessary information from the lambda event
    anomaly_detector_arn = event["anomalyDetectorArn"]
    alert_timestamp = parse_l4m_timestamp(event["timestamp"])
    alert_metric_name = event["impactedMetric"]["metricName"]
    anomaly_score = event["anomalyScore"]

    # Lookup anomaly group by metric name and timestamp
    anomaly_group_id, relevant_time_series = lookup_anomaly_group_and_get_details( anomaly_detector_arn, alert_timestamp, alert_metric_name )
    
    # Create email contents from the identified information
    subject, html_body = create_email_contents( anomaly_detector_arn, alert_timestamp, alert_metric_name, anomaly_score, anomaly_group_id, relevant_time_series )

    # Send email by SES
    send_email( subject, html_body )

    # Returning from Lambda function
    return {
        'statusCode': 200,
        'body': json.dumps('Message Delivered!')
    }

