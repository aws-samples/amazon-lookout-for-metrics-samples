/*

*/
import { App } from 'aws-cdk-lib';
import { L4mDetectorRootStack } from '../lib/l4m-detector-root-stack';
import { L4mQuickSightRootStack } from '../lib/l4m-quicksight-root-stack';

const app = new App();

// Retrieve the environment parameters from cdk.json, specific to each root stack.
// Recommend accessing cdk.json only from the app level for dependency management.
const RootStackEnv = app.node.tryGetContext('detector-stack-dev');
const QuickSightStackEnv = app.node.tryGetContext('quicksight-stack-dev');

// This stack builds the detector and its alerts. Once complete
const l4mDetectorRootStack = new L4mDetectorRootStack(app, 'l4mDetectorRootStack', {
  env: RootStackEnv
});

const l4mQuickSightRootStack = new L4mQuickSightRootStack(app, 'l4mQuickSightRootStack', {
  env: QuickSightStackEnv,
  glueCatalogName: RootStackEnv.glueCatalogName,
  glueCatalogDbName: RootStackEnv.glueCatalogDbName
});
