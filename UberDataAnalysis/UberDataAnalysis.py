import pandas as pd

df = pd.read_csv('uber_data.csv',header=0)
df.tail()

df['trip_id'] = df.index

#type(df['tpep_pickup_datetime'][1]) -- need to convert str to datetime
df['tpep_pickup_datetime']= pd.to_datetime(df['tpep_pickup_datetime'])
df['tpep_dropoff_datetime']= pd.to_datetime(df['tpep_dropoff_datetime'])
df['tpep_pickup_datetime']


# Missing values: Result= No missing value
missing_count= df.isnull().sum()

# drop last row as  it contains invalid trip: date not in 2016 and invalid RatecodeID
df= df[df['RatecodeID'] != 0.3]

# remove duplicate rows
df = df.drop_duplicates().reset_index(drop=True)

# Create Dimension tables as per Data Model
# Pickup_dim
pickup_dim = df[['tpep_pickup_datetime','pickup_longitude','pickup_latitude']]
pickup_dim['pickup_hour']= pickup_dim['tpep_pickup_datetime'].dt.hour
pickup_dim['pickup_minute']= pickup_dim['tpep_pickup_datetime'].dt.minute
pickup_dim['pickup_second']= pickup_dim['tpep_pickup_datetime'].dt.second
pickup_dim['pickup_month']= pickup_dim['tpep_pickup_datetime'].dt.month
pickup_dim['pickup_year']= pickup_dim['tpep_pickup_datetime'].dt.year
pickup_dim['pickup_weekday']= pickup_dim['tpep_pickup_datetime'].dt.weekday
pickup_dim['pickup_id']= pickup_dim.index
pickup_dim= pickup_dim[['pickup_id', 'tpep_pickup_datetime','pickup_longitude','pickup_latitude','pickup_hour','pickup_minute','pickup_second','pickup_month','pickup_year','pickup_weekday']]
pickup_dim.info()

# dropoff_dim
# Create Dimension tables as per Data Model
dropoff_dim = df[['tpep_dropoff_datetime','dropoff_longitude','dropoff_latitude']]
dropoff_dim['dropoff_hour']= dropoff_dim['tpep_dropoff_datetime'].dt.hour
dropoff_dim['dropoff_minute']= dropoff_dim['tpep_dropoff_datetime'].dt.minute
dropoff_dim['dropoff_second']= dropoff_dim['tpep_dropoff_datetime'].dt.second
dropoff_dim['dropoff_month']= dropoff_dim['tpep_dropoff_datetime'].dt.month
dropoff_dim['dropoff_year']= dropoff_dim['tpep_dropoff_datetime'].dt.year
dropoff_dim['dropoff_weekday']= dropoff_dim['tpep_dropoff_datetime'].dt.weekday
dropoff_dim['dropoff_id']= dropoff_dim.index
dropoff_dim= dropoff_dim[['dropoff_id', 'tpep_dropoff_datetime','dropoff_longitude','dropoff_latitude','dropoff_hour','dropoff_minute','dropoff_second','dropoff_month','dropoff_year','dropoff_weekday']]
dropoff_dim.tail()

# rate_dim
rate_code_type={1: 'Standard rate',
2:'JFK',
3:'Newark',
4:'Nassau or Westchester',
5:'Negotiated fare',
6:'Group ride'
}
rate_dim = df[['RatecodeID']]

rate_dim['rate_code_name']= rate_dim['RatecodeID'].map(rate_code_type)
rate_dim['rate_id']= rate_dim.index
rate_dim.rename(columns={"RatecodeID":"rate_code_id"}, inplace=True)
rate_dim=rate_dim[['rate_id','rate_code_id','rate_code_name']]
rate_dim.info()

#payment_dim
payment_codes={1: 'Credit card',
2: 'Cash',
3: 'No charge',
4: 'Dispute',
5: 'Unknown',
6: 'Voided trip'}
payment_dim = df[['payment_type','fare_amount','extra','mta_tax','tip_amount','tolls_amount','improvement_surcharge','total_amount']]
payment_dim.rename(columns={'payment_type':'payment_type_code'},inplace=True)
payment_dim['payment_type_name']= payment_dim['payment_type_code'].map(payment_codes)
payment_dim['payment_id']= payment_dim.index
payment_dim= payment_dim[['payment_id','payment_type_code','payment_type_name', 'fare_amount','extra','mta_tax','tip_amount','tolls_amount','improvement_surcharge','total_amount']]
payment_dim.info()

# Create Fact Table
fact_table= df.merge(pickup_dim, left_on='trip_id', right_on='pickup_id').merge(dropoff_dim, left_on='trip_id', right_on= 'dropoff_id').merge(rate_dim, left_on='trip_id', right_on= 'rate_id')            .merge(payment_dim, left_on='trip_id', right_on= 'payment_id')            [['trip_id', 'VendorID', 'pickup_id', 'dropoff_id', 'rate_id', 'payment_id', 'passenger_count', 'trip_distance', 'store_and_fwd_flag']]
fact_table.tail()

