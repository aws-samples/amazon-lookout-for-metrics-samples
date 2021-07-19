# Amazon Lookout for Metrics

Amazon Lookout for Metrics is a new service that detects outliers in your time-series data, determines their root causes, and
enables you to quickly take action. Built from the same technology used by Amazon.com, Amazon Lookout for Metrics reﬂects
20 years of expertise in outlier detection and machine learning.

## First Steps:

Your first stop should be this folder: [getting_started/](getting_started/) it includes:

1. A detailed overview of Lookout for Metrics' capabilities and concepts. 
1. A sample dataset to use to understand the service.
1. Walkthroughs for the console and Jupyter notebooks for interacting with the service.
1. A CloudFormation template for deploying all resources into a SageMaker Notebook Instance to explore the material in your own account.

If you have a specific question, check out the [Cheat Sheet](LookoutForMetricsCheatSheet.md). If you still have a question or encounter an error, please open and issue in this repository so we can address it!

## What Next?

The [next_steps/](next_steps/) directory houses additional resources for learning more about Lookout for Metrics. 

**Available Now:**

1. Human Readable Alerts - [next_steps/readable_alerts/](next_steps/readable_alerts/) folder contains a CloudFormation template that will deploy a solution to convert JSON alert responses into human readable plain text.
1. Human Readable Alerts in HTML email - [next_steps/readable_alerts_html/](next_steps/readable_alerts_html/) folder contains a CloudFormation template that will deploy a solution to send alerts in HTML email format.
1. Cost Calculator - [next_steps/cost_calculator/](next_steps/cost_calculator/) folder contains a Jupyter Notebook that can guide you through estimating the costs of running your workload.
1. Kinesis Data Stream connector for Lookout for Metrics - [next_steps/kinesis_stream_connector/](next_steps/kinesis_stream_connector/) contains a deployable framework for mapping a Kinesis Data Stream into S3, as well as the automation to build and activate a live detector from it. 

**Coming Soon:**

1. More examples with real world datasets.
1. Integration with 3rd party solutions via API Gateway

If you are interested in something in particular, please open an Issue on this repository with the request. If you want to contribute, simply open a pull request from a fork in your account!

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

