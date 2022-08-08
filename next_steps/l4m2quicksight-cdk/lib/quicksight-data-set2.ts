/*
*/
import { NestedStack, NestedStackProps, ScopedAws } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CfnDataSet } from 'aws-cdk-lib/aws-quicksight'

interface QuickSightDataSourceStackProps extends NestedStackProps {
  quickSightDataSourceArn: string;
  quickSightPrincipalArn: string;
  glueCatalogName: string;
  glueCatalogDbName: string;
}  

export class QuickSightDataSet2Stack extends NestedStack {
  constructor(scope: Construct, id: string, props: QuickSightDataSourceStackProps) {
    super(scope, id, props);
 
    const {
      quickSightDataSourceArn,
      quickSightPrincipalArn,
      glueCatalogName,
      glueCatalogDbName
    } = props;

    const {accountId} = new ScopedAws(this);  
    
    const quickSightLiveDataTable: CfnDataSet.PhysicalTableProperty = {
      relationalTable: {
        dataSourceArn: quickSightDataSourceArn,
        catalog: glueCatalogName,
        schema: glueCatalogDbName, //Glue Catalog DB where the tables are defined
        name: 'live', //Glue catalog table name
        inputColumns: [
        //Allowed Types: STRING | INTEGER | DECIMAL | DATETIME | BIT | BOOLEAN | JSON
          {name: 'platform', type: 'STRING'},
          {name: 'marketplace', type: 'STRING'},
          {name: 'timestamp', type: 'STRING'},
          {name: 'views', type: 'DECIMAL'},
          {name: 'revenue', type: 'DECIMAL'}
        ]
      }
    };

    const quickSightLiveDataLogicalTable: CfnDataSet.LogicalTableProperty = {
      alias: 'L4mLiveDataTable',
      source: { physicalTableId: 'quickSightLiveDataTable' },
      dataTransforms: [{
        renameColumnOperation: {
          columnName: 'timestamp',
          newColumnName: 'livedatatimestamp'
      }}]
    };

    const anomalyScoresTable: CfnDataSet.PhysicalTableProperty = {
      relationalTable: {
        dataSourceArn: quickSightDataSourceArn,
        catalog: glueCatalogName,
        schema: glueCatalogDbName, //Glue catalog DB where the tables are defined
        name: 'metricValueAnomalyScore', //Glue catalog table name
        inputColumns: [
        //Allowed Types: STRING | INTEGER | DECIMAL | DATETIME | BIT | BOOLEAN | JSON
          {name: 'key', type: 'STRING'},
          {name: 'timestamp', type: 'STRING'},
          {name: 'platform', type: 'STRING'},
          {name: 'marketplace', type: 'STRING'},
          {name: 'viewsanomalymetricvalue', type: 'DECIMAL'},
          {name: 'viewsgroupscore', type: 'DECIMAL'},
          {name: 'revenueanomalymetricvalue', type: 'DECIMAL'},
          {name: 'revenuegroupscore', type: 'DECIMAL'}
        ]
      }
    };

    const anomalyScoreLogicalTable: CfnDataSet.LogicalTableProperty = {
      alias: 'L4mMetricAnomalyScoresTable',
      source: { physicalTableId: 'anomalyScoresTable' },
      dataTransforms: [
        { renameColumnOperation: { columnName: 'timestamp', newColumnName: 'anomaliestimestamp' } },
        { renameColumnOperation: { columnName: 'marketplace', newColumnName: 'marketplaceanomalyscore' } },
        { renameColumnOperation: { columnName: 'platform', newColumnName: 'platformanomalyscore' } }
      ]
    };

    const joinedLogicalTable: CfnDataSet.LogicalTableProperty = {
      alias: 'L4mQuickSightMetricsAndLiveData',
      source: {
        joinInstruction: {
          leftOperand: 'quickSightLiveDataLogicalTable',
          rightOperand: 'anomalyScoreLogicalTable',
          type: 'LEFT',
          onClause: 'livedatatimestamp = anomaliestimestamp AND marketplace = marketplaceanomalyscore AND platform = platformanomalyscore'
        }
      },
      dataTransforms: [{
        /* Currently, this commenred section generates an invalid transform error error when creating 
        the transform via code. Added a manual step to the README until this is resolved.
        createColumnsOperation: {
          columns: [{
            columnName: 'timestamp',
            columnId: 'CalculatedTimestamp',
            expression: 'parseDate( livedatatimestamp, "yyyy-MM-dd HH:mm:ss")'
          }]
        },*/
        projectOperation: {
          projectedColumns: [
            'livedatatimestamp',
            'timestamp',
            'marketplace',
            'platform',
            'views',
            'revenue',
            'revenueanomalymetricvalue',
            'revenuegroupscore',
            'viewsanomalymetricvalue',
            'viewsgroupscore'
          ]
        }
      }]
    };

    const quickSightDataSet = new CfnDataSet(this, 'quickSightDataSet', {
      awsAccountId: accountId, //Required
      dataSetId: 'L4MQuickSightDataSetWithLiveData', //Required
      name: 'L4MQuickSightDataSetWithLiveData', //Required
      importMode: 'DIRECT_QUERY',
      permissions: [{
        principal: quickSightPrincipalArn,
        actions: [
          'quicksight:UpdateDataSetPermissions',
          'quicksight:DescribeDataSet',
          'quicksight:DescribeDataSetPermissions',
          'quicksight:PassDataSet',
          'quicksight:DescribeIngestion',
          'quicksight:ListIngestions',
          'quicksight:UpdateDataSet',
          'quicksight:DeleteDataSet',
          'quicksight:CreateIngestion',
          'quicksight:CancelIngestion'
        ]
      }],
      physicalTableMap: {
        quickSightLiveDataTable,
        anomalyScoresTable
      },
      logicalTableMap: {
        quickSightLiveDataLogicalTable,
        anomalyScoreLogicalTable,
        joinedLogicalTable
      }
    });
  }
}
