import pandas as pd
from itertools import product

INPUT_PATH = './process_data/'
OUTPUT_PATH = './output/'
NIBRS_FILE = INPUT_PATH + 'stlmpd_nibrs_2021-2023.csv'

# Load the data
df_input = pd.read_csv(NIBRS_FILE, dtype = "string")

# Remove columns we will not use for aggregations
UNUSED_COLUMNS = ['OccurredFromTime',
                  'Offense',
                  'IncidentTopSRS_UCR',
                  'IncidentLocation',
                  'IntersectionOtherLoc',
                  'FelMisdCit',
                  'NbhdNum',
                  'Latitude',
                  'Longitude',
                  'IncidentSupplemented',
                  'LastSuppDate',
                  'VictimNum',
                  'IncidentNature'
                ]
df_reduced = df_input.drop(UNUSED_COLUMNS, axis=1)

# Replace NULL SRS_UCR values with 0 to represent "Other Crimes" category
df_reduced['SRS_UCR'] = df_reduced['SRS_UCR'].fillna('9')
UCR_LABELS = {
    '1' : 'Murder & Manslaughter',
    '2' : 'Sexual Assault',
    '3' : 'Robbery',
    '4' : 'Aggravated Assault',
    '5' : 'Burglary',
    '6' : 'Theft & Larceny',
    '7' : 'Motor Vehicle Theft',
    '8' : 'Arson',
    '9' : 'Other Offenses'
}

# Drop rows where SRS_UCR is NULL
df_reduced_no_null = df_reduced.dropna(how='any',axis=0) 
df = df_reduced_no_null

# Create year and month columns for filter
df['IncidentDate'] = pd.to_datetime(df['IncidentDate'])
# Extract year (YYYY)
df['Year'] = df['IncidentDate'].dt.year
# Extract month number (MM)
df['Month'] = df['IncidentDate'].dt.month
# Extract month name (e.g., "January")
df['MonthName'] = df['IncidentDate'].dt.month_name()
# Extract month-year for aggregation (will drop later)
df['YearMonth'] = df['Year'].astype(str) + '-' + df['Month'].astype(str)
df['YearMonth'] = pd.to_datetime(df['YearMonth'])

# Aggregate values by Neighborhood, SRS_UCR, YearMonth, FirearmUsed
AGGREGATION_COLUMNS = ['Neighborhood',
                       'YearMonth',
                       'SRS_UCR',
                       'FirearmUsed'
                       ]
df_aggregated = df.groupby(AGGREGATION_COLUMNS).size().reset_index(name='IncidentCount')
df_aggregated = df_aggregated.sort_values(['YearMonth', 'Neighborhood'], ascending=[True, True])

# Get unique values for each variable to create complete combinations
all_neighborhoods = df['Neighborhood'].unique()
all_srs_ucr = df['SRS_UCR'].unique()
all_firearm_used = df['FirearmUsed'].unique()

# Create complete date range for all months between min and max dates
min_date = df['IncidentDate'].min()
max_date = df['IncidentDate'].max()
complete_date_range = pd.date_range(start=min_date, end=max_date, freq='MS')  # 'MS' = Month Start
all_year_months = [date.strftime('%Y-%m-01') for date in complete_date_range]

# Create reference grid with all possible combinations
complete_combinations = pd.DataFrame(
    list(product(
        all_neighborhoods,
        all_srs_ucr, 
        all_firearm_used, 
        all_year_months)),
    columns=['Neighborhood', 'SRS_UCR', 'FirearmUsed', 'YearMonth']
)

# Ensure both YearMonth columns are strings for merging
complete_combinations['YearMonth'] = complete_combinations['YearMonth'].astype(str)
df_aggregated['YearMonth'] = df_aggregated['YearMonth'].astype(str)

# Merge with aggregated data, filling missing values with 0
df_complete = complete_combinations.merge(
    df_aggregated, 
    on=['Neighborhood', 'SRS_UCR', 'FirearmUsed', 'YearMonth'],
    how='left',
    indicator=True
).fillna({'IncidentCount': 0})

# Drop the merge indicator column
df_complete = df_complete.drop('_merge', axis=1)

# Convert IncidentCount to integer
df_complete['IncidentCount'] = df_complete['IncidentCount'].astype(int)

# Sort for better readability
df_complete = df_complete.sort_values(['Neighborhood', 'SRS_UCR', 'FirearmUsed', 'YearMonth'])

