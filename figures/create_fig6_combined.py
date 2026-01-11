"""
Create combined Figure 6: Model Performance Comparison + SHAP Waterfall
This creates a single figure with both subplots
"""
import matplotlib.pyplot as plt
import numpy as np

# Replace with your actual metrics
models = ['XGBoost', 'Random Forest', 'Gradient Boosting', 'Ridge']
rmse = [245.32, 267.18, 271.45, 412.56]  # Your actual RMSE values
mae = [189.45, 201.23, 205.67, 328.91]   # Your actual MAE values
r2 = [0.892, 0.875, 0.869, 0.698]        # Your actual R² values

# Create figure with 2 subplots side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Subplot 1: Model Performance Comparison (3 metrics)
x = np.arange(len(models))
width = 0.25

# Normalize RMSE and MAE for better visualization (or use separate y-axes)
ax1_twin = ax1.twinx()

bars1 = ax1.bar(x - width, rmse, width, label='RMSE', color='#6366f1', alpha=0.8)
bars2 = ax1.bar(x, mae, width, label='MAE', color='#a855f7', alpha=0.8)
bars3 = ax1_twin.bar(x + width, r2, width, label='R²', color='#22c55e', alpha=0.8)

ax1.set_xlabel('Model', fontsize=11)
ax1.set_ylabel('RMSE / MAE', fontsize=11, color='#6366f1')
ax1_twin.set_ylabel('R² Score', fontsize=11, color='#22c55e')
ax1.set_title('(a) Model Performance Comparison', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(models, rotation=45, ha='right')
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')
ax1.grid(True, alpha=0.3)

# Subplot 2: SHAP Waterfall (example - replace with your actual SHAP data)
# This is a placeholder - you'll need to replace with actual SHAP values
feature_names = ['RSI', 'MACD Histogram', 'BB Position', 'SMA Ratio', 'Volatility', 
                 'Momentum', 'ROC', 'Price Lag 1', 'Returns Lag 1', 'Hour']
shap_values = [0.15, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02]  # Replace with actual

# Sort by absolute value
sorted_data = sorted(zip(feature_names, shap_values), key=lambda x: abs(x[1]), reverse=True)
top_features, top_values = zip(*sorted_data[:10])

colors = ['#22c55e' if v > 0 else '#ef4444' for v in top_values]
ax2.barh(range(len(top_features)), top_values, color=colors, alpha=0.8)
ax2.set_yticks(range(len(top_features)))
ax2.set_yticklabels(top_features)
ax2.set_xlabel('SHAP Value', fontsize=11)
ax2.set_title('(b) SHAP Feature Contributions', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')
ax2.axvline(x=0, color='black', linestyle='--', linewidth=0.5)

plt.tight_layout()
plt.savefig('figures/fig6_model_comparison.pdf', dpi=300, bbox_inches='tight')
print("Combined figure saved to figures/fig6_model_comparison.pdf")
print("Note: Replace SHAP values in the script with your actual SHAP data!")




