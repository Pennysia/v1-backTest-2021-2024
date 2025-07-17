#!/usr/bin/env python3
"""
Improved Directional Positioning Showcase
=========================================

Enhanced visualization for Pennysia AMM directional positioning:
- Clearer titles, subtitles, and axis labels
- Annotations and callouts for key findings
- Highlighting of best/worst strategies and market conditions
- Pair-level labeling for outliers in the volatility plot
- Summary/statistics boxes and contextual insights
- Improved color coding and visual hierarchy
- Distribution of pair types and their average advantage
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

plt.style.use('default')
sns.set_palette("Set2")

# Load the latest mirrored results
result_dir = "../result"
files = [f for f in os.listdir(result_dir) if f.startswith("comprehensive_mirrored_results_")]
latest_file = sorted(files)[-1]
df = pd.read_csv(os.path.join(result_dir, latest_file))

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(22, 15))
fig.suptitle('Pennysia AMM: The Power of Directional Positioning (Enhanced)', fontsize=22, fontweight='bold', color='darkgreen', y=1.03)

# 1. Strategy Performance Metrics (Top Left)
metrics = []
for strategy in df['strategy_name'].unique():
    strategy_data = df[df['strategy_name'] == strategy]
    win_rate = len(strategy_data[strategy_data['advantage_vs_uniswap'] > 0]) / len(strategy_data) * 100
    avg_advantage = strategy_data['advantage_vs_uniswap'].mean()
    max_advantage = strategy_data['advantage_vs_uniswap'].max()
    consistency = 100 - strategy_data['advantage_vs_uniswap'].std() / abs(avg_advantage) * 100 if avg_advantage != 0 else 0
    metrics.append({
        'strategy': strategy,
        'win_rate': win_rate,
        'avg_advantage': avg_advantage,
        'max_advantage': max_advantage,
        'consistency': max(0, min(100, consistency))
    })
metrics_df = pd.DataFrame(metrics)
x = np.arange(len(metrics_df))
width = 0.2
bars1 = ax1.bar(x - 1.5*width, metrics_df['win_rate'], width, label='Win Rate (%)', alpha=0.8, color='#4ecdc4')
bars2 = ax1.bar(x - 0.5*width, metrics_df['avg_advantage']/100, width, label='Avg Advantage (100x)', alpha=0.8, color='#ff6b6b')
bars3 = ax1.bar(x + 0.5*width, metrics_df['max_advantage']/1000, width, label='Max Advantage (1000x)', alpha=0.8, color='#ffe66d')
bars4 = ax1.bar(x + 1.5*width, metrics_df['consistency'], width, label='Consistency Score', alpha=0.8, color='#1a535c')
ax1.set_xlabel('Strategy', fontsize=13, fontweight='bold')
ax1.set_ylabel('Scaled Metrics', fontsize=13, fontweight='bold')
ax1.set_title('Strategy Performance Metrics (Win Rate, Avg/Max Advantage, Consistency)', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels([s.replace('100% Long Token0 + 100% Short Token1', '100% Long T0')
                    .replace('75% Long Token0 + 25% Long Token1', '75% Long T0')
                    .replace('50% Long Token0 + 50% Long Token1 (Balanced)', 'Balanced')
                    .replace('25% Long Token0 + 75% Long Token1', '25% Long T0')
                    .replace('100% Short Token0 + 100% Long Token1', '100% Long T1')
                    for s in metrics_df['strategy']], rotation=0, ha='center', fontsize=11)
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)
# Annotate best win rate
best_idx = metrics_df['win_rate'].idxmax()
ax1.annotate(f'Best Win Rate: {metrics_df.loc[best_idx, "win_rate"]:.1f}%',
             xy=(best_idx, metrics_df.loc[best_idx, 'win_rate']),
             xytext=(best_idx, metrics_df['win_rate'].max()+10),
             arrowprops=dict(facecolor='green', shrink=0.05), fontsize=12, fontweight='bold', color='green')

# 2. Strategy Performance by Market Direction (Top Right)
df['market_direction'] = 'Mixed'
df.loc[(df['token0_change_pct'] > 100) & (df['token1_change_pct'] < 50), 'market_direction'] = 'Token0 Bullish'
df.loc[(df['token0_change_pct'] < 50) & (df['token1_change_pct'] > 100), 'market_direction'] = 'Token1 Bullish'
df.loc[(df['token0_change_pct'] > 100) & (df['token1_change_pct'] > 100), 'market_direction'] = 'Both Bullish'
df.loc[(df['token0_change_pct'] < 0) | (df['token1_change_pct'] < 0), 'market_direction'] = 'Bearish Market'
market_performance = df.groupby(['market_direction', 'strategy_name'])['advantage_vs_uniswap'].mean().unstack().fillna(0)
sns.heatmap(market_performance, annot=True, fmt='.0f', cmap='RdYlGn', center=0, ax=ax2, cbar_kws={'label': 'Avg Advantage (%)'})
ax2.set_title('Strategy Performance by Market Direction', fontsize=14, fontweight='bold')
ax2.set_xlabel('Strategy', fontsize=13)
ax2.set_ylabel('Market Direction', fontsize=13)
# Highlight best cell
max_idx = np.unravel_index(np.nanargmax(market_performance.values), market_performance.shape)
ax2.add_patch(plt.Rectangle((max_idx[1], max_idx[0]), 1, 1, fill=False, edgecolor='blue', lw=3, clip_on=False))
ax2.annotate('Best Scenario', xy=(max_idx[1]+0.5, max_idx[0]+0.5), xycoords='data', color='blue', fontsize=12, fontweight='bold', ha='center', va='center')

# 3. Volatility vs Advantage (Bottom Left)
df['volatility'] = abs(df['token0_change_pct'] - df['token1_change_pct'])
scatter = ax3.scatter(df['volatility'], df['advantage_vs_uniswap'], c=df['pennysia_return_pct'], cmap='plasma', s=np.abs(df['advantage_vs_uniswap'])/100, alpha=0.7, edgecolor='k')
ax3.set_xlabel('Price Volatility (|Token0% - Token1%|)', fontsize=13)
ax3.set_ylabel('Advantage vs Uniswap (%)', fontsize=13)
ax3.set_title('Volatility vs Advantage (Bubble Size = Advantage)', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.axhline(y=0, color='red', linestyle='--', alpha=0.7)
cbar3 = plt.colorbar(scatter, ax=ax3)
cbar3.set_label('Pennysia Return (%)')
# Annotate top 3 outliers
outliers = df.nlargest(3, 'advantage_vs_uniswap')
for _, row in outliers.iterrows():
    ax3.annotate(row['pair'], (row['volatility'], row['advantage_vs_uniswap']),
                 textcoords="offset points", xytext=(0,10), ha='center', fontsize=10, fontweight='bold', color='blue')

# 4. Strategy Performance by Pair Type (Bottom Right)
pair_types = []
for pair in df['pair']:
    if 'USDC' in pair or 'USDT' in pair:
        pair_types.append('Crypto-Stable')
    elif 'GALA' in pair:
        pair_types.append('GALA Pairs')
    else:
        pair_types.append('Crypto-Crypto')
df['pair_type'] = pair_types
pair_type_performance = df.groupby(['pair_type', 'strategy_name'])['advantage_vs_uniswap'].mean().unstack().fillna(0)
pair_type_performance.plot(kind='bar', ax=ax4, width=0.8, alpha=0.8, legend=True)
ax4.axhline(y=0, color='red', linestyle='-', linewidth=1)
ax4.set_xlabel('Pair Type', fontsize=13)
ax4.set_ylabel('Average Advantage (%)', fontsize=13)
ax4.set_title('Strategy Performance by Pair Type', fontsize=14, fontweight='bold')
ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
ax4.grid(True, alpha=0.3)
ax4.tick_params(axis='x', rotation=0)
# Annotate best bar
best_pairtype = pair_type_performance.max().max()
for i, col in enumerate(pair_type_performance.columns):
    idx = pair_type_performance[col].idxmax()
    val = pair_type_performance[col].max()
    if val == best_pairtype:
        ax4.annotate('Best', xy=(list(pair_type_performance.index).index(idx), val),
                     xytext=(0, 20), textcoords='offset points', ha='center', color='blue', fontsize=12, fontweight='bold', arrowprops=dict(facecolor='blue', shrink=0.05))

# Add summary box
summary_text = f"""
Key Insights:
- Best win rate: {metrics_df['win_rate'].max():.1f}%
- Highest avg advantage: {metrics_df['avg_advantage'].max():.0f}%
- Top outlier: {outliers.iloc[0]['pair']} ({outliers.iloc[0]['advantage_vs_uniswap']:.0f}%)
- Best scenario: {market_performance.columns[max_idx[1]]} in {market_performance.index[max_idx[0]]}
"""
fig.text(0.99, 0.01, summary_text, ha='right', va='bottom', fontsize=13, color='black', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout(rect=[0, 0.03, 1, 0.97])
plt.savefig(os.path.join(result_dir, 'directional_positioning_showcase_improved.png'), dpi=300, bbox_inches='tight')
plt.close()
print('✅ Improved directional positioning showcase saved as directional_positioning_showcase_improved.png') 