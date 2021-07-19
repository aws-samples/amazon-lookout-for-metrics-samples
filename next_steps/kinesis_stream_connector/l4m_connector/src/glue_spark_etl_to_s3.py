# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# This code is sample only. Not for use in production.
#
# Author: Babu Srinivasan
# Contact: babusri@amazon.com, babu.b.srinivasan@gmail.com
#
# Spark Streaming ETL script  
#   Input: 
#       1/ Kinesis Data Stream source (via AWS Glue Table)
#       2/ Time interval (for Amazon Lookout for Metrics)
#   Output: 
#       1/ Streaming data (selected columns only) organized by time interval 
#   Processing:
#       1/ Micro-batch streaming data by time interval
#       2/ Select user specified columns (dimensions & measures) and event_timestamp 
#       3/ Output data to S3 sink (organized using S3 prefixes that contains timestamp) 

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame
import datetime

args = getResolvedOptions(sys.argv, [
    "JOB_NAME",  
    "srcDBName",
    "srcTableName",
    "srcFormat",
    "l4mBucket",
    "l4mBucketPrefix",
    "l4mInterval"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Glue Job parameters - specified in cdk.json during stack deployment
bucketname = args["l4mBucket"]
bucketprefix = args["l4mBucketPrefix"]
glue_dbname = args["srcDBName"]
glue_tablename = args["srcTableName"]
src_format = args["srcFormat"]
l4m_interval = int(args["l4mInterval"])  # in minutes

s3path_data = "s3://" + bucketname + "/" + bucketprefix + "/data/"
s3path_chkpt = "s3://" + bucketname + "/" + bucketprefix + "/checkpoint/"
DELTA_MINS = datetime.timedelta(minutes=l4m_interval)
TEMP_TS = datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
BATCH_WIN_SIZE = str(l4m_interval) + " minutes"
 
 
# Function to populate time interval based on Event Timestamp. 
# This is equivalent to built-in STEP() function in Kinesis Data Analytics SQL application
def populateTimeInterval(rec):
    out_ts = (((rec['event_time'] - TEMP_TS) // DELTA_MINS) * DELTA_MINS) + TEMP_TS
    
    rec['intvl_date'] = datetime.datetime.strftime(out_ts, "%Y-%m-%d") 
    rec['intvl_hhmm'] = datetime.datetime.strftime(out_ts, "%H%M")
    return rec

# Main processing logic - called from main for each micro-batch of window size determined by time interval 
def processBatch(data_frame, batchId): 
    if (data_frame.count() > 0):
        # Convert Data frame to Glue Dynamic Frame and select only dimensions & measures that will be used by Anomaly detection
        datasource0 = DynamicFrame.fromDF(data_frame, glueContext, "from_data_frame").select_fields(['marketplace','event_time', 'views'])
        # Populate time interval (yyyy-mm-dd & HHMM) 
        datasource1 = Map.apply(frame=datasource0, f=populateTimeInterval)
        
        # datasource1.printSchema()

        # Write the dynamic frame to S3 sink with prefix constructed from time interval
        path_datasink1 = s3path_data  
        datasink1 = glueContext.write_dynamic_frame.from_options(frame = datasource1, connection_type = "s3", \
                        connection_options = {"path": path_datasink1, "partitionKeys": ["intvl_date", "intvl_hhmm"]}, \
                        format_options={"quoteChar": -1, "timestamp.formats": "yyyy-MM-dd HH:mm:ss"}, \
                        format = src_format, transformation_ctx = "datasink1")

#### Main
data_frame_datasource0 = glueContext.create_data_frame.from_catalog(stream_batch_time = BATCH_WIN_SIZE, \
                            database = glue_dbname, table_name = glue_tablename, transformation_ctx = "datasource0", \
                            additional_options = {"startingPosition": "TRIM_HORIZON", "inferSchema": "false"})
data_frame_datasource0.printSchema()
glueContext.forEachBatch(frame = data_frame_datasource0, batch_function = processBatch, \
                        options = {"windowSize": BATCH_WIN_SIZE, "checkpointLocation": s3path_chkpt})
job.commit()