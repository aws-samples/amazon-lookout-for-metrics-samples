# Amazon Lookout for Metrics Cheat Sheet!

This file should contain everything you need to get a working understanding of where Lookout for Metrics makes sense, how to frame problems for the service, and where to go for more information. The goal is that every answer is in plain English and if something is not covered here, please open an issue here so we can fix it!

## Is Lookout for Metrics a Good Fit?

Amazon Lookout for Metrics is a great platform for general purpose anomaly detection for time series datasets, that encompasses a lot, but there are a number of caveats and they are explained below:

|Good Fit    |Bad Fit    |
|---    |---    |
| Providing quick responses to shifts in KPIs for your business.    | Providing quick responses on specific users' behavior.    |
| Identifying when levels plummet or spike outside of norms.    | Identifying anomalies when data does not arrive.    |
| Identifying anomalies in structured CSV or JSONlines files from S3 based on timestamps.    | Detecting anomalies in free form text log files.    |
| Identifying anomalies in 5 min, 10 min, 1 hour, and 1 day intervals.    | Identifying anomalies on custom intervals.    |


## Minimum Suggested Data Volume:

Unlike other AI services within AWS you can get started with 0 data points with Lookout for Metrics, that does not mean that you can detect anomalies immediately, or that your model will be incredibly performant but that you can build a solution and it will grow and improve over time as data collects.

That said if you start with no information the service will cold start for various periods ranging from 14 for daily to 300 for smaller intervals. As your detector collects more data, the addition will be used to retrain your models improving them more and more over time. 

## Use Cases Explained 

**What Kind of Use Cases Can Be Solved, and How?**

All use cases that are solved by Lookout for Metrics start by being grounded in a consistent flow of time series information. For example if you would like to know when there is an anomaly of traffic from a specific soure your dataset might look like this:

|timestamp    | traffic_source   | traffic_volume   |
|---    |---    | ---    |
|03/03/2021 10:00:00    | stream1    | 1000    |
|03/03/2021 10:00:00    | stream2    | 1000    |
|03/03/2021 11:00:00    | stream1    | 1005    |
|03/03/2021 11:00:00    | stream2    | 999    |


**What About Data Aggregation?**

Lookout for Metrics will automatically aggregate over multiple files and timestamps so if your values are spread over multiple files, the aggregation function you select(Sum or Average) will be applied automatically over that content. Additionally if you provide multiple entries per minute for example, then choose to aggregate them for hourly detection, the service will grab all of the relevant values for that metric and combine them for you.

