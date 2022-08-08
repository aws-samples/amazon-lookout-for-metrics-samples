/*
https://docs.aws.amazon.com/lookoutmetrics/latest/dev/lookoutmetrics-detectors.html

Builds the Amazon Lookout for Metrics Anomaly Detector, also defining its access requirements, 
source, metrics, and dimensions.

Outputs the ARNs for the detector and metric set.
*/
import { NestedStack, NestedStackProps, ScopedAws, Fn } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Role, ServicePrincipal, PolicyDocument, PolicyStatement, Effect } from 'aws-cdk-lib/aws-iam';
import { CfnAnomalyDetector } from 'aws-cdk-lib/aws-lookoutmetrics';

interface L4mDetectorStackProps extends NestedStackProps {
  bucketArn: string,
  bucketName: string;
  bucketPrefix: string;
  detectorFrequency: string;
  metrics: string[];
  dimensions: string[];
  timestampFormat: string;
  timestampColumn: string;
};

export class L4mDetectorStack extends NestedStack {
  public readonly l4mAnomalyDetectorArn: string;
  public readonly l4mDetectorMetricSetArn: string;
  constructor(scope: Construct, id: string, props: L4mDetectorStackProps) {
    super(scope, id, props);

    const {partition, accountId, region} = new ScopedAws(this);

    const {
      bucketArn,
      bucketName,
      bucketPrefix,
      detectorFrequency,
      metrics,
      dimensions,
      timestampFormat,
      timestampColumn
    } = props;

    // S3 location for live data access for the metricSource
    const metricSourceS3PathTemplate = 's3://' + bucketName + '/' + bucketPrefix + '/{{yyyyMMdd}}/{{HHmm}}';

    // Policy to allow limited s3 actions on only the L4M bucket.
    const metricSourceRolePolicy = new PolicyDocument({
      statements: [
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: ['s3:ListBucket', 's3:GetBucketAcl'],
          resources: [bucketArn]
        }),
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: ['s3:GetObject'],
          resources: [bucketArn + '/' + bucketPrefix + '/*']
        })
      ]
    });

    // Create the role for metricSource access
    const metricSourceRole = new Role(this, "metricSourceRole", {
      assumedBy: new ServicePrincipal('lookoutmetrics.amazonaws.com'),
      inlinePolicies: {metricSourceRolePolicy}
    });

    // Define the metric source based on the S3 location and access requirements
    const metricSource: CfnAnomalyDetector.MetricSourceProperty = {
      s3SourceConfig: {
        fileFormatDescriptor: {
          csvFormatDescriptor: {
            charset: 'utf-8',
            containsHeader: true,
            delimiter: ',',
            fileCompression: 'NONE',
            quoteSymbol: '"'
          }
        },
        roleArn: metricSourceRole.roleArn,
        templatedPathList: [metricSourceS3PathTemplate]
      }
    };

    // Create an array of metric properties from the metrics array, defined in the cdk.json
    // This example presents them all as SUMs.
    const metricList: CfnAnomalyDetector.MetricProperty [] = [];
    metrics.forEach((metric: string) => {
      const metricProperty: CfnAnomalyDetector.MetricProperty = {
        metricName: metric,
        aggregationFunction: 'SUM'
      }
      metricList.push(metricProperty);
    });

     // Configure input data (s3) - dimensions, metrics, timestamp, s3 location, timezone, frequency.
    const metricSetProperty: CfnAnomalyDetector.MetricSetProperty = {
      metricSetName: 'L4MLiveDetectorMetricSet',
      metricList: metricList,
      dimensionList: dimensions, // defined in cdk.json
      metricSource: metricSource,
      metricSetFrequency: detectorFrequency, // defined in cdk.json
      timestampColumn: {
        columnFormat: timestampFormat, // defined in cdk.json
        columnName: timestampColumn // defined in cdk.json
      }
    };

    // Create the detector
    const l4mAnomalyDetector = new CfnAnomalyDetector(this, 'l4mAnomalyDetector', {
      anomalyDetectorName: 'L4MLiveDetector', // Name is required in the L1 construct
      metricSetList: [metricSetProperty],
      anomalyDetectorConfig: {
        anomalyDetectorFrequency: detectorFrequency // defined in the cdk.json
      }
    });

    this.l4mAnomalyDetectorArn = l4mAnomalyDetector.attrArn;

    // The MetricSet's ARN is not retrievable from the CDK L1 construct, so build as an explicit output
    this.l4mDetectorMetricSetArn = Fn.join('', [
      'arn:' + partition + ':lookoutmetrics:' + region + ':' + accountId,
      ':MetricSet/L4MLiveDetector/' + metricSetProperty.metricSetName
    ])
  }
}
