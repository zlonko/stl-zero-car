import pandas as pd
import geopandas as gpd
from shapely import wkt
import matplotlib.pyplot as plt
import matplotlib.colors as colors

INPUT_PATH = './output/'
OUTPUT_PATH = './charts/'
TRACT_DATA = 'st_louis_city_vulnerability_rates.csv'

# Load census tract level data
df_base_data = pd.read_csv(INPUT_PATH + TRACT_DATA)
df_base_data['FIPS Code'] = df_base_data['FIPS Code'].astype(str)

df_tracts = pd.read_csv('tracts.csv')
df_tracts['FIPS Code'] = df_tracts['GEOID'].astype(str)

# Merge data and geometries on tract FIPS
df_combined = df_tracts.merge(df_base_data, on='FIPS Code', how='left')
df_combined['geometry'] = df_combined['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df_combined, geometry='geometry', crs="EPSG:4326")

# Create a choropleth map
fig, ax = plt.subplots(figsize=(14, 10))

def plot_quantitative_map(gdf, ax, variable, map_title, label, CHART_OUTPUT_NAME):
    # Create plot
    gdf.plot(
        column = variable,
        cmap = 'Purples',
        linewidth = 0.8,
        ax = ax,
        edgecolor = '0.8',
        legend = True,
        legend_kwds = {'label': label, 'orientation': "vertical"},
    )
    # Add title to map
    ax.set_title(map_title, fontsize=15)
    ax.set_axis_off()
    plt.tight_layout()
    
    # Save file
    plt.savefig(OUTPUT_PATH + CHART_OUTPUT_NAME)
    return

def plot_qualitative_map(gdf, ax, variable, map_title, label, CHART_OUTPUT_NAME):
    # Plot variable on map geometries
    gdf.plot(
        column = variable,
        cmap = 'Purples',
        linewidth = 0.8,
        ax = ax,
        edgecolor = '0.8',
        legend = True,
        legend_kwds = {'label': label, 'orientation': "vertical"},
    )

    # Add title to map
    ax.set_title(map_title, fontsize=15)
    ax.set_axis_off()
    plt.tight_layout()

    # Save file
    plt.savefig(OUTPUT_PATH + CHART_OUTPUT_NAME)
    # plt.show()
    return

# Plot Zero-Car Map
plot_quantitative_map(gdf, ax,
                      'no_vehicle_rate', 
                      'Percent of Zero-Car Households, St. Louis City', 
                      'Percent of households without a vehicle', 
                      'MAP_no_vehicle_rate.svg')

# Plot pct-BIPOC map
plot_quantitative_map(gdf, ax, 
                      'bipoc_resident_rate', 
                      'Percent of Residents Who Are BIPOC, St. Louis City', 
                      'Percent of residents who are BIPOC', 
                      'MAP_bipoc_resident_rate.svg')

# Plot commute ratio map
plot_qualitative_map(gdf, ax,
                     'ratio_quantile',
                     'Areas Where More Jobs are Commutable by Car than Transit, St. Louis City',
                     'Difference in commute ratio',
                     'MAP_commute_ratio_diff.svg'
                     )