/*
*/
import { Stack, StackProps, CfnParameter } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { QuickSightDataSourceStack } from './quicksight-data-source';
import { QuickSightDataSet1Stack } from './quicksight-data-set1';
import { QuickSightDataSet2Stack } from './quicksight-data-set2';

interface L4mQuickSightRootStackProps extends StackProps {
  env: any;
  glueCatalogName: string;
  glueCatalogDbName: string;
};

export class L4mQuickSightRootStack extends Stack {
  constructor(scope: Construct, id: string, props: L4mQuickSightRootStackProps) {

    super(scope, id, props);
    const {env, glueCatalogName, glueCatalogDbName} = props;

    // Passing in the QuickSight username to be set as the principal in the data source permissions.
    // Use the cdk deploy option: '--parameters quickSightUserName=<your username>'
    // Note the username will not persist in any source code, but will be in the compiled 
    // CloudFormation Template, within the access policy principal.
    const QuickSightUserName = new CfnParameter(this, "QuickSightUserName", {
      type: "String",
      noEcho: true,
      description: "Your QuickSight username (different than your AWS account username"
    });

    const quickSightDataSource = new QuickSightDataSourceStack(this, 'quickSightDataSource', {
      quickSightUserName: QuickSightUserName.valueAsString,
      quickSightRegion: env.quickSightRegion
    });

    const quickSightDataSet1 = new QuickSightDataSet1Stack(this, 'quickSightDataSet1', {
      quickSightDataSourceArn: quickSightDataSource.quickSightDataSourceArn,
      quickSightPrincipalArn: quickSightDataSource.quickSightPrincipalArn,
      glueCatalogName: glueCatalogName,
      glueCatalogDbName: glueCatalogDbName
    });

    const quickSightDataSet2 = new QuickSightDataSet2Stack(this, 'quickSightDataSet2', {
      quickSightDataSourceArn: quickSightDataSource.quickSightDataSourceArn,
      quickSightPrincipalArn: quickSightDataSource.quickSightPrincipalArn,
      glueCatalogName: glueCatalogName,
      glueCatalogDbName: glueCatalogDbName
    });
  }
}

  