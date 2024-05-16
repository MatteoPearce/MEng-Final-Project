import numpy as np
import matplotlib.pyplot as plt

# Generate some example data
np.random.seed(42)
target = np.linspace(0, 100, 100)  # Target variable ranging from 0 to 100
predictions = target + np.random.normal(0, 50, 100)  # Model's predictions with RMSE of 50

# Calculate RMSE
rmse = np.sqrt(np.mean((predictions - target)**2))

# Calculate NRMSE
range_target = np.max(target) - np.min(target)
nrmse = rmse / range_target

# Plot the target variable and the model's predictions
plt.figure(figsize=(10, 6))
plt.plot(target, label='Target')
plt.plot(predictions, label='Predictions')
plt.fill_between(np.arange(len(target)), target - rmse, target + rmse, color='gray', alpha=0.3, label='RMSE')
plt.title(f'NRMSE: {nrmse:.2f}')
plt.xlabel('Index')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plt.show()

# Generate some example data
np.random.seed(42)
target = np.linspace(0, 100, 100)  # Target variable ranging from 0 to 100
predictions = target + np.random.normal(0, 250, 100)  # Model's predictions with RMSE of 250 (NRMSE of 5)

# Calculate RMSE
rmse = np.sqrt(np.mean((predictions - target)**2))

# Calculate NRMSE
range_target = np.max(target) - np.min(target)
nrmse = rmse / range_target

# Plot the target variable and the model's predictions
plt.figure(figsize=(10, 6))
plt.plot(target, label='Target')
plt.plot(predictions, label='Predictions')
plt.fill_between(np.arange(len(target)), target - rmse, target + rmse, color='gray', alpha=0.3, label='RMSE')
plt.title(f'NRMSE: {nrmse:.2f}')
plt.xlabel('Index')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plt.show()

np.random.seed(42)
target = np.linspace(0, 100, 100)  # Target variable ranging from 0 to 100
predictions = target + np.random.normal(0, 5, 100)  # Model's predictions with RMSE of 5 (NRMSE of 0.1)

# Calculate RMSE
rmse = np.sqrt(np.mean((predictions - target)**2))

# Calculate NRMSE
range_target = np.max(target) - np.min(target)
nrmse = rmse / range_target

# Plot the target variable and the model's predictions
plt.figure(figsize=(10, 6))
plt.plot(target, label='Target')
plt.plot(predictions, label='Predictions')
plt.fill_between(np.arange(len(target)), target - rmse, target + rmse, color='gray', alpha=0.3, label='RMSE')
plt.title(f'NRMSE: {nrmse:.2f}')
plt.xlabel('Index')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plt.show()