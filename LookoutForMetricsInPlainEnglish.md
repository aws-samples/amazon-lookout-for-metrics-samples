# Amazon Lookout for Metrics in Plain English

This file should contain everything you need to get a working understanding of where Lookout for Metrics 
makes sense, how to frame problems for the service, and where to go for more information. The goal is 
that every answer is in plain English and if something is not covered here, please open an issue here 
so we can fix it!

## What Exactly Does Lookout for Metrics Do?
To quote our homepage: https://aws.amazon.com/lookout-for-metrics/ 
> Amazon Lookout for Metrics uses machine learning (ML) to automatically detect and diagnose anomalies (i.e. outliers from the norm) in business and operational data, such as a sudden dip in sales revenue or customer acquisition rates. In a couple of clicks, you can connect Amazon Lookout for Metrics to popular data stores like Amazon S3, Amazon Redshift, and Amazon Relational Database Service (RDS), as well as third-party SaaS applications, such as Salesforce, Servicenow, Zendesk, and Marketo, and start monitoring metrics that are important to your business. Amazon Lookout for Metrics automatically inspects and prepares the data from these sources to detect anomalies with greater speed and accuracy than traditional methods used for anomaly detection. You can also provide feedback on detected anomalies to tune the results and improve accuracy over time. Amazon Lookout for Metrics makes it easy to diagnose detected anomalies by grouping together anomalies that are related to the same event and sending an alert that includes a summary of the potential root cause. It also ranks anomalies in order of severity so that you can prioritize your attention to what matters the most to your business.

Which is to say, if you are interested in monitoring for anomalous changes in the values of measurements
you are recording over time, Lookout for Metrics might be able to help.

The service works by consuming data from an external source like S3 or CloudWatch, then evaluating the data for
anomalies, and then triggering alerts if any of the data points are seen as anomalous. A user can then visit the 
Lookout for Metrics console to explore the anomaly in more detail, to see the metrics historical behavior, relationships
between this anomaly and others if they were detected, and to provide feedback to the anomaly detection model on 
whether the detected anomaly was relevant or not.

## What Exactly is a Metric?
If you are going to be looking out for them, it would help to know what they are at first. Within Lookout for Metrics there are 3 components to your datasets, together they help shape your Metrics.

They are:
1. `Timestamp` - This is required, all entries in this service are required to start with a timestamp of when the remaining columns were relevant or occurred.
2. `Dimensions` - These are categorical columns, you can have up to 5 of them, keep in mind they are combined to refer to a specific entity. For example, if your domains are `location` and `repair_type` your data could look like this:

| timestamp           | location            | repair_type    |
|---------------------|---------------------|----------------|
| 01/10/2022 10:00:00 | 123 Interesting Ave | oil_change     |
| 01/10/2022 10:00:00 | 123 Interesting Ave | tire_rotation  |
| 01/10/2022 10:00:00 | 745 Interesting Ave | oil_change     |
| 01/10/2022 10:00:00 | 745 Interesting Ave | tire_rotation  |

From this dataset we have 2 dimensions(location and emergency type) and when we start to think about the total number of possible metrics(full calculation to come) we can see there are 2 distinct locations and 2 distinct repair types.

3. `Measures` - These are the numerical columns where real observable numbers are placed. These numbers are bound to a
specific unique set of domains. You can also have up to 5 of these columns. Now expanding our earlier dataset with 2 additional numerical columns of `total` and `fixed`.

| timestamp           | location            | repair_type    | total | fixed |
|---------------------|---------------------|----------------|-------|-------|
| 01/10/2022 10:00:00 | 123 Interesting Ave | oil_change     | 10    | 8     |
| 01/10/2022 10:00:00 | 123 Interesting Ave | tire_rotation  | 10    | 10    |
| 01/10/2022 10:00:00 | 745 Interesting Ave | oil_change     | 10    | 10    |
| 01/10/2022 10:00:00 | 745 Interesting Ave | tire_rotation  | 10    | 7     |

Lookout for Metrics with this dataset has 8 metrics. How did we get this number? 

**A `Metric` is a unique combination of categorical entries and 1 numerical value.**
### How to Calculate the Total Number of Metrics

The formula to calculate the total number of metrics is: Unique(domain1) * Unique(domain2) * Number of measures. So in 
this case that would be:

2 * 2 * 2 or 8.

At present Lookout for Metrics can support a maximum of 50,000 metrics per Detector, which is the trained model assigned 
to a particular set of data. So if you wanted to track more of them than 50,000, you would simply segment your data into multiple Detectors.

