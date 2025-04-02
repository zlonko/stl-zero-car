import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

DATA_PATH = './output/st_louis_city_vulnerability_rates.csv'
OUTPUT_PATH = './charts/'

# Read in dataframe
df = pd.read_csv(DATA_PATH)

# Correlation matrix for numerical variables
df_only_rate_columns = df.drop(['FIPS Code', 'Location'], axis = 1)
corr = df_only_rate_columns.select_dtypes(include = np.number).corr()
plt.figure(figsize = (20, 10))
sns.heatmap(corr, annot = True, cmap = 'coolwarm', center = 0)
plt.title('Correlation Matrix')
plt.savefig(OUTPUT_PATH + 'correlation_matrix.svg')

# Create scatterplot
def create_scatterplot(chart_name, variable_x, variable_y, plot_title, x_label, y_label):
    # Plot design
    plt.figure(figsize=(6, 6))
    sns.regplot(x = variable_x, 
                y = variable_y, 
                data = df,
                scatter_kws = {'alpha':0.5})
    plt.title(plot_title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True, linestyle='--', alpha = 0.5)

    # Calculate Pearson correlation coefficient
    correlation = df[variable_x].corr(df[variable_y])
    plt.annotate(f'PCC: {correlation:.2f}', xy = (0.05, 0.95), xycoords = 'axes fraction')

    # Control plot display
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH + 'SCATTER_' + chart_name + ".svg")
    return

create_scatterplot(
    'fpl-zerocar',
    'no_vehicle_rate',
    'below_150_pct_fpl_rate',
    'Zero-Car Households and Poverty, St. Louis City Census Tracts',
    'Percentage of Zero-Car Households',
    'Percentage of Population Below 150-pct FPL'
)

create_scatterplot(
    'bipoc-zerocar',
    'no_vehicle_rate',
    'bipoc_resident_rate',
    'Zero-Car Households and BIPOC Residents, St. Louis City Census Tracts',
    'Percentage of Zero-Car Households',
    'Percentage of Residents Who Are BIPOC'
)

create_scatterplot(
    'education-zerocar',
    'no_vehicle_rate',
    'without_high_school_diploma_rate',
    'Zero-Car Households and Population Without High School Diploma, St. Louis City Census Tracts',
    'Percentage of Zero-Car Households',
    'Percentage of Residents Without a Diploma'
)

create_scatterplot(
    'bipoc-fpl',
    'bipoc_resident_rate',
    'below_150_pct_fpl_rate',
    'BIPOC Residents and Poverty, St. Louis City Census Tracts',
    'Percentage of Residents Who Are BIPOC',
    'Percentage of Population Below 150-pct FPL'
)

def create_overlap_histogram():
    # Set up the figure
    plt.figure(figsize=(10, 6))

    # Create histogram bins that work for both distributions
    min_value = min(df['number_jobs_commutable_by_vehicle_45_minutes'].min(), df['number_jobs_commutable_by_transit_45_minutes'].min())
    max_value = max(df['number_jobs_commutable_by_vehicle_45_minutes'].max(), df['number_jobs_commutable_by_transit_45_minutes'].max())
    bins = np.linspace(min_value, max_value, 15)

    # Plot both histograms with transparency
    plt.hist(df['number_jobs_commutable_by_vehicle_45_minutes'], bins=bins, alpha=0.6, color='steelblue', 
            edgecolor='black', label='Jobs Commutable by Vehicle')
    plt.hist(df['number_jobs_commutable_by_transit_45_minutes'], bins=bins, alpha=0.6, color='orange', 
            edgecolor='black', label='Jobs Commutable by Transit')

    # Add reference line for city average
    plt.axvline(x=0, color='red', linestyle='--', linewidth=1.5, label='City Average')

    # Add labels and title
    plt.title('Comparison of Commutable Jobs by Vehicle vs. Transit', fontsize=14)
    plt.xlabel('Number of Jobs', fontsize=12)
    plt.ylabel('Number of Census Tracts', fontsize=12)
    plt.legend()

    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3)

    # Improve layout
    plt.tight_layout()

    # To show the plot
    plt.savefig(OUTPUT_PATH + 'HISTO_overlapping_commute_histograms.svg', dpi=300, bbox_inches='tight')
    plt.show()
    return

create_overlap_histogram()