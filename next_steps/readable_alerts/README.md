# Human Readable Alerts

By default the alerts that are delivered from Lookout for Metrics contain a great deal of information via a JSON response, however these are not consumable to the average human, for example:

```JSON
{
  "alertName": "CanaryAlert-009a9443-d34a-41af-b782-f6e409db55c2",
  "alertEventId": "arn:aws:lookoutmetrics:us-east-1:246405784697:Alert:CanaryAlert-009a9443-d34a-41af-b782-f6e409db55c2:event/3bf090ef-5437-4262-920c-512d311c1503",
  "anomalyDetectorArn": "arn:aws:lookoutmetrics:us-east-1:246405784697:AnomalyDetector:CanaryAD-BackTest-PT1H-RCF-LOW_VOL-12768b4f-8636-4089-b",
  "alertArn": "arn:aws:lookoutmetrics:us-east-1:246405784697:Alert:CanaryAlert-009a9443-d34a-41af-b782-f6e409db55c2",
  "alertDescription": null,
  "impactedMetric": {
    "metricName": "revenue",
    "dimensionContribution": [
      {
        "dimensionName": "colorCode",
        "dimensionValueContributions": [
          {
            "dimensionValue": "blue",
            "valueContribution": 100
          }
        ]
      },
      {...

```

The content above is not particularly useful, what we want to do instead is to deploy a simple solution that will deliver a human readable response to our end user so that they can take appropriate action, the guide below will convert the response above into an email that looks like this:

```
An anomaly in revenue was detected on February 17 2021 at 11:00.
1 time series was impacted.

TimeSeries: 1 was impacted on the following dimensions and values:
        colorCode - blue
        deviceType - tablet
        marketplace - CANADA
        platform - windows

The Anomaly  score was: 28.29
To learn more visit the Lookout for Metrics console at: https://us-west-2.con....
```

This provides more digestable information to our user and connects them with the service to learn more.

## Overview

The included CloudFormation template will create the following resources for you:

1. SNS Topic to receive the new alerts.
1. SNS Subscription to deliver the alerts to a specified email address.
1. An IAM Role for Lambda to deliver notifications to ONLY the newly created topic.
1. A Lambda function to actually perform the work

You will still need to create the Alert mechanism within Lookout for Metrics and to create a role that Lookout for Metrics can assume in order to execute your newly created Lambda. 

## Getting Started

The simplest possible option is to simply deploy the existing template and answer a few questions, to do that click the link below and follow along with the screenshots provided. At the end of it, the human readable alerts will arrive in your inbox automatically!

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=HumanReadableAlerts&templateURL=https://lookoutformetricsbucket.s3.amazonaws.com/HumanReadableAlerts.YAML)