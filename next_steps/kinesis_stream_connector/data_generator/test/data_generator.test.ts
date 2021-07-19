import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as DataGenerator from '../stack/data_generator_stack';

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new DataGenerator.DataGeneratorStack(app, 'MyTestStack');
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT))
});
