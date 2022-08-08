/*
https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html

Creates the AWS Glue crawler that will populate the AWS Glue Data Catalog with tables
in preparation for the Amazon QuickSight data source creation. It creates the Glue Crawler,
Database, with the access needed for S3.

Once created, the crawler must be run from the Glue console:
https://console.aws.amazon.com/glue/home?#catalog:tab=crawlers
*/
import { NestedStack, NestedStackProps, ScopedAws } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Role, ServicePrincipal, PolicyDocument, PolicyStatement, Effect, ManagedPolicy } from 'aws-cdk-lib/aws-iam';
import { CfnCrawler, CfnDatabase } from 'aws-cdk-lib/aws-glue';

interface GlueCrawlerStackProps extends NestedStackProps {
  s3BucketArn: string;
  s3BucketName: string;
  glueCatalogDbName: string;
};

export class GlueCrawlerStack extends NestedStack {
  public readonly glueDatabase: CfnDatabase;
  constructor(scope: Construct, id: string, props: GlueCrawlerStackProps) {
    super(scope, id, props);

    const {s3BucketArn, s3BucketName, glueCatalogDbName} = props; 
    const {accountId} = new ScopedAws(this);

    const glueDatabase = new CfnDatabase(this, 'gluedatabase', {
      catalogId: accountId, //Required to be specifiec in both locations
      databaseInput: {
        targetDatabase: {
          catalogId: accountId, //Required to be specifiec in both locations
          databaseName: glueCatalogDbName, //Database name is required
        }
      }
    });

    const glueCrawlerRolePolicy = new PolicyDocument({
      statements: [
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: ['s3:ListBucket'],
          resources: [s3BucketArn]
        }),
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: [
            's3:GetObject',
            's3:PutObject'
          ],
          resources: [
            `${s3BucketArn}/ecommerce/live/*`,
            `${s3BucketArn}/anomalyResults/dimensionContributions/*`,
            `${s3BucketArn}/anomalyResults/metricValueAnomalyScore/*`
          ]
        })
      ],
    });

    const glueCrawlerRole = new Role(this, 'glueCrawlerRole', {
      assumedBy: new ServicePrincipal('glue.amazonaws.com'),
      managedPolicies: [
        ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSGlueServiceRole')
      ],
      inlinePolicies: { glueCrawlerRolePolicy }
    });

    const glueCrawler = new CfnCrawler(this, 'glueCrawler', {
      role: glueCrawlerRole.roleArn,
      databaseName: glueCatalogDbName,
      targets: {
        s3Targets: [
          {path: `${s3BucketName}/ecommerce/live`},
          {path: `${s3BucketName}/anomalyResults/dimensionContributions`},
          {path: `${s3BucketName}/anomalyResults/metricValueAnomalyScore`}
        ]
      },
      schemaChangePolicy: {
        deleteBehavior: 'DEPRECATE_IN_DATABASE',
        updateBehavior: 'UPDATE_IN_DATABASE'
      }
    });
  }
}
