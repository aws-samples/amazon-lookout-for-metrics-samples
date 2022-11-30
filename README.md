# Amazon Lookout for Metrics
Amazon Lookout for Metrics is a new service that detects outliers in your time-series data, helps determine their root causes, and
enables you to quickly take action. Built from the same technology used by Amazon.com, Amazon Lookout for Metrics reﬂects
20 years of expertise in outlier detection and machine learning.

## First Steps
Before going any further please read our guide [Lookout for Metrics in Plain English](LookoutForMetricsInPlainEnglish.md). This should guide you through all the core concepts that you need to understand to make the best use of the service. From there you are ready to move onto our hands on training material in the [getting_started/](getting_started/) folder, it includes:

1. A detailed overview of Lookout for Metrics' capabilities and concepts. 
1. A sample dataset to use to understand the service.
1. Walkthroughs for the console and Jupyter notebooks for interacting with the service.
1. A CloudFormation template for deploying all resources into a SageMaker Notebook Instance to explore the material in your own account.

## What Next?
If you've worked through the content above, you definitely have a grasp of what kinds of problems Lookout for Metrics can help tackle, and how to configure a dataset for your own use cases. The next step is to actually build that dataset so that you can determine the pricing for using Lookout for Metrics as well as enabling you to run a backtesting job that will showcase the performance of Lookout for Metrics for your use case.

### Dataset Design and Pricing
To help you sanity check your assumptions and to better understand your costs for using Lookout for Metrics, open [next_steps/cost_calculator/AmazonLookoutForMetricsPricingCalculatorWorkbook.xlsx](next_steps/cost_calculator/AmazonLookoutForMetricsPricingCalculatorWorkbook.xlsx). Or if you prefer to operate inside a Jupyter environment you can use [next_steps/cost_calculator/CostCalculator.ipynb](next_steps/cost_calculator/CostCalculator.ipynb)


### Validating with Backtesting
The next step would be to explore a dataset with the service via a backtesting job and prove the validity of your use case. That can be accomplished once you build your initial CSV or JSONLines file and following along with the initial guides you already used in [getting_started/BacktestingWithTheConsole.md](getting_started/BacktestingWithTheConsole.md).

After completing this process, you will see anomalies that were detected in the most recent 30% of the historical data you provided. These will tell you exactly what kind of information you can expect Lookout for Metrics to provide you with in the future. If these look promising you are well on your way to deploying an anomaly detection system on your live data!

## The Journey to Continuous Anomaly Detection

Some of the hardest parts are already behind you, you have created a dataset that reflects your history, and you've shown what kinds of anomalies the service is likely to find and now you need to configure this process so that it is totally automated going forward. The content below will cover a range of options for getting your data into the service.

### Simplest First
With Lookout for Metrics, if your data exists in a simple table inside an RDS database, or if you are using CloudWatch, you can simply create a new detector with the relevant connector via the console and you are all set. For more information on this option, take a look at our official docs: https://docs.aws.amazon.com/lookoutmetrics/latest/dev/lookoutmetrics-services.html.

### What If Things are More Complicated?

For all more complicated approaches, the workflow is:

1. Define the interval for performing anomaly detection.
2. At the same interval, schedule an ETL process to deliver the latest data for Lookout for Metrics.
3. Define an export folder structure for the ETL using timestamps in the folders for S3 so that Lookout for Metrics can access the content.
4. Determine how long this ETL process takes to complete.
5. Setup the detector, make sure to pad additional time for your ETL workflow to complete into the `Offset` parameter of your detector when creating it.

#### Totally Custom S3 Files:
The official documentation provides a decent getting started guide using S3, https://docs.aws.amazon.com/lookoutmetrics/latest/dev/services-s3.html. You can also examine the folder structure provided in the folder `ecommerce/live/` if you extract [getting_started/data/ecommerce.zip](getting_started/data/ecommerce.zip). This will show you an example of a valid folder structure for your data to be written to in order to work efficiently with Lookout for Metrics.


#### Extracting from Redshift or an RDS Database
Earlier we mentioned that if the data is in a singular table and preformatted you are ready to go, we have a project called [Custom Connectors](https://github.com/aws-samples/amazon-lookout-for-metrics-custom-connectors). You can visit the site to quickly deploy a reference implementation or checkout the code, modify a few files, and deploy a totally bespoke solution that will extract your data and write it to s3 for you, it even configures the detector as well!


#### Streaming Data Sources
Inside this repository we also have an example solution that showcases how to stream data from Kinesis into Amazon Lookout for Metrics, you can learn more at [next_steps/kinesis_stream_connector/](next_steps/kinesis_stream_connector/). It contains a deployable framework for mapping a Kinesis Data Stream into S3, as well as building your detector.

## Delivering Results
Lookout for Metrics allows you to quickly see the list of all of the anomalies that it detects inside the console, however you may want to deliver notifications to your end users based on the anomalies. To do this you use a feature called Alerts, it allows you to deliver a message to SNS or Lambda regarding the anomaly, for full developer details check out: https://docs.aws.amazon.com/lookoutmetrics/latest/dev/detectors-alerts.html. You may want to clean up the JSON that Lookout for Metrics delivers before your users see it. We have two sample projects below to help with this:

1. Human Readable Alerts(Plaintext)- [next_steps/readable_alerts/](next_steps/readable_alerts/) folder contains a CloudFormation template that will deploy a solution to convert JSON alert responses into human readable plain text.
1. Human Readable Alerts in HTML(Richly formatted) - [next_steps/readable_alerts_html/](next_steps/readable_alerts_html/) folder contains a CloudFormation template that will deploy a solution to send alerts in HTML email format.

Additionally you may want to surface the results of all the anomalies into another dashboarding system, we have an example in our workshop below that ports your findings to QuickSight.

## Visualize Anomaly Results Using Amazon QuickSight
One of the challenges encountered by teams using Amazon lookout for Metrics is quickly and efficiently connecting it to data visualization. The anomalies are presented as individuals in the console, each with their own graph, making it difficult to view the set as a whole. An automated, integrated solution is needed for deeper analysis. The [next_steps/l4m2quicksight/](next_steps/l4m2quicksight/) folder contains the CloudFormation-based instructions related to the corresponding blog post, providing an example for connecting Lookout for Metrics output to Amazon QuickSight. An AWS CDK-based version of the instructions is also provided in the [next_steps/l4m2quicksight-cdk/](next_steps/l4m2quicksight-cdk/) folder.

## Workshops

The most up to date Workshop for Lookout for Metrics is workshops/RI2021/](workshops/RI2021/) it contains a CloudFormation template taht will deploy a full demo pipeline with Amazon Lookout for Metrics showcasing backtesting results and how to orchestrate ML Ops with Step Functions. Also instructions provided to support visualizing results with Quicksight.

## Issues, Requests, Questions, or Contributions:
If you are interested in something in particular, please open an Issue on this repository with the request. If you want to contribute, simply open a pull request from a fork in your account!

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

