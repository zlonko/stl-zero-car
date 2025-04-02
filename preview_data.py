import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

DATA_PATH = './process_data/st_louis_city_vulnerability.csv'

# Load the data
df = pd.read_csv(DATA_PATH)

# Get basic information about data
print("Dataset shape:", df.shape)
print("\nPreview rows:")
print(df.head())

# Check values for completeness
print("\nMissing values per column:")
print(df.isnull().sum())

# Run summary statistics
print("\nSummary statistics:")
print(df.describe())

# Check column data types
print("\nData types:")
print(df.dtypes)

# Distribution of key variables
plt.figure(figsize=(12, 10))
for i, column in enumerate(df.select_dtypes(include=np.number).columns[:9]):
    plt.subplot(3, 3, i+1)
    sns.histplot(df[column], kde=True)
    plt.title(column)
plt.tight_layout()
plt.show()