## What Kinds of Problems Can Lookout for Metrics Solve?
As stated above, Lookout for Metrics is a general purpose anomaly detection tool for time-series data. This means
all problems that it can solve are going to start by relying on time-series data. To be more precise, if it is about
understanding behavior over time, Lookout for Metrics can help, if it is about specific behavior events then Lookout for Metrics
will not be helpful. To break this down further, read below to see what Lookout for Metrics can tell based on the data
provided to it.

### What Can Lookout for Metrics Tell Me From My Data
Like all great things powered by Machine Learning: It depends!

### Structure Impacts Anomalies
Specifically here it depends on how your data is structured and how your data is aggregated. Structure applies to the 
way we shape a dataset in determining the number of domains and the number of measures provided. For example the same dataset as earlier:

| timestamp           | location            | repair_type    | total | fixed |
|---------------------|---------------------|----------------|-------|-------|
| 01/10/2022 10:00:00 | 123 Interesting Ave | oil_change     | 10    | 8     |
| 01/10/2022 10:00:00 | 123 Interesting Ave | tire_rotation  | 10    | 10    |
| 01/10/2022 10:00:00 | 745 Interesting Ave | oil_change     | 10    | 10    |
| 01/10/2022 10:00:00 | 745 Interesting Ave | tire_rotation  | 10    | 7     |

This would identify the following types of issues:
1. If the `total` number of `oil_change` type events at `123 Interesting Ave` is anomalous
2. If the `total` number of `tire_rotation` type events at `123 Interesting Ave` is anomalous
3. If the `fixed` number of `oil_change` type events at `123 Interesting Ave` is anomalous
4. If the `fixed` number of `tire_rotation` type events at `123 Interesting Ave` is anomalous
5. If the `total` number of `oil_change` type events at `745 Interesting Ave` is anomalous
6. If the `total` number of `tire_rotation` type events at `745 Interesting Ave` is anomalous
7. If the `fixed` number of `oil_change` type events at `745 Interesting Ave` is anomalous
8. If the `fixed` number of `tire_rotation` type events at `745 Interesting Ave` is anomalous

That's 8 different things, mapping to the 8 metrics identified earlier. Additionally, with the causation features, IF
there was a relationship defined by patterns in the data for the values between
the `total` and `fixed` columns of a particular `location` and `repair_type` then we could report how one anomaly 
may impact the other. Also, if there were a pattern between locations, those anomalies
could be linked in a cause and effect relationship as well. The last thing that could happen here is that anomalies that
look similar in the same time period could be groups together and shown as on the page
at the same time.

## Is Lookout for Metrics a Good Fit?
Lookout for metrics is a great platform for anomaly detection of structured time series data, 
but there are caveats, and lots of use cases that may not fit well with the service, or even at all. 

| Good Fit                                                                 | Bad Fit                                                                                         |
|--------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| Identifying anomalies in KPIs for your business or application.          | Identifying anomalies on a specific user's behavior.                                            |
| Identifying when supply or demand levels spike or drop outside of norms. | Detecting when data does not arrive.                                                            |
| Determining anomalies in structured CSV or JSONLines files.              | Detecting anomalies in log files.                                                               |
| Checking for anomalies at 5min, 10min, 1hour, and 1day intervals.        | Checking for anomalies more frequently, or less frequently than  the previous specified values. |

## What Kinds of Problems Can Lookout for Metrics Solve?
As stated above, Lookout for Metrics is a general purpose anomaly detection tool for time-series data. This means
all problems that it can solve are going to start by relying on time-series data. To be more precise, if it is about
understanding behavior over time, Lookout for Metrics can help, if it is about specific behavior events then Lookout for Metrics
will not be helpful.

Keep in mind the earlier list of issues that could be identified based on the dataset, create a sample list based
on the dimensions and measures provided and you can begin to reason about what kinds of anomalies will be present, and how those 
can be helpful to identify.

### Use Case Examples

#### Retail
| Timestamp           | Location          | Department  | Loyalty Points | Sales |
|---------------------|-------------------|-------------|----------------|-------|
| 2020-11-13 23:45:00 | 602 North Ave     | Home Goods  | 325            | 16    |
| 2020-11-13 23:45:00 | 602 North Ave     | Electronics | 4715           | 2400  |
| 2020-11-13 23:50:00 | 208 Martin Street | Apparel     | 208            | 12    |

*Dimensions* - Location, Department: Informs the specific address and section of a retail store's source of information.

*Measures* - Loyalty Points, Sales: Provides the observed value of how many loyalty points were earned as well as the total
volume of revenue at the time. This could also refer to the volume of orders, or you could even add it as another measure.

*Anomalies* - Based on this dataset you could quickly identify issues in how many points are being earned by each
location and department combination as well as the sales volume there as well. If orders dropped, or if loyalty points shifted in some
way you could be alerted of this issue.

