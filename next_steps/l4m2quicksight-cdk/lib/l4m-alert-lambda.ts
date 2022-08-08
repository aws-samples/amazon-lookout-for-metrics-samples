/*
https://docs.aws.amazon.com/lookoutmetrics/latest/dev/detectors-alerts.html

Creates the AWS Lambda function, the Amazon Lookout for Metrics Lambda Alert, and 
the required access role.
*/
import { NestedStackProps, NestedStack, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { join } from 'path';
import { Role, ServicePrincipal, ManagedPolicy, PolicyDocument, PolicyStatement, Effect } from 'aws-cdk-lib/aws-iam';
import { Function, Runtime, Code, LayerVersion, Tracing } from 'aws-cdk-lib/aws-lambda';
import { CfnAlert } from 'aws-cdk-lib/aws-lookoutmetrics';

interface L4mLambdaAlertStackProps extends NestedStackProps {
  l4mAnomalyDetectorArn: string,
  l4mDetectorMetricSetArn: string,
  s3BucketArn: string,
  lambdaHandlerName: string,
  lambdaRelativePath: string,
  lambdaMemorySize: number,
  lambdaDuration: number,
  pandasLayerArn: string
};

export class L4mLambdaAlertStack extends NestedStack {
  constructor(scope: Construct, id: string, props: L4mLambdaAlertStackProps) {
    super(scope, id, props);

    const {
      l4mAnomalyDetectorArn,
      l4mDetectorMetricSetArn,
      s3BucketArn,
      lambdaHandlerName,
      lambdaRelativePath,
      lambdaMemorySize,
      lambdaDuration,
      pandasLayerArn
    } = props;

    // Create the Lambda Layer from the ARN paramater set in the cdk.json
    // ARN from Keith's Layers (Klayers) github repo (https://github.com/keithrozario/Klayers)
    const pandasLayer = LayerVersion.fromLayerVersionArn(this, "pandasLayer", pandasLayerArn);

    // Limited permissions assigned ot the Lambda function
    const lambdaExecutionRolePolicy = new PolicyDocument({
      statements: [
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: ['lookoutmetrics:DescribeMetricSet'],
          resources: [
            l4mAnomalyDetectorArn,
            l4mDetectorMetricSetArn
          ]
        }),
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: [
            's3:ListBucket',
            //'s3:GetBucketLocation'
          ],
          resources: [s3BucketArn]
        }),
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: [
            's3:PutObject',
            's3:GetObject'
          ],
          resources: [
            s3BucketArn + '/anomalyResults/dimensionContributions/*',
            s3BucketArn + '/anomalyResults/metricValueAnomalyScore/*'
          ]
        })
      ]
    });

    const lambdaExecutionRole = new Role(this, 'lambdaExecutionRole', {
      assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
      inlinePolicies: {lambdaExecutionRolePolicy},
      managedPolicies: [
        ManagedPolicy.fromAwsManagedPolicyName("service-role/AWSLambdaBasicExecutionRole"),
      ]
    });
    
    // lambda function definition. Note that it assumes the python 3.9 runtime.
    const lambdaFunction = new Function(this, 'lambdaFunction', {
      role: lambdaExecutionRole,
      runtime: Runtime.PYTHON_3_9,
      memorySize: lambdaMemorySize,
      timeout: Duration.seconds(lambdaDuration),
      handler: lambdaHandlerName,
      code: Code.fromAsset(join(__dirname, lambdaRelativePath)),
      layers: [pandasLayer],
      tracing: Tracing.ACTIVE
    });

    // Policy that will allow the L4M alert to invoke the lambda function.
    const lambdaAlertRolePolicy = new PolicyDocument({
      statements: [
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: ['lambda:InvokeFunction'],
          resources: [lambdaFunction.functionArn]
        })
      ]
    });

    const lambdaAlertRole = new Role(this, 'lambdaAlertRole', {
      assumedBy: new ServicePrincipal('lookoutmetrics.amazonaws.com'),
      inlinePolicies: {lambdaAlertRolePolicy}
    });

    // Create the L4M alert as an L1 construct, attaching it to the detector,
    // defining the lambda to be called, and assigning the role needed to execute it.
    const lamdaAlert = new CfnAlert(this, 'lamdaAlert', {
      action: {
        lambdaConfiguration: {
          lambdaArn: lambdaFunction.functionArn,
          roleArn: lambdaAlertRole.roleArn
        }
      },
      alertSensitivityThreshold: 70,
      anomalyDetectorArn: l4mAnomalyDetectorArn
    });
  }
}
