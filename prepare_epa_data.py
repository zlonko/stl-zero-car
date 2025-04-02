import pandas as pd

DATA_PATH = './process_data/'
EPA_SLD_FILE = 'EPA_SmartLocationDatabase_V3_Jan_2021_Final.csv'
OUTPUT_FILE = 'st_louis_city_epa_transit_jobs.csv'

''' Initial data load, filter to St. Louis City, output to separate file'''
# # Load the data
# df = pd.read_csv(DATA_PATH + EPA_SLD_FILE)

# # Filter data to Missouri (STATEFP == 29)
# df = df[df['STATEFP'] == 29]

# # Filter data to St. Louis City (COUNTYFP == 510)
# df = df[df['COUNTYFP'] == 510]

# df.to_csv(DATA_PATH + 'epa_sld_jan_2021_st_louis_city.csv')

''' Load subset data '''
# FUTURE USE: Load subset data
df = pd.read_csv(DATA_PATH + 'epa_sld_jan_2021_st_louis_city.csv')

# Limit to only necessary columns
KEEP_COLUMNS = ['STATEFP', 
                'COUNTYFP', 
                'TRACTCE',
                'BLKGRPCE',
                'D5AR', # Number of jobs within 45-minute commute by car
                'D5BR', # Number of jobs within 45-minute commute by public transit
                'D4A' # meters from population weighted centroid to public transit stop
                ]
df = df[KEEP_COLUMNS]

''' Calculate variables '''
# Create FIPS Code column for join
cols = ['STATEFP', 'COUNTYFP', 'TRACTCE']
df['FIPS Code'] = df[cols].apply(lambda row: ''.join(row.values.astype(str)), axis=1)

# Clean number of jobs
df['D5AR'] = df['D5AR'].abs()
df['D5BR'] = df['D5BR'].abs()

# Sum data by census tract (TRACTCE)
# Note: D5AR, D5BR values are counts; D4A values are distances in meters
df = df.groupby(['FIPS Code']).sum()

# Calculate ratio of the number of jobs accessible by car in 45 minutes to the number of jobs accessible by transit in 45 minutes
# Ratio values > 1 indicates that more jobs are accessible by car than by public transit
# Ratio values < 1 indicates that fewer jobs are accessible by car than by public transit
df['jobs_commute_ratio_tract'] = df['D5AR'] / df['D5BR']

# Calculate the county-level average: total number of jobs commutable by car / total number of jobs commutable by transit
vehicle_jobs_sum = df['D5AR'].sum()
transit_jobs_sum = df['D5BR'].sum()
df['jobs_commute_ratio_city'] = vehicle_jobs_sum / transit_jobs_sum

# Calculate the deviation of each tract's commute mode ratio from the regional average
# Values > 1 indicate tracts where more jobs are accessible by car than by transit compared to the regional average
# Values < 1 indicate tracts where fewer jobs are accessible by car than by transite compared to the regional average
df['jobs_commute_ratio_adjusted'] = df['jobs_commute_ratio_tract'] - df['jobs_commute_ratio_city']

# Calculate quintiles for adjusted ratio
df['ratio_quantile'] = pd.qcut(df['jobs_commute_ratio_adjusted'], q=5, labels=False)

''' Clean up columns '''
# Improve column readability
df = df.rename(columns={'D4A': 'meters_to_nearest_transit_stop', 
                        'D5AR': 'number_jobs_commutable_by_vehicle_45_minutes',
                        'D5BR': 'number_jobs_commutable_by_transit_45_minutes'})
# Drop block used group identifier, no longer needed because data are at tract-level
UNUSED_COLUMNS = ['STATEFP', 'COUNTYFP', 'TRACTCE', 'BLKGRPCE']
df = df.drop(UNUSED_COLUMNS, axis=1)

''' Export CSV file '''
df.to_csv(DATA_PATH + OUTPUT_FILE)
print(df.describe())