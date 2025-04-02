import pandas as pd

INPUT_PATH = './process_data/'
OUTPUT_PATH = './output/'
JHU_FILE = INPUT_PATH + 'st_louis_city_vulnerability.csv'
EPA_FILE = INPUT_PATH + 'st_louis_city_epa_transit_jobs.csv'

# Load the data
df = pd.read_csv(JHU_FILE)

''' Calculate demographic rate variables '''
# Calculate poverty rate for each census tract
df['below_150_pct_fpl_rate'] = df['Ppl Below 150% Poverty'] / df['Population']

# Calculate rate of households without vehicles for each census tract
df['no_vehicle_rate'] = df['Households with no vehicle'] / df['Households']

# Calculate rate of residents who are BIPOC out of total population in each census tract
df['bipoc_resident_rate'] = df['BIPOC Residents'] / df['Population']

# Calculate rate of residents who are 25 years or older without a high school diploma
df['without_high_school_diploma_rate'] = df['People 25+ w/o high school diploma'] / df['Population']

''' Join to transit data '''
df_epa = pd.read_csv(EPA_FILE)
df_combined = df.merge(df_epa, on='FIPS Code', how='left')

''' Remove unused variables '''
UNUSED_COLUMNS = ['Area (in sq mi)', 
                'Population', 
                'Households',
                'Housing Units',
                'Ppl Below 150% Poverty',
                'BIPOC Residents',
                'Households with no vehicle',
                'Percent of Overcrowded Housing Units',
                'People 25+ w/o high school diploma',
                ]
df_combined = df_combined.drop(UNUSED_COLUMNS, axis=1)

''' Export CSV file '''
df_combined.to_csv(OUTPUT_PATH + 'st_louis_city_vulnerability_rates.csv')

print(df_combined.describe())