#### Advertising and Marketing
| Timestamp           | Ad-Platform | Asset                | Impressions | ClickThrough |
|---------------------|-------------|----------------------|-------------|--------------|
| 2020-11-13 23:45:00 | AdWords     | Dogshoes.com         | 400000      | .9           |
| 2020-11-13 23:45:00 | AdWords     | BagelDelivery.io     | 470000      | .12          |
| 2020-11-13 23:50:00 | Facebook    | MediaStreaming.co.uk | 512000      | .23          |

*Dimensions* - Ad-Platform, Asset: This is specifying the advertising network as well as 
the specific property or website being monitored.

*Measures* - Impressions, ClickThrough: Provides the total number of views or impressions along with the click through rate
being observed at each interval.

*Anomalies* - Based on this dataset you could quickly identify issues like impressions shifting from interval to interval, or 
if the click through rate has spiked or dipped. Also, you can see how one anomaly impacts another if they are dependent
in some way.

#### Gaming
| Timestamp           | Game          | Platform | Active Users | In-App Purchases |
|---------------------|---------------|----------|--------------|------------------|
| 2020-11-13 23:45:00 | Resident Good | PC       | 10000        | 4500             |
| 2020-11-13 23:45:00 | RoboticBlocks | iOS      | 62300        | 2400             |
| 2020-11-13 23:50:00 | 4-D Chess     | iOS      | 2            | 8                |

*Dimensions* - Game, Platform: Identifies the game and gaming platform for the observed values in measures.

*Measures* - Active Users, In-App Purchases: Provides the number of users playing during an interval, along with the number
of purchases made within each title.

*Anomalies* - Based on this dataset you could quickly identify issues in player activity if the number of active users shifts. Also
the volume of In-App purchases can be monitored. You can also see if one anomaly that is identified starts to impact others.

#### Telco
| Timestamp           | Sector | Tower | usage_per_subscriber | latency |
|---------------------|--------|-------|----------------------|---------|
| 2020-11-13 23:45:00 | NW-42  | 2     | 700                  | 1635    |
| 2020-11-13 23:45:00 | NW-42  | 3     | 1231                 | 2400    |
| 2020-11-13 23:50:00 | SE-10  | 5     | 208                  | 12      |

*Dimensions* - Sector, Tower: Identifies the region or sector as well as the tower for the measurements.

*Measures* - usage_per_subscriber, latency: Provides the total usage for all subscribers and the latency at a specific union of dimensions.

*Anomalies* - Based on this dataset you could quickly identify issues where network usage could swing, or any sudden
changes in latency.

## How Do I Configure Lookout for Metrics To Solve a Problem?
1. Start by identifying the entities that you wish to monitor for anomalies, then look for your source of time-series
data that has your historic values and where you will collect future ones. 
2. Build a simple table like the ones above that point out the timestamp, dimension, and measure values.
3. Identify what the shifts in the metrics can tell you, and that it meets your use case.
4. Build a pipeline from this datasource into Lookout for Metrics, this can be via custom automation, the Custom Connectors solution below, or simply reading an existing table in your database.
5. Activate a detector inside Lookout for Metrics.
6. Attach a dataset to Lookout for Metrics.
7. Activate the Detector.
8. Bonus - Configure Alerts.

## How Do I Understand the Results from Lookout for Metrics?
Lookout for Metrics examines data in your specified interval to look for and detect anomalies within that time period. Anomalies that look very similar in that they are impacting the same measures will be grouped together and listed in the console as a singular anomaly, however it will contain all the time series that were impacted.Using this approach the console can show you over how many dimensions an anomaly occured, as well as by what percentage it occurred. For example it could show you that only 2 geographic regions are reporting an issue, and the percentage that each of them are impacted. Lastly the service may detect a correlation between one metric's anomaly and another, if this occurs the service will show them as a cause-effect relationship in the details of the anomaly as well.

## Resources
1. [Getting Started Guide](https://github.com/aws-samples/amazon-lookout-for-metrics-samples/tree/main/getting_started) - After reading this doc and the getting started guide, you'll know how to work with Lookout for Metrics from end to end.
2. [Cost Calculator](https://github.com/aws-samples/amazon-lookout-for-metrics-samples/blob/main/next_steps/cost_calculator/) - Run this notebook to instantly calculate the monthly cost for your dataset. There's also a spreadhsheet there if you prefer that approach.
3. [Re:Invent 2021 Workshop](https://github.com/aws-samples/amazon-lookout-for-metrics-samples/tree/main/workshops/RI2021) - Getting started and how to push anomalies into custom dashboards.
4. [Custom Connectors](https://github.com/aws-samples/amazon-lookout-for-metrics-custom-connectors) - A simple way to provide complex data from your database into Lookout for Metrics.