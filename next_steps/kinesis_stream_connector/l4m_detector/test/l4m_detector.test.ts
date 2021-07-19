import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as L4mDetector from '../stack/l4m_detector_stack';

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new L4mDetector.L4mDetectorStack(app, 'MyTestStack');
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT))
});
