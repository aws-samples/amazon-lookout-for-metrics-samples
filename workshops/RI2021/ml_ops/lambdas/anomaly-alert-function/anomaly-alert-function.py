import time
import os
import io
import json
import shutil
import zipfile
import pathlib
import pandas as pd
import boto3
import datetime
import botocore
from dateutil.parser import parse
s3 = boto3.client('s3')
lookoutmetrics_client = boto3.client( "lookoutmetrics")

def lambda_handler(event, context):
    
    #Function to format the date given by the event
    def datetime_from_string(s):
        try:
            dt = datetime.datetime.fromisoformat(s.split("[")[0])
        except ValueError:
            dt = datetime.datetime.strptime(s.split("[")[0], "%Y-%m-%dT%H:%MZ")
        return dt
    #Function to update the metricValue_AnomalyScore csv in the case that one already exists
    def update_Anomaly_CSV(event,key,bucket,obj,response):
        print('object exist')
        #Reading the existing file
        original_df = pd.read_csv(obj.get("Body"), index_col=False)
        file2 = original_df.to_dict('list')

        #getting the needed data
        metricList = response['MetricList']
        dimensionList = response['DimensionList']
        metricName = event['impactedMetric']['metricName']
 
        #Column names generator
        data2={}
        data2['key']=[]
        data2['Timestamp'] =[]
        for i in dimensionList:
            data2[i]=[]
        #    data2[i]=[]
        for i in metricList:
            data2[i['MetricName']+'AnomalyMetricValue']=[]
            data2[i['MetricName']+'GroupScore']=[]
    
        #Data collection from the event for the CSV
        for i in event['impactedMetric']['relevantTimeSeries']:
            for a in i['dimensions']:
                data2[a['dimensionName']].append(a['dimensionValue'])
            data2[metricName+'AnomalyMetricValue'].append(i['metricValue'])
            data2[metricName+'GroupScore'].append(event['anomalyScore'])
            data2['Timestamp'].append(start_time)
            
        nRow=len(data2['Timestamp'])
        nDimension = len(dimensionList)
        
        #key generator
        i=0
        while i<nRow:
            value=''
            for a in dimensionList:
                value+=str(data2[a][i])
            value= str(data2['Timestamp'][i])+value
            data2['key'].append(value)
            i=i+1
        c=0
        #Checking if the data is  already in the original file and ammend the empty spaces and add the data  
        for n in data2['key']:
            
            if n in file2['key']:
                where=file2['key'].index(n)
                file2[metricName+'AnomalyMetricValue'][where] = data2[metricName+'AnomalyMetricValue'][c]
                file2[metricName+'GroupScore'][where] =data2[metricName+'GroupScore'][c]
            else:
                file2['key'].append(data2['key'][c])
                for i in dimensionList:
                    file2[i].append(data2[i][c])
                
                file2[metricName+'AnomalyMetricValue'].append(data2[metricName+'AnomalyMetricValue'][c])
                file2[metricName+'GroupScore'].append(data2[metricName+'GroupScore'][c])
                file2['Timestamp'].append(dateTime)
            c+=1
            
        df = pd.DataFrame.from_dict(data=file2, orient='index')
        df2 = df.transpose()
        with io.StringIO() as filename:
            df2.to_csv(filename, index=False, encoding='utf-8')
            response = s3.put_object(
                Bucket=bucket, Key=key, Body=filename.getvalue()
            )
        print('updated Anomaly csv saved')
    #If the metricValue_AnomalyScore file does not exist it will create one
    def generate_Anomaly_CSV(event,key,bucket,response):
        #getting the needed data
        metricList = response['MetricList']
        dimensionList = response['DimensionList']
        metricName = event['impactedMetric']['metricName']
        pd.options.mode.use_inf_as_na = True
        
        #Column names generator
        data2={}
        data2['key']=[]
        data2['Timestamp'] =[]
        for i in dimensionList:
            data2[i]=[]
            data2[i]=[]
        for i in metricList:
            data2[i['MetricName']+'AnomalyMetricValue']=[]
            data2[i['MetricName']+'GroupScore']=[]
    
        #Data collection for the CSV
        for i in event['impactedMetric']['relevantTimeSeries']:
            for a in i['dimensions']:
                data2[a['dimensionName']].append(a['dimensionValue'])
            data2[metricName+'AnomalyMetricValue'].append(i['metricValue'])
            data2[metricName+'GroupScore'].append(event['anomalyScore'])
            data2['Timestamp'].append(start_time)
        nRow=len(data2['Timestamp'])
        #key generator
        i=0
        while i<nRow:
            value=''
            for a in dimensionList:
                value+=str(data2[a][i])
            value= str(data2['Timestamp'][i])+value
            data2['key'].append(value)
            i+=1

        df = pd.DataFrame.from_dict(data=data2, orient='index')
        df2 = df.transpose()

        with io.StringIO() as filename:
            df2.to_csv(filename, index=False, encoding='utf-8')
            response = s3.put_object(
                Bucket=bucket, Key=key, Body=filename.getvalue()
            )
        print('Anomaly csv saved in', key)
    #Checks if the metricValue_AnomalyScore file already exists
    def Anomaly_CSV_Check(event,key,bucket,response):
        try:
            obj = s3.get_object(Bucket=bucket,Key=key) 
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code']=='404' or e.response['Error']['Code']=='NoSuchKey':
                print('the Anomaly csv file does not exist and we will generate the very first file now')
                generate_Anomaly_CSV(event,key,bucket,response)
            else:
                print('something else happened')
                print('error is', e.response)
                raise
        else:
            update_Anomaly_CSV(event,key,bucket,obj,response)
    #Updates the dimensionContributions csv file if it exists
    def update_Dimension_CSV(event,key,obj,bucket):
        print('object exist')
        original_df = pd.read_csv(obj.get("Body"), index_col=False)
        file = original_df.to_dict('list')
        #Column Titles generation
        data = {}
        data ['Timestamp'] =[]
        data['metricName'] =[]
        data['dimensionName'] =[]
        data['dimensionValue'] =[]
        data['valueContribution'] =[]
        
        #Data collection for the CSV
        for i in event['impactedMetric']['dimensionContribution']:
            for a in i['dimensionValueContributions']:
                data['Timestamp'].append(start_time)
                data['dimensionName'].append(i['dimensionName'])
                data['dimensionValue'].append(a['dimensionValue'])
                data['valueContribution'].append(a['valueContribution'])
                data['metricName'].append(event['impactedMetric']['metricName'])
          
        df=pd.DataFrame(data=data)
        df2 = pd.DataFrame(data=file)
        result = pd.concat([df2, df])

        with io.StringIO() as filename:
            result.to_csv(filename, index=False, encoding='utf-8')
            response = s3.put_object(
                Bucket=bucket, Key=key, Body=filename.getvalue()
            )
        print('updated Dimension csv saved')
    
    #Generates the dimensionContributions csv file     
    def generate_Dimension_CSV(event,key,bucket):
        #Column Titles generator
        data = {}
        data ['Timestamp'] =[]
        data['metricName'] =[]
        data['dimensionName'] =[]
        data['dimensionValue'] =[]
        data['valueContribution'] =[]
        
        #Data collection for the CSV
        for i in event['impactedMetric']['dimensionContribution']:
            for a in i['dimensionValueContributions']:
                data['Timestamp'].append(start_time)
                data['dimensionName'].append(i['dimensionName'])
                data['dimensionValue'].append(a['dimensionValue'])
                data['valueContribution'].append(a['valueContribution'])
                data['metricName'].append(event['impactedMetric']['metricName'])
          
        df=pd.DataFrame(data=data)
        print('the dimension first csv file is', )
        #CSV generation and upload to S3
        with io.StringIO() as filename:
            df.to_csv(filename, index=False)
            response = s3.put_object(
                Bucket=bucket, Key=key, Body=filename.getvalue()
            )
        print('the Dimension CSV has been saved in', key)
    #Checks if the dimensionContributions csv file already exists
    def Dimension_CSV_Check(event,key,bucket):
        try:
           obj = s3.get_object(Bucket=bucket,Key=key) 
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code']=='404' or e.response['Error']['Code']=='NoSuchKey':
                print('the Dimension csv file does not exist and we will generate the very first file now')
                generate_Dimension_CSV(event,key,bucket)
            else:
                print('something else happened')
                print('error is', e.response)
                raise
        else:
            update_Dimension_CSV(event,key,obj,bucket)
    
    start_time = datetime_from_string(event["timestamp"] )
    dateTime = str(start_time)
    splitdate = dateTime.split()
    
    #Initial parameters. Here you write the bucket and the ARN from the dataset of the detector (do not change the key1 and key2)
    #Write the bucket where you want the results to be located. THE BUCKET HAS TO ALREADY EXIST
    bucket = os.getenv('S3_BUCKET')
    DataSet_ARN = os.getenv('METRIC_SET_ARN')
    
    key1 = 'anomalyResults/metricValue_AnomalyScore/'+splitdate[0]+'_'+splitdate[1]+'_metricValue_AnomalyScore.csv'
    key2 = 'anomalyResults/dimensionContributions/'+splitdate[0]+'_'+splitdate[1]+'_dimensionContributions.csv'
    
    response = lookoutmetrics_client.describe_metric_set(MetricSetArn=DataSet_ARN)
    Anomaly_CSV_Check(event,key1,bucket,response)
    Dimension_CSV_Check(event,key2,bucket)
