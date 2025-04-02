import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.graphics.regressionplots import plot_partregress

DATA_PATH = './output/st_louis_city_vulnerability_rates.csv'
OUTPUT_PATH = './charts/'

# Load data
df = pd.read_csv(DATA_PATH)

# 1. Correlation matrix with visualization
plt.figure(figsize=(10, 8))
correlation_matrix = df.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Correlation Matrix')
plt.tight_layout()
plt.savefig(OUTPUT_PATH + 'correlation_matrix.svg')
plt.close()

# 2. Pairplot to visualize relationships
plt.figure(figsize=(12, 10))
sns_plot = sns.pairplot(df, kind='reg', diag_kind='kde')
sns_plot.fig.suptitle('Pairwise Relationships', y=1.02)
plt.savefig(OUTPUT_PATH + 'pairplot.svg')
plt.close()

# 3. Multiple regression model
X = df[['bipoc_resident_rate', 'below_150_pct_fpl_rate']]
X = sm.add_constant(X)  # Add constant for intercept
y = df['no_vehicle_rate']

# Fit model
model = sm.OLS(y, X).fit()

# Print summary
print("\nMultiple Regression Results:")
print(model.summary())

# 4. Partial regression plots
fig = plt.figure(figsize=(12, 6))
fig = plot_partregress(model, fig=fig, exog_i= '', exog_others='')
plt.tight_layout()
plt.savefig(OUTPUT_PATH + 'partial_regression_plots.svg')
plt.close()

# 5. 3D visualization for two predictors
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Create meshgrid for prediction surface
x1_range = np.linspace(df['bipoc_resident_rate'].min(), df['bipoc_resident_rate'].max(), 20)
x2_range = np.linspace(df['below_150_pct_fpl_rate'].min(), df['below_150_pct_fpl_rate'].max(), 20)
X1_grid, X2_grid = np.meshgrid(x1_range, x2_range)
Z_pred = np.zeros(X1_grid.shape)

# Calculate predicted values for each point in the grid
for i in range(X1_grid.shape[0]):
    for j in range(X1_grid.shape[1]):
        # Create input array with constant term
        x_input = np.array([1, X1_grid[i,j], X2_grid[i,j]])
        Z_pred[i,j] = x_input.dot(model.params)

# Plot the surface
surface = ax.plot_surface(X1_grid, X2_grid, Z_pred, alpha=0.5, cmap='viridis')

# Plot the actual data points
scatter = ax.scatter(df['bipoc_resident_rate'], df['below_150_pct_fpl_rate'], df['no_vehicle_rate'], 
                    c=df['no_vehicle_rate'], cmap='viridis', s=50, edgecolor='k')

# Add labels and colorbar
ax.set_xlabel('BIPOC Percentage')
ax.set_ylabel('Percentage Below 150-FPL')
ax.set_zlabel('No Vehicle Rate')
ax.set_title('3D Visualization of Multiple Regression')
fig.colorbar(surface, ax=ax, shrink=0.5, aspect=5)

plt.tight_layout()
plt.savefig(OUTPUT_PATH + '3d_regression.svg')
plt.close()

# 6. Residual analysis
# Get predictions and residuals
df['predicted'] = model.predict(X)
df['residuals'] = model.resid

# Residual plots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Residuals vs. fitted values
sns.scatterplot(x='predicted', y='residuals', data=df, ax=axes[0, 0])
axes[0, 0].axhline(y=0, color='r', linestyle='-')
axes[0, 0].set_title('Residuals vs. Fitted Values')
axes[0, 0].set_xlabel('Fitted Values')
axes[0, 0].set_ylabel('Residuals')

# Residuals vs. predictor 1
sns.scatterplot(x='bipoc_resident_rate', y='residuals', data=df, ax=axes[0, 1])
axes[0, 1].axhline(y=0, color='r', linestyle='-')
axes[0, 1].set_title('Residuals vs. BIPOC Resident Rate')
axes[0, 1].set_xlabel('BIPOC Percentage')
axes[0, 1].set_ylabel('Residuals')

# Residuals vs. predictor 2
sns.scatterplot(x='below_150_pct_fpl_rate', y='residuals', data=df, ax=axes[1, 0])
axes[1, 0].axhline(y=0, color='r', linestyle='-')
axes[1, 0].set_title('Residuals vs. Percentage Below 150-FPL')
axes[1, 0].set_xlabel('Percentage Below 150-FPL')
axes[1, 0].set_ylabel('Residuals')

# Histogram of residuals
sns.histplot(df['residuals'], kde=True, ax=axes[1, 1])
axes[1, 1].set_title('Distribution of Residuals')
axes[1, 1].set_xlabel('Residuals')

plt.tight_layout()
plt.savefig(OUTPUT_PATH + 'residual_analysis.svg')
plt.close()