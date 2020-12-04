# Amazon Lookout for Metrics README.md

Amazon Lookout for Metrics(ALFM) is a new service that detects outliers in your time-series data, determines their root causes, and
enables you to quickly take action. Built from the same technology used by Amazon.com, ALFM reﬂects
20 years of expertise in outlier detection and machine learning.


With ALFM, you can build highly-accurate, machine learning models (called detectors) to ﬁnd outliers
in your data, without any machine learning expertise. ALFM detects outliers on live or real-time data. If
you have historical data, ALFM will use it to train a model which will then detect outliers on live data. If
you do not have historical data then ALFM will train a model on-the-go. Using the ALFM console or SDK,
you simply provide ALFM with the location and scope of your data. This includes the measures, which
are the variables that you want to investigate (like revenue), and dimensions, which are the categorical
variables that correspond to a measure (revenue can have dimensions such region and product category).
ALFM then automatically chooses the best machine learning algorithm to optimize performance for
your outlier detection use case and begins training a detector. ALFM uses this custom-trained detector
to monitor your chosen metrics for outliers, allowing you to quickly identify and resolve issues that are
likely to impact your business. ALFM can also integrate with Amazon SNS to alert you when the service
detects important outliers.

This guide will walk you through the steps needed to configure local or SageMaker environment for working with Amazon Lookout For Metrics(ALFM). At the end of this guide, move on to the Jupyter notebooks to explore the service in more detail.

## Reference Architecture

ALFM is designed to primarily focus on alerting you to real-time anomalies within your data(Continuous), however there is a secondary mode for backtesting to help you explore historical items and to learn what ALFM may be able to help you react to in the future(Backtesting). Both architectures are illustrated below:

### Continous Data Architecture

![Continuous Data Arch](static/imgs/readme/ALFM-Continous(v1).png)

#### Continuous Mode:

1. Create and configure a detector: 
    1. Provide a detector name and description
    2. Select the data frequency.
2. Create and configure a dataset:
    1. Point to the S3 location of your data when using the SDK or select the `Detect` option when using the console 
    2. Configure the IAM permissions needed to access it.
    3. Select a timezone of your data
    4. Declare the measures and dimensions and map them to the appropriate fields in your data
    5. Define the timestamp format and map it to the timestamp field in your data
3. Activate Detector to kick off the training and continious detection 
4. Set up alerts and configure notification parameter to get notified when Poirot detects important outliers.
5. Inspect the detected outliers to figure out their root causes.
6. Provide feedback on the outliers to improve predictor accuracy.


### Backtesting Data Architecture

![Backtesting Data Arch](static/imgs/readme/ALFM-Backtesting(v1).png)

#### Backtesting Mode:

1. Extract backtesting data from your database and save as a CSV or JSON lines format file into an Amazon S3 bucket.
2. Create and configure a detector:
    1. Provide a detector name and description
    2. Select the data frequency.
3. Create and configure the dataset:
    1. Point to the S3 location of your backtest data when using the SDK or select `Test` option when using the console 
    2. Configure the IAM permissions needed to access the data
    3. Select the timezone of your data
    4. Declare the measures and dimensions and map them to the appropriate fields in your data
    5. Define the timestamp format and map it to the timestamp field in your data
4. Activate Detector to kick off the training and backtesting process 
5. Once the backtesting process is finished running, validate backtesting results.


## Initial Setup

You will need a working environment in which to get your data ready for ALFM, this can be done locally with Excel but many customers enjoy using Python and tools like Pandas, so here we will start by deploying a CloudFormation Template that will provision an environment for your work going forward. 

The first step is to deploy a CloudFormation template that will perform much of the initial setup for you. In another browser window login to your AWS account. Once you have done that open the link below in a new tab to start the process of deploying the items you need via CloudFormation.

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=ALFMDemo&templateURL=https://lookoutformetricsbucket.s3.amazonaws.com/LookoutForMetricsNotebookSetup.YAML)

### Cloud Formation Wizard

Start by clicking `Next` at the bottom like shown:

![StackWizard](static/imgs/readme/img1.png)

All of the default options here are fine, click next:

![StackWizard2](static/imgs/readme/img2.png)

This page is a bit longer so scroll to the bottom to click `Next`.

![StackWizard3](static/imgs/readme/img3.png)

Again scroll to the bottom, check the box to enable the template to create new IAM resources and then click `Create Stack`.

![StackWizard4](static/imgs/readme/img4.png)

For a few minutes CloudFormation will be creating the resources described above on your behalf it will look like this while it is provisioning:

![StackWizard5](static/imgs/readme/img5.png)

Once it has completed you'll see green text like below indicating that the work has been completed:

