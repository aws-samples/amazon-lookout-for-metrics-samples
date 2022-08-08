/*
*/
import { Stack, StackProps, CfnParameter } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Bucket } from 'aws-cdk-lib/aws-s3';
import { L4mDetectorStack } from './l4m-detector';
import { L4mAlertSnsStack } from './l4m-alert-sns';
import { L4mLambdaAlertStack } from './l4m-alert-lambda';
import { GlueCrawlerStack } from './glue-crawler';

interface L4mDetectorRootStackProps extends StackProps {
  env: any;
};

export class L4mDetectorRootStack extends Stack {
  constructor(scope: Construct, id: string, props: L4mDetectorRootStackProps) {

    super(scope, id, props);
    const {env} = props;

    // Pass in the AWS Account number to use in the bucket name created in the L4M Getting
    // Started notebook prerequisite. If you used a different bucket name, this will 
    // need to be modified.
    const AWSAccountNumber = new CfnParameter(this, "AWSAccountNumber", {
      type: 'String',
      noEcho: true,
      description: "Your AWS Account Number (used in the bucket name and role ARN)"
    });

    // Retrieve the s3 bucket ARN for the metric source, Lambda, and Glue access policies.
    const s3Bucket = Bucket.fromBucketName(this, 's3Bucket', AWSAccountNumber.valueAsString + '-lookoutmetrics-lab');
  
    const l4mDetectorStack = new L4mDetectorStack(this, 'l4mDetectorStack', {
      bucketArn: s3Bucket.bucketArn,
      bucketName: s3Bucket.bucketName,
      bucketPrefix: env.bucketPrefix,
      detectorFrequency: env.detectorFrequency,
      metrics: env.metrics,
      dimensions: env.dimensions,
      timestampFormat: env.timestampFormat,
      timestampColumn: env.timestampColumn
    });

    // Build the SMS Alert only if the SMS number is provided in the cdk.json.
    // The samples code, by default, leaves it as null.
    // Number must be provided in the E.164 format (e.g. for US, +1XXX5550100)
    if (env.smsSubscriptionNumber) {
      const l4mAlertSnsStack = new L4mAlertSnsStack(this, 'l4mSnsAlertStack', {
        l4mAnomalyDetectorArn: l4mDetectorStack.l4mAnomalyDetectorArn,
        smsSubscriptionNumber: env.smsSubscriptionNumber
      });
    };

    const l4mAlertLambdaStack = new  L4mLambdaAlertStack( this, 'L4mAlertLambdaStack', {
      l4mAnomalyDetectorArn: l4mDetectorStack.l4mAnomalyDetectorArn,
      l4mDetectorMetricSetArn: l4mDetectorStack.l4mDetectorMetricSetArn,
      s3BucketArn: s3Bucket.bucketArn,
      lambdaHandlerName: env.lambdaHandlerName,
      lambdaRelativePath: env.lambdaRelativePath,
      lambdaMemorySize: env.lambdaMemorySize,
      lambdaDuration: env.lambdaDuration,
      pandasLayerArn: env.pandasLayerArn
    });

    const glueCrawlerStack = new GlueCrawlerStack( this, 'glueCrawlerStack', {
      s3BucketArn: s3Bucket.bucketArn,
      s3BucketName: s3Bucket.bucketName,
      glueCatalogDbName: env.glueCatalogDbName
    });
  }
}

  