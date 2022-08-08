/*
https://docs.aws.amazon.com/quicksight/latest/user/create-a-data-set-existing.html

Creates a QuickSight Data Source using Athena to query the previously created AWS 
Glue Data Catalog.
*/
import { NestedStack, NestedStackProps, ScopedAws } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CfnDataSource } from 'aws-cdk-lib/aws-quicksight'

interface QuickSightDataSourceStackProps extends NestedStackProps {
  quickSightUserName: string;
  quickSightRegion: string;
}  

export class QuickSightDataSourceStack extends NestedStack {
  public readonly quickSightDataSourceArn: string;
  public readonly quickSightPrincipalArn: string;
  constructor(scope: Construct, id: string, props: QuickSightDataSourceStackProps) {
    super(scope, id, props);
 
    const {quickSightUserName, quickSightRegion} = props;
    const {accountId} = new ScopedAws(this);  
    
    this.quickSightPrincipalArn = 'arn:aws:quicksight:' + quickSightRegion + ':' + accountId + ':user/default/' + quickSightUserName;
    
    const quickSightDataSource = new CfnDataSource(this, 'quickSightDataSource', {
      awsAccountId: accountId, //Required
      dataSourceId: 'L4MQuickSightDataSourceId', //Required
      name: 'L4MQuickSightDataSource', //Required
      type: 'ATHENA', //Required
      dataSourceParameters: {
        athenaParameters: {
          workGroup: 'primary' //The default workgroup
        }
      },
      permissions: [{
        actions: [
          'quicksight:DescribeDataSource',
          'quicksight:DescribeDataSourcePermissions',
          'quicksight:UpdateDataSource',
          'quicksight:UpdateDataSourcePermissions',
          'quicksight:DeleteDataSource',
          'quicksight:PassDataSource'
        ],
        principal: this.quickSightPrincipalArn
      }]
    });

    //Export the data source ARN to be used in the data set stacks
    this.quickSightDataSourceArn = quickSightDataSource.attrArn;
  }
}
