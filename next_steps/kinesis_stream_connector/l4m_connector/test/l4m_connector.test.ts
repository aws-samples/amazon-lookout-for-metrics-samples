import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as DataGenerator from '../lib/l4m_connector_stack';

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new DataGenerator.L4mConnectorStack(app, 'MyTestStack');
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT))
});