![StackWizard5](static/imgs/readme/img6.png)

Now that you have your environment created, you need to save the name of your S3 bucket for future use, you can find it by clicking on the `Outputs` tab and then looking for the resource `S3Bucket`, once you find it copy and paste it to a text file for the time being.

### Using the Notebooks

## Using the Notebooks

Start by navigating to the Amazon SageMaker landing [page](https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/). From the service page click the `Notebook Instances` link on the far left menu bar.

![StackWizard5](static/imgs/readme/img7.png)

To get to the Jupyter interface, simply click `Open JupyterLab` on the far right next to your notebook instance.

![StackWizard5](static/imgs/readme/img8.png)

Clicking the open link will take a few seconds to redirect you to the Jupyter system but once there you should see a collection of files on your left. 

To get started navigate to the first notebook you should see a folder `getting_started` in the file browser to your left, open that folder and proceed to `0.SettingUpALFMPackages.ipynb` this will setup the rest of the things needed to interact with ALFM within your SageMaker Environment. You can also follow the guide below for how to setup a local environment on MacOS that will also work with the SDK. A similar process will work for Linux or Windows installations as well.


## Paths Forward

There are afew ways to work with Amazon Lookout for Metrics(ALFM):

1. A live on demand detector for alerting when suspected anomalous events occur.
1. A backtest on historical data to determine which events would have been identified if ALFM was activated on that data stream.

Both paths are supported within this onboarding guide!

### Option 1: Live Detection

After completing `0.SettingUpALFMPackages.ipynb` you can open and run `1.GettingStartedWithALFM.ipynb` to configure a project with ALFM. After you have completed that notebook you can simulate future data using `2.GenerateDataForALFM.ipynb`. At this, point the detector will be configured for you along with synthetic data for the future and you can track the anomalies that are reported against those that you generated.


### Option 2: Back Testing

In this case we will start with a notebook to generate the dataset and upload it to s3, the rest of the tutorial will rely on you creating the resources needed within the console. You can work through that project in `3.GenerateBacktestDataForALFM.ipynb`


## Bonus: Building an Environment Locally:


### Configure Your Local Environment (Or skip this section if using SageMaker)

This is a bit more complex, for this we are going to assume you are using a computer with MacOS, the steps are generalized to be:

1. Install Xcode Tools
1. Install Homebrew
1. Install Python3
1. Install Virtualenv / VirtualenvWrapper 
1. Create a virtualenv for ALFM testing
1. Install the dependencies
1. Install the patches for ALFM

This can be swapped out to support Conda if you are more familiar or any other Python setup, I've just chosen the default stack for many developers. Also you can skip ahead to the section where you download the SDK if you are using Conday for example.

To Install XCode tools, simply open a terminal and enter:

```
xcode-select --install
```

Then just follow the prompts.

You will now want to install homebrew a package manager for MacOS that will allow you to install open source components. In a terminal enter:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```

If that does not work, consult the latest docs: https://brew.sh

Now you have brew installed it is time to install python3, to do that in your terminal enter the following:

```
brew install python3
```

This may take a few moments but it should leave you with a totally clean Python3 install. 

Now you will need to patch your terminal to leverage this version of Python. Add the following lines to your `~/.bash_profile` , `~/.bashrc`, or `~/.zshrc` depending on which file you store your settings in.

```
export PATH="/usr/local/opt/sqlite/bin:$PATH"
export PATH="/usr/local/opt/python/libexec/bin:/usr/local/sbin:$PATH"
```

Now close your terminal and open a new one. From there enter the following to install both virtualenv and virtualenv wrapper:

```
pip install virtualenv virtualenvwrapper
```

Once they have completed, open your profile file again as earlier and append the following:

```
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/local/opt/python/libexec/bin/python
source /usr/local/bin/virtualenvwrapper.sh
```

Once you have finished that step, lastly enter the following to create the directory for your environments:

```
mkdir ~/.virtualenvs
```

Now you have a clean install of Python3, virtualenv to isolate your Python environments, and virtualenvwrapper to make using them and creating them a tad easier. To validate everything is working, close your terminal and open a new one. You should see a few directories being created.

The very last step is to create a virtualenv to use for ALFM, this is helpful so that beta changes you make do not impact your broader system Python config.

In a terminal( you can change `ALFMttest` to anything you'd like):

```
mkvirtualenv ALFMttest
```

This will create a new version of Python for you, as well as activate it. In the future to resume usage of this environment in your terminal just enter:

```
workon ALFMttest
```

It would also be handy to have a working set of data science tools so enter the following to install them 

```
pip install jupyterlab numpy scipy pandas matplotlib requests
```

To run Juypyter Lab after that:

```
jupyter lab
```


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

