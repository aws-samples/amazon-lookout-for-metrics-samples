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

export class QuickSightDataSet1Stack extends NestedStack {
  constructor(scope: Construct, id: string, props: QuickSightDataSourceStackProps) {
    super(scope, id, props);
 
    const {
      quickSightDataSourceArn,
      quickSightPrincipalArn,
      glueCatalogName,
      glueCatalogDbName
    } = props;
    const {accountId} = new ScopedAws(this);  
    
    const dimensionContributionsTable: CfnDataSet.PhysicalTableProperty = {
      relationalTable: {
        dataSourceArn: quickSightDataSourceArn,
        catalog: glueCatalogName,
        schema: glueCatalogDbName, //Glue Catalog DB where the tables are defined
        name: 'dimensioncontributions', //Glue catalog table name
        inputColumns: [
        //Allowed Types: STRING | INTEGER | DECIMAL | DATETIME | BIT | BOOLEAN | JSON
          {name: 'timestamp', type: 'STRING'},
          {name: 'metricname', type: 'STRING'},
          {name: 'dimensionname', type: 'STRING'},
          {name: 'dimensionvalue', type: 'STRING'},
          {name: 'valuecontribution', type: 'DECIMAL'}
        ]
      }
    };

    const dimensionContributionsLogicalTable: CfnDataSet.LogicalTableProperty = {
      alias: 'L4mDimensionContributionsTable',
      source: { physicalTableId: 'dimensionContributionsTable' },
      dataTransforms: [{
        renameColumnOperation: {
        columnName: 'timestamp',
        newColumnName: 'dimensionstimestamp'
      }}]
    };

    const anomalyScoresTable: CfnDataSet.PhysicalTableProperty = {
      relationalTable: {
        dataSourceArn: quickSightDataSourceArn,
        catalog: glueCatalogName,
        schema: glueCatalogDbName, //Glue Catalog DB where the tables are defined
        name: 'metricvalueanomalyscore', //Glue catalog table name
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

    const anomalyScoresLogicalTable: CfnDataSet.LogicalTableProperty = {
      alias: 'L4mMetricAnomalyScoresTable',
      source: { physicalTableId: 'anomalyScoresTable' },
      dataTransforms: [{
        renameColumnOperation: {
          columnName: 'timestamp',
          newColumnName: 'anomaliestimestamp'
      }}]
    };

    const joinedLogicalTable: CfnDataSet.LogicalTableProperty = {
      alias: 'L4mQuickSightMetricsAndDimensions',
      source: {
        joinInstruction: {
          leftOperand: 'dimensionContributionsLogicalTable',
          rightOperand: 'anomalyScoresLogicalTable',
          type: 'RIGHT',
          onClause: 'dimensionstimestamp = anomaliestimestamp'
        }
      },
      dataTransforms: [{
        /* Currently, this commented section generates an invalid transform error error when creating 
        the transform via code. Added a manual step to the README until this is resolved.
        createColumnsOperation: {
          columns: [{
              columnName: 'timestamp',
              columnId: 'CalculatedTimestamp',
              expression: "parseDate( dimensionstimestamp, 'yyyy-MM-dd HH:mm:ss' )"
            }]
        },
        */
        projectOperation: {
          projectedColumns: [
            'dimensionstimestamp',
            'dimensionname',
            'dimensionvalue',
            'marketplace',
            'metricname',
            'ScoreValue',
            'platform',
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
      dataSetId: 'L4MQuickSightDataSetWithDimensionContributions', //Required
      name: 'L4MQuickSightDataSetWithDimensionContributions', //Required
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
        dimensionContributionsTable,
        anomalyScoresTable
      },
      logicalTableMap: {
        dimensionContributionsLogicalTable,
        anomalyScoresLogicalTable,
        joinedLogicalTable
      }
    });
  }
}