# Create aggregate categories
# 1. Create "All neighborhoods" category
all_neighborhoods = df_complete.groupby(['SRS_UCR', 'FirearmUsed', 'YearMonth'])['IncidentCount'].sum().reset_index()
all_neighborhoods['Neighborhood'] = 'All neighborhoods'

# 2. Create "Yes or No" FirearmUsed category  
all_firearm = df_complete.groupby(['Neighborhood', 'SRS_UCR', 'YearMonth'])['IncidentCount'].sum().reset_index()
all_firearm['FirearmUsed'] = 'Yes or No'

# 3. Create "All neighborhoods" + "Yes or No" combination
all_both = df_complete.groupby(['SRS_UCR', 'YearMonth'])['IncidentCount'].sum().reset_index()
all_both['Neighborhood'] = 'All neighborhoods'
all_both['FirearmUsed'] = 'Yes or No'

# 4. Combine all the data
column_order = ['Neighborhood', 'SRS_UCR', 'FirearmUsed', 'YearMonth', 'IncidentCount']

df_complete_reordered = df_complete[column_order]
all_neighborhoods_reordered = all_neighborhoods[column_order]
all_firearm_reordered = all_firearm[column_order]
all_both_reordered = all_both[column_order]

# Concatenate all DataFrames
df_final = pd.concat([
    df_complete_reordered,
    all_neighborhoods_reordered,
    all_firearm_reordered,
    all_both_reordered
], ignore_index=True)

# Sort for better organization
df_final = df_final.sort_values(['Neighborhood', 'SRS_UCR', 'FirearmUsed', 'YearMonth'])

# Formatting cleanup
df_final['Date'] = pd.to_datetime(df_final['YearMonth'])
df_final['Year'] = df_final['Date'].dt.year
df_final['Month'] = df_final['Date'].dt.month
df_final['MonthName'] = df_final['Date'].dt.month_name()
df_final['OffenseUCR'] = df_final['SRS_UCR'].map(UCR_LABELS)

# Calculate average incidents by month, neighborhood, offense type, and firearm use
monthly_avg = df_final.groupby(['MonthName', 'Neighborhood', 'OffenseUCR', 'FirearmUsed'])['IncidentCount'].mean().reset_index()
monthly_avg = monthly_avg.rename(columns={'IncidentCount': 'IncidentMonthlyAvg'})

# Merge the averages back to the original dataframe
df_final_with_avg = df_final.merge(
    monthly_avg,
    on=['MonthName', 'Neighborhood', 'OffenseUCR', 'FirearmUsed'],
    how='left'
)

# Round IncidentMonthlyAvg to one decimal place
df_final_with_avg['IncidentMonthlyAvg'] = df_final_with_avg['IncidentMonthlyAvg'].round(1)

# Calculate year-over-year percentage change
# First, create a pivot table to get January and December values side by side
monthly_pivot = df_final_with_avg.pivot_table(
    index=['Year', 'Neighborhood', 'OffenseUCR', 'FirearmUsed'],
    columns='MonthName',
    values='IncidentCount',
    aggfunc='sum'
).reset_index()

# Calculate percentage change from January to December
# Handle division by zero and NULL values by setting them to 0
monthly_pivot['IncidentYoYPctChg'] = monthly_pivot.apply(
    lambda row: 0 if pd.isna(row['January']) or row['January'] == 0 or pd.isna(row['December'])
    else round(((row['December'] - row['January']) / row['January'] * 100), 1),
    axis=1
)

# Merge the YoY percentage change back to the original dataframe
df_final_with_avg = df_final_with_avg.merge(
    monthly_pivot[['Year', 'Neighborhood', 'OffenseUCR', 'FirearmUsed', 'IncidentYoYPctChg']],
    on=['Year', 'Neighborhood', 'OffenseUCR', 'FirearmUsed'],
    how='left'
)

# Fill any remaining NULL values with 0
df_final_with_avg['IncidentYoYPctChg'] = df_final_with_avg['IncidentYoYPctChg'].fillna(0)

# Output the new dataframe with averages
df_final_with_avg.to_csv(OUTPUT_PATH + 'stlmpd_nibrs_with_avg.csv')
print('Exported CSV file to: ' + OUTPUT_PATH + 'stlmpd_nibrs_with_avg.csv')