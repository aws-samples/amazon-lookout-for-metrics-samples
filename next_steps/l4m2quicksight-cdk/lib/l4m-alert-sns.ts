/*
https://docs.aws.amazon.com/lookoutmetrics/latest/dev/detectors-alerts.html

Creates the Amazon SLookout for Metrics SNS Alert, the SNS topic, and 
required access role.

The SMS number provided must be in the E.164 format (e.g. for US, +1XXX5550100)
or SNS subscription will not work properly.
*/
import { NestedStack, NestedStackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CfnAlert } from 'aws-cdk-lib/aws-lookoutmetrics';
import { Topic } from 'aws-cdk-lib/aws-sns';
import { SmsSubscription } from 'aws-cdk-lib/aws-sns-subscriptions';
import { Role, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { Alias } from 'aws-cdk-lib/aws-kms';

interface L4mAlertSnsStackProps extends NestedStackProps {
  l4mAnomalyDetectorArn: string;
  smsSubscriptionNumber: string;
};

export class L4mAlertSnsStack extends NestedStack {
  constructor(scope: Construct, id: string, props: L4mAlertSnsStackProps) {
    super(scope, id, props);
    const {l4mAnomalyDetectorArn, smsSubscriptionNumber} = props;

    // Create the SNS topic for the alert to ...
    const detectorAlertTopic = new Topic(this, 'detectorAlertTopic', {
      masterKey: Alias.fromAliasName(this, 'aws/sns', 'aws/sns')
    });

    // Subscribe to the SNS Topic using the SMS number specified in the cdk.json
    // Building this alert is optional. If no SMS number is provided, this stack is skipped.
    // If the number is not provided in correct E.164 format, SNS will handle the error.
    detectorAlertTopic.addSubscription(new SmsSubscription(smsSubscriptionNumber))

    // Create the alert role and grant publish permissions on the topic
    const detectorAlertRole = new Role(this, 'detectorAlertRole', {
      assumedBy: new ServicePrincipal('lookoutmetrics.amazonaws.com')
    });
    detectorAlertTopic.grantPublish(detectorAlertRole);

    // Create the detector SNS alert and attach it to the detector
    const detectorAlert = new CfnAlert(this, 'detectorAlert', {
      action: {
        snsConfiguration: {
          roleArn: detectorAlertRole.roleArn,
          snsTopicArn: detectorAlertTopic.topicArn
        },
      },
      alertSensitivityThreshold: 50,
      anomalyDetectorArn: l4mAnomalyDetectorArn
    });
  }
}
