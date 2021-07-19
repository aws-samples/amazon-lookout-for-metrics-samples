/*
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# This code is sample only. Not for use in production.
#
# Author: Babu Srinivasan
# Contact: babusri@amazon.com, babu.b.srinivasan@gmail.com
# 
# Deploys data generator lambda and schedules it to run every time interval
# After the stack is deployed, the AWS EventBridge rule must be enabled to 
#  run lambda function at specified time interval. 
# 
#   Note: update stack parameters in cdk.json before deploying the stack
*/

import * as cdk from '@aws-cdk/core';
import { Stream } from '@aws-cdk/aws-kinesis';
import { PolicyStatement } from "@aws-cdk/aws-iam"
import { Function, Runtime, AssetCode} from "@aws-cdk/aws-lambda"
import { CfnOutput, Duration } from '@aws-cdk/core';
import { Rule, RuleTargetInput, Schedule } from '@aws-cdk/aws-events';
import { LambdaFunction } from '@aws-cdk/aws-events-targets';

export class DataGeneratorStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
  
    // retrieve parameters from cdk.json
    const streamName = this.node.tryGetContext('streamName');
    const streamShards = Number(this.node.tryGetContext('streamShards'))

    const functionName = this.node.tryGetContext('functionName');
    const runFrequency = Number(this.node.tryGetContext('runFrequency'));
    const loggingLevel = this.node.tryGetContext('lambdaLoggingLevel');
    
    // create a new Kinesis Data Stream (KDS)
    const kds = new Stream(this, streamName, {
      streamName: streamName, 
      shardCount: streamShards
    });

    // create IAM policy with permissions to write to KDS  
    const lambdaPolicy1 = new PolicyStatement();
    lambdaPolicy1.addActions("kinesis:putRecords");
    lambdaPolicy1.addResources(kds.streamArn);

    const lambdaPolicy2 = new PolicyStatement();
    lambdaPolicy2.addActions("kinesis:DescribeStream");
    lambdaPolicy2.addAllResources();

    // deploy the lambda function (data generator) from /src/ directory
    const dataGenerator = new Function(this, functionName, {
      functionName: functionName,
      handler: "synth_live_data_csv.lambda_handler",
      runtime: Runtime.PYTHON_3_8,
      environment: {
        "LOGGING_LEVEL": loggingLevel
      },
      code: new AssetCode('./src'),
      timeout: Duration.seconds(10),
      memorySize: 256,
      initialPolicy: [lambdaPolicy1, lambdaPolicy2]
    });

    /* 
    Setup lambda function as the event target with KDS stream name (obtained from cdk.json) as the input parameter.
    The input parameter is passed to lambda function via 'event' data structure
    */     
    const eventTarget = new LambdaFunction(dataGenerator, {
      event: RuleTargetInput.fromObject({ "stream_name": streamName })

    });

    /* 
    Create event rule to run data generator lambda at specified run frequency (in minutes).
    The run frequency is passed to this code from cdk.json context variables.
    The event rule is created in disabled status. Please set 'enabled' to true if you want 
     the lambda to start running when the resources are deployed by this CDK. Otherwise, leave 
     'enabled' set to false. When you are ready to generate data and ingest it from KDS, you can 
     enable the rule from AWS console or from AWS CLI. 
    */ 
    const eventRule = new Rule(this, 'eventRule', {
      enabled: false,   
      description: "Event to run data generator lambda at specified interval",
      ruleName: "run-data-generator-lambda",
      schedule: Schedule.rate(Duration.minutes(runFrequency)),
      targets: [eventTarget]
    });

    new CfnOutput(this, "Lambda Function", {
      description: "Lambda function to generate sample data",
      exportName: "data-generator-lambda",      
      value: dataGenerator.functionArn
    });

    new CfnOutput(this, "Kinesis Data Stream", {
      description: "Data stream to ingest sample data",
      exportName: "data-stream-kds",      
      value: kds.streamArn
    });

    new CfnOutput(this, "Event Bridge rule", {
      description: "Rule to schedule lambda function at user specified time interval",
      exportName: "schedule-lambda-rule",      
      value: eventRule.ruleArn
    });    

  }
}
