import os
import math
import random
import itertools
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import shutil
import pandas as pd


dataset_name = "ecommerce"

frequency = "1H"
dimensions = { "platform" : [ "pc_web", "mobile_web", "mobile_app" ], "marketplace" : [ "us", "uk", "de", "fr", "es", "it", "jp" ] }
metrics = [ "views", "revenue" ]
start = date.today() + relativedelta(months=-9)
end = date.today() + relativedelta(months=+3)
period = (datetime.datetime(start.year, start.month, start.day), datetime.datetime(end.year, end.month, end.day))

daily_peak_size_range = ( 200, 400 )
daily_peak_time = ( 12 * 60, 21 * 60 )
daily_offset_range = ( 100, 200 )

random_factor_size_range = (2, 10)

anomaly_size_range = ( 100, 600 )
anomaly_length_range = ( 1, 5 * 60 )
anomaly_possibility = 0.005

introduce_metric_from_upstream = [
    lambda x : max( int(x), 0 ),    # sin curve -> views 
    lambda x : x * 0.3,             # views -> revenue
]

random.seed(1234)

class DailyPattern:
    
    def __init__( self ):
        self.peak_size = random.uniform( *daily_peak_size_range )
        self.peak_time = random.uniform( *daily_peak_time )
        self.offset = random.uniform( *daily_offset_range )
    
    def get( self, t ):
        
        minutes_in_day = t.hour * 60 + t.minute
        
        factor1 = math.cos( (( minutes_in_day - self.peak_time ) / ( 24 * 60 )) * 2 * math.pi ) * self.peak_size + self.peak_size + self.offset
        
        return factor1

class RandomFactor:
    
    def __init__( self ):
        self.size = random.uniform( *random_factor_size_range )

    def get(self):
        return random.uniform( -self.size, self.size )


class Anomaly:
    
    def __init__(self):
        self.remaining_time = random.randint( *anomaly_length_range )
        self.offset = random.uniform( *anomaly_size_range ) * (random.randint(0,1)*2-1)
        #print( self.offset )

    def proceed_time(self):
        self.remaining_time -= pd.to_timedelta(frequency).seconds / 60
        return self.remaining_time <= 0

    def get(self):
        return self.offset

class Item:

    def __init__( self, dimension ):
        
        #print( dimension )
        
        self.dimension = dimension
        
        self.daily_pattern = DailyPattern()
        self.random_factor = RandomFactor()
        self.anomaly = None
    
    def get( self, t ):
    
        if random.random() < anomaly_possibility:
            self.anomaly = Anomaly()
        
        value = self.daily_pattern.get(t)
        
        value += self.random_factor.get()

        is_anomaly = bool(self.anomaly)
        if self.anomaly:
            value += self.anomaly.get()
            if self.anomaly.proceed_time():
                self.anomaly = None
        
        metric_values = []
        for i, metric in enumerate(metrics):
            value = introduce_metric_from_upstream[i](value)
            metric_values.append(value)
        
        return metric_values, is_anomaly


def synthesize():

    # create item list
    item_list = []
    for dimension_values in itertools.product( *dimensions.values() ):
        item = Item( dict( zip( dimensions.keys(), dimension_values ) ) )
        item_list.append(item)
    
    # itereate and prepare data    
    dimension_values_list = []
    for i in range( len(dimensions) ):
        dimension_values_list.append([])

    timestamp_list = []

    metric_values_list = []
    for i, metric in enumerate(metrics):
        metric_values_list.append([])

    labels_list = []
    for i, metric in enumerate(metrics):
        labels_list.append([])
    
    t = period[0]
    while t<period[1]:
        
        #print(t)

        for item in item_list:
            
            for i, d in enumerate(item.dimension.values()):
                #print(i,d)
                dimension_values_list[i].append(d)
            
            timestamp_list.append(t)
            
            metric_values, is_anomaly = item.get(t)
            for i, metric_value in enumerate(metric_values):
                metric_values_list[i].append(metric_value)
                labels_list[i].append( int(is_anomaly) )

        t += pd.to_timedelta(frequency)
        
    # convert to DataFrame
    data = {}
    for dimension_name, dimension_values in zip( dimensions.keys(), dimension_values_list ):
        data[dimension_name] = dimension_values
    data["timestamp"] = timestamp_list
    for metric_name, metric_values in zip( metrics, metric_values_list ):
        data[metric_name] = metric_values
    for metric_name, labels in zip( metrics, labels_list ):
        data[metric_name + "_label"] = labels    
    df = pd.DataFrame(data)
    return df


def splot_into_intervals( df, output_dirname ):

    for timestamp, df_single_timestamp in df.groupby("timestamp"):        
        dirname = os.path.join( output_dirname, timestamp.strftime( "%Y%m%d/%H%M" ) )
        filename = os.path.join( dirname, timestamp.strftime("%Y%m%d_%H%M%S.csv") )

        if not os.path.exists(dirname):
            os.makedirs( dirname )
        
        df_single_timestamp.to_csv( filename, index=False, date_format="%Y-%m-%d %H:%M:%S" )


def generate_data():
    df_full = synthesize()
    # Get rid of old files:
    dir_path = './data'
    try:
       shutil.rmtree(dir_path, ignore_errors=False, onerror=None)
    except:
       print('Error while deleting directory')

    # Create new ones:
    if not os.path.exists( "./data/%s/backtest" % dataset_name ):
        os.makedirs( "./data/%s/backtest" % dataset_name )
    if not os.path.exists( "./data/%s/live" % dataset_name ):
        os.makedirs( "./data/%s/live" % dataset_name )

    df_full.to_csv( "./data/%s/label.csv" % dataset_name, index=False )
    label_colunn_names = [ metric_name + "_label" for metric_name in metrics ]
    df_input = df_full.drop( columns = label_colunn_names )
    df_input.to_csv( "./data/%s/backtest/input.csv" % dataset_name, index=False )

    splot_into_intervals( df_input, "./data/%s/live" % dataset_name )