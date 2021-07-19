# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# This code is sample only. Not for use in production.
#
# Credits:  
#  Based on: https://github.com/aws-samples/amazon-lookout-for-metrics-samples/blob/main/getting_started/synth_data.py
#  Changes: 1/Added 'write_to_kinesis' function 2/Changed main loop to write only one set of records & other minor tweaks
#           3/Added logging & exception handling 4/Code changes to deploy as AWS Lambda function
#
# Author: Babu Srinivasan
# Contact: babusri@amazon.com, babu.b.srinivasan@gmail.com

import os
import math
import random
import itertools
import datetime
import boto3
import logging 
from botocore.exceptions import ClientError

loglevel = os.getenv('LOGGING_LEVEL', "WARNING")
logger = logging.getLogger()
logger.setLevel(loglevel)

aws_region = os.getenv('AWS_REGION', "us-east-1")
kinesis_client = boto3.client('kinesis', region_name=aws_region)

frequency = 1  # sample data generation frequency in minutes.This should match lambda event schedule

dimensions = { "platform" : [ "pc_web", "mobile_web", "mobile_app" ], "marketplace" : [ "us", "uk", "de", "fr", "es", "it", "jp" ] }
metrics = [ "views", "revenue" ]

# numbers used for simulating data - both regular and anomalous data points
daily_peak_size_range = ( 200, 400 )
daily_peak_time = ( 12 * 60, 21 * 60 )
daily_offset_range = ( 100, 200 )

random_factor_size_range = (2, 10)

anomaly_size_range = ( 100, 600 )
anomaly_length_range = ( 1, 5 * 60 )
anomaly_possibility = 0.005

introduce_metric_from_upstream = [
    lambda x : max( int(x), 0 ),    # sin curve -> views 
    lambda x : x * 0.3,             # views -> revenue
]


class DailyPattern:  
    def __init__( self ):
        self.peak_size = random.uniform( *daily_peak_size_range )
        self.peak_time = random.uniform( *daily_peak_time )
        self.offset = random.uniform( *daily_offset_range )
    
    def get( self, t ):
        minutes_in_day = t.hour * 60 + t.minute
        factor1 = math.cos( (( minutes_in_day - self.peak_time ) / ( 24 * 60 )) * 2 * math.pi ) * self.peak_size + self.peak_size + self.offset
        return factor1

class RandomFactor:
    def __init__( self ):
        self.size = random.uniform( *random_factor_size_range )

    def get(self):
        return random.uniform( -self.size, self.size )

class Anomaly:
    def __init__(self):
        self.remaining_time = random.randint( *anomaly_length_range )
        self.offset = random.uniform( *anomaly_size_range ) * (random.randint(0,1)*2-1)

    def proceed_time(self):
        # self.remaining_time -= pd.to_timedelta(frequency).seconds / 60
        self.remaining_time -= datetime.timedelta(minutes=frequency).seconds / 60
        return self.remaining_time <= 0

    def get(self):
        return self.offset

class Item:
    def __init__( self, dimension ):
        self.dimension = dimension
        
        self.daily_pattern = DailyPattern()
        self.random_factor = RandomFactor()
        self.anomaly = None
    
    def get( self, t ):    
        if random.random() < anomaly_possibility:
            self.anomaly = Anomaly()
        
        value = self.daily_pattern.get(t)
        
        value += self.random_factor.get()

        is_anomaly = bool(self.anomaly)
        if self.anomaly:
            value += self.anomaly.get()
            if self.anomaly.proceed_time():
                self.anomaly = None
        
        metric_values = []
        for i, metric in enumerate(metrics):
            value = introduce_metric_from_upstream[i](value)
            metric_values.append(value)
        
        return metric_values, is_anomaly


def synthesize():
    # create item list - for the given set of dimensions and values
    item_list = []
    for dimension_values in itertools.product( *dimensions.values() ):
        item = Item( dict( zip( dimensions.keys(), dimension_values ) ) )
        item_list.append(item)
    
    # itereate and prepare data    
    dimension_values_list = []
    for i in range( len(dimensions) ):
        dimension_values_list.append([])

    timestamp_list = []

    metric_values_list = []
    for i, metric in enumerate(metrics):
        metric_values_list.append([])

    # for each combination of dimesion values, populate metric & timestamp data points
    t = datetime.datetime.utcnow()
    tstr = datetime.datetime.strftime(t,"%Y-%m-%d %H:%M:%S")
    logger.info('Generating data for timestamp '+tstr)

    for item in item_list:
        
        for i, d in enumerate(item.dimension.values()):
            dimension_values_list[i].append(d)
        
        timestamp_list.append(tstr)
        
        metric_values, is_anomaly = item.get(t)
        for i, metric_value in enumerate(metric_values):
            metric_values_list[i].append(metric_value)

    data = {}
    for dimension_name, dimension_values in zip( dimensions.keys(), dimension_values_list ):
        data[dimension_name] = dimension_values
    data["event_time"] = timestamp_list

    for metric_name, metric_values in zip( metrics, metric_values_list ):
        data[metric_name] = metric_values

    # convert dictionary of lists (containing dimension & metric values) to comma separated string records
    synthdata = []
    for k in zip(*data.values()):
        synthdata.append(",".join(map(str, k)))    
    return synthdata

# function to write simulated records to Kinesis data stream
def write_to_kinesis(synthdata, stream_name):
    # generate KDS partition key randomly
    part_key = str(math.floor(random.random()*(10000000000)))
    records = []
    # structure records for KDS
    for row in synthdata:
        records.append({"PartitionKey": part_key, "Data": row + "\n"})

    # check if stream exists before writing records to it.
    try:
        logger.info('Checking if stream '+stream_name+' exists')
        resp = kinesis_client.describe_stream(StreamName=stream_name)
    except ClientError:
        logger.error('Error locating stream '+stream_name, exc_info=1)
        raise
    else:
        pass

    # write records to stream using batch put
    try:
        logger.info('Writing records to '+stream_name+' with partition key '+part_key)
        response = kinesis_client.put_records(StreamName=stream_name, Records=records)
    except ClientError:
        logger.error('Error writing records to '+stream_name, exc_info=1)
        raise 
    else:
        logger.debug('## Records written to Kinesis Data stream:')
        logger.debug(records)
        return (response) 

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(' AWS_REGION='+os.environ['AWS_REGION'])
    logger.info(' LOGGING_LEVEL='+os.environ['LOGGING_LEVEL'])
    logger.info('## EVENT')
    logger.info(event)

    # get stream name passed from CDK code via lambda event data structure
    stream_name = event['stream_name']
    
    synthdata = synthesize()
    kinesis_response = write_to_kinesis(synthdata, stream_name)
    logger.info(str(kinesis_response['FailedRecordCount'])+" records failed to write to stream")
    
    return {"failed_rec_count": kinesis_response['FailedRecordCount']}