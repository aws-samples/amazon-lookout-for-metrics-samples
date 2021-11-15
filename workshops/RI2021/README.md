
# Welcome to AIM 302: Lookout for Metrics Workshop

**Duration: 120 Minutes**


## What You'll Learn Here:

1. A history of Anomaly Detection at Amazon
1. A working knowledge of the types of problems Amazon Lookout for Metrics can help solve and how to identify or curiate datasets for the service.
1. How to execute a backtesting job with your data to identify the types of anomalies that Amazon Lookout for Metrics can help you find.
1. How to view anomalies and export them for use in other tools.
1. How to create real time anomaly detection workloads and how to iteratively improve your models.
1. How to crawl your datasets with AWS Glue and to build high value datasets for use with Amazon QuickSight.
1. How to import your data and create impactful dashboards with Amazon QuickSight.
1. How to get additional assitance for any Amazon Lookout for Metrics workload or project you may be exploring.


If you're attending this workshop via an official AWS event, there will already be an environment created for you where this content has been deployed, instructions should be provided in the room for accessing this content. Please reach out to any of the presenters or other helping staff if you have questions on how to access this environment.

Otherwise you can deploy this: [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=ALFMWorkshopRI2021&templateURL=https://lookoutformetricsbucket.s3.amazonaws.com/AL4MWorkshop.yaml)


## Agenda:

1. An overview of Anomaly Detection and Amazon Lookout for Metrics
2. A review of how backtesting works 
3. Setting up your own live anomaly detection job ( and why that matters )
4. Building impactful dashboards with Glue and Quicksight.
5. What’s Next?


## Let's Start:

### An Onverview of Anomaly Detection and Amazon Lookout for Metrics:

#### What Do We Mean By Anomaly Detection?

If you've been working in Data Science or Machine Learning you may have read this interesting article: [The AI Hierarchy of Needs](https://hackernoon.com/the-ai-hierarchy-of-needs-18f111fcc007) it contains an interesting graphic: 

![AI Hierarchy of Needs Graphic](static/imgs/data-science-hierarchy-of-needs.png)

In this chart you see a few levels: collect, move/store, explore/transform, aggregate/label, learn/optimize; with collect as the foundation and learn/optimize as the peak. Here you'll notice in explore/transform that Anomaly Detection is listed as one of these components. For the rest of this workshop this is NOT what we mean by Anomaly Detection. In the heirarchy of needs you would be focused on cleansing your dataset to create a performant model based on your collected data. Here we are seeking to build models based on operational data and to simply identify anomalies within that data in order to alert key stakeholders, not specifically to pipeline cleansed data to a new process. Similar use cases, but a little different. 

#### What Is an Anomaly?


**An anomaly is an observation that diverges from otherwise well-structured or patterned data**

Anomalies in time series data can come in a few formats such as:

1. Shifts in expected values: ![shows a spiky data point over a period of time](static/imgs/shifts_in_time_series.png)
1. Breaks in periodicity: ![shows a discontinuous time series](static/imgs/breaks-in-periodicity.png)
1. Unclassifiable data points: ![shows a binary classification problem with failures](static/imgs/unclassifiable-data-points.png)

Amazon Lookout for Metrics focuses on: **SHIFTS IN EXPECTED VALUES**. This is key for being successful with the service, you may want to explore more rule based options for breaks or alternative modeling approaches for unclassifiable data points.


### An Overview of Anomaly Detection

![A few key areas where Amazon has used Anomaly Detection explained below](static/imgs/anomaly-detection-at-Amazon.png)

At Amazon, Anomaly Detection has been crucial to many key workloads including:

1. Product Analytics - Understanding the performance of millions of products sold on Amazon.com in over 180 countries.
1. Performance of Ads - Monitoring billions of impressions a day on millions of sponsored products. 
1. Customer Experience - Hundreds of millions of customers log onto multiple devices and software versions to visit Amazon.com every month.
1. Database Monitoring - Tracking several hundred million DynamoDB metrics each day over thousands of hosts. 

Monitoring large amounts of data accross businesses with Machine Learning enables Amazon to stay ahead of issues and to constantly deliver a great customer experience. With this expertise many teams at Amazon look to learn best practices and what works from each other, this iteration drives further innovation and occasionally will lead to a new service launch( F O R E S H A D O W I N G).

A rough timeline of Anomaly Detection at Amazon is as follows:

* 1995 - BI and data analytics dashboards were created, then later static rules and thresholds were created to enable rule based alerts.
* 2007 - Building custom machine learning models started
* 2015 - Integration of anomaly detection inside our analytics platforms, usage of deep learning for Anomaly Detection, and creation of Human in the Loop(HITL) algorithms
* 2019 - Grouping and causality algorithms were developed and tested

This experimentation and development gave rise to a few key learnigns on Anomaly Detection:

![Our learnings on Anomaly Detection, iterated below](static/imgs/our-learnings.png)

Namely, Machine Learning based techniques perform well, but need to solve multiple complex problems in order to be useful.

Furthermore:

* Customer data is unique and one single anomaly detection algorithm or approach will not fit all data types
* Generating actionable results by learning relationships across customer metrics is critical to faster remediation
* Being able to dynamically adapt to changing business cycles and seasonal trends helps reduce false alerts, resulting in improved accuracy
* Building accurate and effective anomaly detection requires ML experts

All of those points are what helped navigate our development as we built and launched Amazon Lookout for Metrics. 


### An Overview of Amazon Lookout for Metrics

Amazon Lookout for Metrics Amazon Lookout for Metrics is a new service that detects outliers in your time-series data, determines their root causes, and enables you to quickly take action. Built from the same technology used by Amazon.com, Amazon Lookout for Metrics reﬂects 20 years of expertise in outlier detection and machine learning.

With Amazon Lookout for Metrics, you can build highly-accurate, machine learning models (called Detectors) to ﬁnd outliers in your data, without any machine learning expertise. Amazon Lookout for Metrics detects outliers on live or real-time data. If you have historical data, Amazon Lookout for Metrics will use it to train a model which will then detect outliers on live data. If you do not have historical data then Amazon Lookout for Metrics will train a model on-the-go. Using the Amazon Lookout for Metrics console or SDK, you simply provide Amazon Lookout for Metrics with the location and scope of your data. This includes the Measures, which are the variables that you want to investigate (like revenue), and dimensions, which are the categorical variables that correspond to a measure (revenue can have dimensions such region and product category). Amazon Lookout for Metrics then automatically chooses the best machine learning algorithm to optimize performance for your outlier detection use case and begins training a detector. Amazon Lookout for Metrics uses this custom-trained detector to monitor your chosen metrics for outliers, allowing you to quickly identify and resolve issues that are likely to impact your business. Amazon Lookout for Metrics can also integrate with Amazon SNS to alert you when the service detects important outliers.


### A Review of How Backtesting Works

### Setting Up Your Own Live Anomaly Detector

### Building Impactful Dashboards with Glue and Quicksight

### What’s Next


## Todos
- Port get anomalies script to lambda
- Port lambda to CF template
- Combine ec2 bootstrapping with lambda CF
- Validate EE support
- Document how to create dashboards
- Validate EE Support of dashboards
- Cut screenshots and document
- Port PPTX content into docs as well.
- LOTS OF DRY RUNS