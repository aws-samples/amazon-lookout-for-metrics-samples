/*
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# This code is sample only. Not for use in production.
#
# Author: Babu Srinivasan
# Contact: babusri@amazon.com, babu.b.srinivasan@gmail.com
# 
# Deploys Amazon Lookout for Metrics detector in "Continuous detection" mode.
# After this CDK is deployed successfully, detector must be activated from 
#   AWS Console/CLI to start detecting anomalies.
#  
#   Note: update stack parameters in cdk.json before deploying the stack
*/

import { ManagedPolicy, Role, ServicePrincipal } from '@aws-cdk/aws-iam';
import { CfnAnomalyDetector } from '@aws-cdk/aws-lookoutmetrics';
import * as cdk from '@aws-cdk/core';
import { CfnOutput } from '@aws-cdk/core';


export class L4mDetectorStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Retrieve parameters from cdk.json
    const datasetname = this.node.tryGetContext("datasetname");
    const dimensions = this.node.tryGetContext("dimensions").split(",");  
    const metricnames = this.node.tryGetContext("metricnames").split(",");  
    const timestampcolumn = this.node.tryGetContext("timestampcolumn");
    const timeoffset = Number(this.node.tryGetContext("timeoffset"));
    const timestampformat = this.node.tryGetContext("timestampformat"); 
    const timezone = this.node.tryGetContext("timezone");
    const l4mfrequency = this.node.tryGetContext("l4mfrequency");
    const bucketname = this.node.tryGetContext("bucketname");
    const bucketprefix = this.node.tryGetContext("bucketprefix");
    const detectorname = this.node.tryGetContext("detectorname"); 

    // S3 location for streaming data (output from AWS Glue ETL job)
    const s3pathtemplate = "s3://"+bucketname+"/"+bucketprefix+"/data/intvl_date={{yyyy-MM-dd}}/intvl_hhmm={{HHmm}}/";

    const metriclist: CfnAnomalyDetector.MetricProperty [] = [];
    metricnames.forEach((metric: any) => {
      const m: CfnAnomalyDetector.MetricProperty = {
        aggregationFunction: "SUM",
        metricName: metric
      }
      metriclist.push(m)
    });

    // Create IAM Role
    const l4mrole = new Role(this, "l4mliverole", {
      roleName: "l4mliverole",
      assumedBy: new ServicePrincipal("lookoutmetrics.amazonaws.com"),
      managedPolicies: [
        ManagedPolicy.fromAwsManagedPolicyName("AmazonS3FullAccess"),
        ManagedPolicy.fromAwsManagedPolicyName("AmazonSNSFullAccess")
      ]
    })

    const metricsource: CfnAnomalyDetector.MetricSourceProperty = {
      s3SourceConfig: {
        fileFormatDescriptor: {
          csvFormatDescriptor: {
            charset: "utf-8",
            containsHeader: true,
            delimiter: ","          }
        },
        roleArn:l4mrole.roleArn,
        templatedPathList: [s3pathtemplate]
      }
    };
    
    // Configure input data (s3) - dimensions, metrics, timestamp
    //    s3 location, timezone, frequency.
    const dataset: CfnAnomalyDetector.MetricSetProperty = {
      dimensionList: dimensions,
      metricList: metriclist,
      metricSetName: datasetname,
      metricSetDescription: "live detector using continuous data",
      metricSource: metricsource,
      metricSetFrequency: l4mfrequency,
      offset: timeoffset,
      timestampColumn: {
        columnFormat: timestampformat,
        columnName: timestampcolumn
      },
      timezone: timezone,
  
    };

    // Create a new detector in continuous mode - this does NOT activate the detector
    // The detector can be activated from AWS console/cli
    const l4mdetector = new CfnAnomalyDetector(this, "l4mdetector", {
      anomalyDetectorName:detectorname,
      anomalyDetectorDescription: "continuous detector - live data",
      metricSetList: [dataset],
      anomalyDetectorConfig: {
        AnomalyDetectorFrequency: l4mfrequency
      }
    });

    new CfnOutput(this, "Anomaly Detector", {
      description: "Anomaly detector for live data",
      exportName: "anomaly-detector-live",
      value: l4mdetector.attrArn
    });

  }
}