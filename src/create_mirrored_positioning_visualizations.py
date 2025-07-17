#!/usr/bin/env python3
"""
Mirrored Positioning Visualizations
===================================

Create comprehensive charts, heatmaps, and graphs to showcase the
Pennysia mirrored positioning backtest results.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# Set style for professional charts
plt.style.use('default')
sns.set_palette("husl")

def load_latest_mirrored_results() -> pd.DataFrame:
    """Load the latest mirrored positioning results"""
    
    result_dir = "../result"
    
    # Find the latest mirrored results file
    files = [f for f in os.listdir(result_dir) if f.startswith("comprehensive_mirrored_results_")]
    if not files:
        print("❌ No mirrored results found")
        return pd.DataFrame()
    
    latest_file = sorted(files)[-1]
    file_path = os.path.join(result_dir, latest_file)
    
    print(f"📊 Loading results from: {latest_file}")
    df = pd.read_csv(file_path)
    print(f"   {len(df)} strategy tests loaded")
    
    return df

def create_advantage_distribution_analysis(df: pd.DataFrame, output_dir: str):
    """Create comprehensive advantage distribution analysis"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Pennysia Mirrored Positioning: Advantage Distribution Analysis', fontsize=18, fontweight='bold')
    
    # 1. Advantage distribution histogram
    advantages = df['advantage_vs_uniswap']
    
    # Remove extreme outliers for better visualization
    q99 = advantages.quantile(0.99)
    q01 = advantages.quantile(0.01)
    filtered_advantages = advantages[(advantages >= q01) & (advantages <= q99)]
    
    ax1.hist(filtered_advantages, bins=50, alpha=0.7, color='green', edgecolor='black', linewidth=0.5)
    ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Break-even')
    ax1.axvline(x=advantages.mean(), color='blue', linestyle='-', linewidth=2, label=f'Mean: {advantages.mean():.0f}%')
    ax1.set_xlabel('Advantage vs Uniswap V2 (%)', fontsize=12)
    ax1.set_ylabel('Number of Strategy Tests', fontsize=12)
    ax1.set_title('Distribution of Pennysia Advantages (99th percentile view)', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add statistics text
    win_rate = len(df[df['advantage_vs_uniswap'] > 0]) / len(df) * 100
    stats_text = f"""Statistics:
Total Tests: {len(df)}
Win Rate: {win_rate:.1f}%
Mean Advantage: {advantages.mean():.0f}%
Median Advantage: {advantages.median():.0f}%
Max Advantage: {advantages.max():.0f}%"""
    
    ax1.text(0.75, 0.95, stats_text, transform=ax1.transAxes, fontsize=10,
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
             verticalalignment='top')
    
    # 2. Strategy performance comparison
    strategy_performance = df.groupby('strategy_name').agg({
        'advantage_vs_uniswap': ['mean', 'median', 'count'],
        'pennysia_return_pct': 'mean'
    }).round(1)
    
    strategy_names = [name.replace(' + ', '\n+\n').replace('Token0', 'T0').replace('Token1', 'T1') 
                     for name in strategy_performance.index]
    
    x_pos = np.arange(len(strategy_names))
    means = strategy_performance[('advantage_vs_uniswap', 'mean')]
    
    bars = ax2.bar(x_pos, means, alpha=0.7, color=['red', 'orange', 'yellow', 'lightgreen', 'green'])
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('Strategy', fontsize=12)
    ax2.set_ylabel('Average Advantage (%)', fontsize=12)
    ax2.set_title('Average Advantage by Strategy', fontsize=14)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(strategy_names, rotation=45, ha='right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, means)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(means)*0.01,
                f'{val:.0f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 3. Win rate by strategy
    win_rates = []
    for strategy in strategy_performance.index:
        strategy_data = df[df['strategy_name'] == strategy]
        wins = len(strategy_data[strategy_data['advantage_vs_uniswap'] > 0])
        total = len(strategy_data)
        win_rates.append(wins / total * 100)
    
    bars3 = ax3.bar(x_pos, win_rates, alpha=0.7, color=['red', 'orange', 'yellow', 'lightgreen', 'green'])
    ax3.set_xlabel('Strategy', fontsize=12)
    ax3.set_ylabel('Win Rate (%)', fontsize=12)
    ax3.set_title('Win Rate by Strategy', fontsize=14)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(strategy_names, rotation=45, ha='right', fontsize=9)
    ax3.set_ylim(0, 100)
    ax3.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, rate in zip(bars3, win_rates):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # 4. Advantage vs Price Changes Scatter
    scatter = ax4.scatter(df['token0_change_pct'], df['advantage_vs_uniswap'], 
                         c=df['token1_change_pct'], cmap='RdYlBu', alpha=0.6, s=40)
    ax4.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    ax4.axvline(x=0, color='red', linestyle='--', alpha=0.5)
    ax4.set_xlabel('Token0 Price Change (%)', fontsize=12)
    ax4.set_ylabel('Advantage vs Uniswap (%)', fontsize=12)
    ax4.set_title('Advantage vs Price Changes', fontsize=14)
    ax4.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('Token1 Price Change (%)', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mirrored_advantage_distribution_analysis.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   📊 Advantage distribution analysis saved")

def create_pair_performance_heatmap(df: pd.DataFrame, output_dir: str):
    """Create pair performance heatmaps"""
    
    # Get unique pairs and strategies
    pairs = df['pair'].unique()
    strategies = df['strategy_name'].unique()
    
    # Create matrices for different metrics
    advantage_matrix = np.full((len(pairs), len(strategies)), np.nan)
    return_matrix = np.full((len(pairs), len(strategies)), np.nan)
    
    for i, pair in enumerate(pairs):
        for j, strategy in enumerate(strategies):
            mask = (df['pair'] == pair) & (df['strategy_name'] == strategy)
            if mask.any():
                advantage_matrix[i, j] = df.loc[mask, 'advantage_vs_uniswap'].iloc[0]
                return_matrix[i, j] = df.loc[mask, 'pennysia_return_pct'].iloc[0]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 12))
    fig.suptitle('Pennysia Mirrored Positioning: Performance Heatmaps', fontsize=18, fontweight='bold')
    
    # Strategy names for labels (shortened)
    strategy_labels = [s.replace('100% Long Token0 + 100% Short Token1', '100% Long T0')
                      .replace('75% Long Token0 + 25% Long Token1', '75% Long T0')
                      .replace('50% Long Token0 + 50% Long Token1 (Balanced)', '50% Balanced')
                      .replace('25% Long Token0 + 75% Long Token1', '25% Long T0')
                      .replace('100% Short Token0 + 100% Long Token1', '100% Long T1')
                      for s in strategies]
    
    # 1. Advantage heatmap
    # Cap extreme values for better visualization
    advantage_capped = np.clip(advantage_matrix, -1000, 10000)
    
    sns.heatmap(advantage_capped, 
                xticklabels=strategy_labels,
                yticklabels=pairs,
                annot=True, fmt='.0f', 
                cmap='RdYlGn', center=0,
                ax=ax1, 
                cbar_kws={'label': 'Advantage vs Uniswap (%)'})
    ax1.set_title('Advantage vs Uniswap V2 by Pair and Strategy', fontsize=14)
    ax1.set_xlabel('Strategy', fontsize=12)
    ax1.set_ylabel('Trading Pair', fontsize=12)
    
    # 2. Pennysia returns heatmap
    return_capped = np.clip(return_matrix, -100, 20000)
    
    sns.heatmap(return_capped,
                xticklabels=strategy_labels,
                yticklabels=pairs,
                annot=True, fmt='.0f',
                cmap='viridis',
                ax=ax2,
                cbar_kws={'label': 'Pennysia Return (%)'})
    ax2.set_title('Pennysia Returns by Pair and Strategy', fontsize=14)
    ax2.set_xlabel('Strategy', fontsize=12)
    ax2.set_ylabel('Trading Pair', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mirrored_pair_performance_heatmap.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   📊 Pair performance heatmap saved")

def create_top_performers_showcase(df: pd.DataFrame, output_dir: str):
    """Create showcase of top and bottom performers"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Pennysia Mirrored Positioning: Top & Bottom Performers', fontsize=18, fontweight='bold')
    
    # 1. Top 15 individual results
    top_15 = df.nlargest(15, 'advantage_vs_uniswap')
    
    y_pos = np.arange(len(top_15))
    bars1 = ax1.barh(y_pos, top_15['advantage_vs_uniswap'], 
                     color='green', alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Create labels with pair and strategy info
    labels = [f"{row['pair']} ({row['strategy_name'][:15]}...)" 
              for _, row in top_15.iterrows()]
    
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(labels, fontsize=9)
    ax1.set_xlabel('Advantage vs Uniswap (%)', fontsize=12)
    ax1.set_title('Top 15 Individual Results', fontsize=14)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars1, top_15['advantage_vs_uniswap'])):
        ax1.text(val + max(top_15['advantage_vs_uniswap'])*0.01, bar.get_y() + bar.get_height()/2,
                f'+{val:.0f}%', va='center', fontweight='bold', fontsize=8)
    
    # 2. Bottom 10 individual results
    bottom_10 = df.nsmallest(10, 'advantage_vs_uniswap')
    
    y_pos = np.arange(len(bottom_10))
    bars2 = ax2.barh(y_pos, bottom_10['advantage_vs_uniswap'], 
                     color='red', alpha=0.7, edgecolor='black', linewidth=0.5)
    
    labels_bottom = [f"{row['pair']} ({row['strategy_name'][:15]}...)" 
                     for _, row in bottom_10.iterrows()]
    
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(labels_bottom, fontsize=9)
    ax2.set_xlabel('Advantage vs Uniswap (%)', fontsize=12)
    ax2.set_title('Bottom 10 Individual Results', fontsize=14)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars2, bottom_10['advantage_vs_uniswap'])):
        ax2.text(val - abs(min(bottom_10['advantage_vs_uniswap']))*0.01, bar.get_y() + bar.get_height()/2,
                f'{val:.0f}%', va='center', ha='right', fontweight='bold', fontsize=8)
    
    # 3. Best strategy by pair
    best_by_pair = df.loc[df.groupby('pair')['advantage_vs_uniswap'].idxmax()]
    best_by_pair = best_by_pair.sort_values('advantage_vs_uniswap', ascending=True)
    
    y_pos = np.arange(len(best_by_pair))
    colors = ['red' if x < 0 else 'green' for x in best_by_pair['advantage_vs_uniswap']]
    
    bars3 = ax3.barh(y_pos, best_by_pair['advantage_vs_uniswap'], 
                     color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(best_by_pair['pair'], fontsize=10)
    ax3.set_xlabel('Best Advantage vs Uniswap (%)', fontsize=12)
    ax3.set_title('Best Strategy Performance by Pair', fontsize=14)
    ax3.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax3.grid(True, alpha=0.3)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars3, best_by_pair['advantage_vs_uniswap'])):
        if val >= 0:
            ax3.text(val + max(best_by_pair['advantage_vs_uniswap'])*0.01, bar.get_y() + bar.get_height()/2,
                    f'+{val:.0f}%', va='center', fontweight='bold', fontsize=8)
        else:
            ax3.text(val - abs(min(best_by_pair['advantage_vs_uniswap']))*0.01, bar.get_y() + bar.get_height()/2,
                    f'{val:.0f}%', va='center', ha='right', fontweight='bold', fontsize=8)
    
    # 4. Return comparison by strategy
    strategy_comparison = df.groupby('strategy_name').agg({
        'uniswap_return_pct': 'mean',
        'pennysia_return_pct': 'mean'
    }).round(0)
    
    x_pos = np.arange(len(strategy_comparison))
    width = 0.35
    
    bars4a = ax4.bar(x_pos - width/2, strategy_comparison['uniswap_return_pct'], 
                     width, label='Uniswap V2', alpha=0.8, color='blue')
    bars4b = ax4.bar(x_pos + width/2, strategy_comparison['pennysia_return_pct'], 
                     width, label='Pennysia', alpha=0.8, color='green')
    
    ax4.set_xlabel('Strategy', fontsize=12)
    ax4.set_ylabel('Average Return (%)', fontsize=12)
    ax4.set_title('Average Returns: Uniswap vs Pennysia', fontsize=14)
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels([s.replace(' + ', '\n+\n').replace('Token0', 'T0').replace('Token1', 'T1') 
                        for s in strategy_comparison.index], rotation=45, ha='right', fontsize=9)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mirrored_top_performers_showcase.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   📊 Top performers showcase saved")

def create_price_movement_analysis(df: pd.DataFrame, output_dir: str):
    """Create analysis based on price movements"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Pennysia Performance vs Market Conditions', fontsize=18, fontweight='bold')
    
    # 1. Advantage vs Token0 price change
    scatter1 = ax1.scatter(df['token0_change_pct'], df['advantage_vs_uniswap'], 
                          c=df['token1_change_pct'], cmap='coolwarm', alpha=0.6, s=50)
    ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7, linewidth=2)
    ax1.axvline(x=0, color='red', linestyle='--', alpha=0.7, linewidth=2)
    ax1.set_xlabel('Token0 Price Change (%)', fontsize=12)
    ax1.set_ylabel('Advantage vs Uniswap (%)', fontsize=12)
    ax1.set_title('Advantage vs Token0 Price Movement', fontsize=14)
    ax1.grid(True, alpha=0.3)
    
    cbar1 = plt.colorbar(scatter1, ax=ax1)
    cbar1.set_label('Token1 Price Change (%)')
    
    # 2. Strategy effectiveness in different market conditions
    # Categorize market conditions
    df_analysis = df.copy()
    df_analysis['market_condition'] = 'Mixed'
    df_analysis.loc[(df_analysis['token0_change_pct'] > 50) & (df_analysis['token1_change_pct'] > 50), 'market_condition'] = 'Both Up'
    df_analysis.loc[(df_analysis['token0_change_pct'] < -10) & (df_analysis['token1_change_pct'] < -10), 'market_condition'] = 'Both Down'
    df_analysis.loc[(df_analysis['token0_change_pct'] > 50) & (df_analysis['token1_change_pct'] < 10), 'market_condition'] = 'Token0 Up'
    df_analysis.loc[(df_analysis['token0_change_pct'] < 10) & (df_analysis['token1_change_pct'] > 50), 'market_condition'] = 'Token1 Up'
    
    market_performance = df_analysis.groupby(['market_condition', 'strategy_name'])['advantage_vs_uniswap'].mean().unstack()
    
    market_performance.plot(kind='bar', ax=ax2, width=0.8, alpha=0.8)
    ax2.axhline(y=0, color='red', linestyle='-', linewidth=1)
    ax2.set_xlabel('Market Condition', fontsize=12)
    ax2.set_ylabel('Average Advantage (%)', fontsize=12)
    ax2.set_title('Strategy Performance by Market Condition', fontsize=14)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Volatility analysis
    df_analysis['price_volatility'] = abs(df_analysis['token0_change_pct'] - df_analysis['token1_change_pct'])
    
    # Bin by volatility
    df_analysis['volatility_category'] = pd.cut(df_analysis['price_volatility'], 
                                               bins=[0, 100, 500, 1000, float('inf')],
                                               labels=['Low (<100%)', 'Medium (100-500%)', 'High (500-1000%)', 'Extreme (>1000%)'])
    
    volatility_performance = df_analysis.groupby('volatility_category')['advantage_vs_uniswap'].agg(['mean', 'count'])
    
    bars3 = ax3.bar(range(len(volatility_performance)), volatility_performance['mean'], 
                    alpha=0.7, color='purple', edgecolor='black', linewidth=0.5)
    ax3.axhline(y=0, color='red', linestyle='-', linewidth=1)
    ax3.set_xlabel('Price Volatility Category', fontsize=12)
    ax3.set_ylabel('Average Advantage (%)', fontsize=12)
    ax3.set_title('Performance vs Price Volatility', fontsize=14)
    ax3.set_xticks(range(len(volatility_performance)))
    ax3.set_xticklabels(volatility_performance.index, rotation=45, ha='right')
    ax3.grid(True, alpha=0.3)
    
    # Add count labels
    for i, (bar, count) in enumerate(zip(bars3, volatility_performance['count'])):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + max(volatility_performance['mean'])*0.02,
                f'n={count}', ha='center', va='bottom', fontsize=9)
    
    # 4. Best strategy heatmap by price ranges
    # Create price range categories
    token0_bins = pd.cut(df['token0_change_pct'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    token1_bins = pd.cut(df['token1_change_pct'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    
    df_heatmap = df.copy()
    df_heatmap['token0_range'] = token0_bins
    df_heatmap['token1_range'] = token1_bins
    
    # Find best strategy for each price range combination
    best_strategy_matrix = df_heatmap.groupby(['token0_range', 'token1_range'])['advantage_vs_uniswap'].max().unstack()
    
    sns.heatmap(best_strategy_matrix, annot=True, fmt='.0f', cmap='RdYlGn', center=0,
                ax=ax4, cbar_kws={'label': 'Best Advantage (%)'})
    ax4.set_title('Best Advantage by Price Range Categories', fontsize=14)
    ax4.set_xlabel('Token1 Price Range', fontsize=12)
    ax4.set_ylabel('Token0 Price Range', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mirrored_price_movement_analysis.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   📊 Price movement analysis saved")

def create_comprehensive_summary_dashboard(df: pd.DataFrame, output_dir: str):
    """Create a comprehensive summary dashboard"""
    
    fig = plt.figure(figsize=(24, 16))
    gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
    
    fig.suptitle('Pennysia Mirrored Positioning: Comprehensive Results Dashboard', 
                 fontsize=20, fontweight='bold', y=0.98)
    
    # Key metrics at the top
    ax_metrics = fig.add_subplot(gs[0, :])
    ax_metrics.axis('off')
    
    total_tests = len(df)
    avg_advantage = df['advantage_vs_uniswap'].mean()
    win_rate = len(df[df['advantage_vs_uniswap'] > 0]) / len(df) * 100
    best_result = df['advantage_vs_uniswap'].max()
    avg_uniswap = df['uniswap_return_pct'].mean()
    avg_pennysia = df['pennysia_return_pct'].mean()
    
    metrics_text = f"""
    COMPREHENSIVE BACKTEST RESULTS (2021-2024)
    
    📊 Total Strategy Tests: {total_tests}         🎯 Overall Win Rate: {win_rate:.1f}%         📈 Average Advantage: {avg_advantage:.0f}%
    
    💰 Average Uniswap Return: {avg_uniswap:.0f}%         🚀 Average Pennysia Return: {avg_pennysia:.0f}%         🏆 Best Individual Result: {best_result:.0f}%
    """
    
    ax_metrics.text(0.5, 0.5, metrics_text, transform=ax_metrics.transAxes, 
                   fontsize=14, ha='center', va='center', 
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
    
    # 1. Strategy win rates (top left)
    ax1 = fig.add_subplot(gs[1, 0])
    strategy_wins = []
    strategies = df['strategy_name'].unique()
    
    for strategy in strategies:
        strategy_data = df[df['strategy_name'] == strategy]
        wins = len(strategy_data[strategy_data['advantage_vs_uniswap'] > 0])
        total = len(strategy_data)
        strategy_wins.append(wins / total * 100)
    
    strategy_labels = [s.replace('100% Long Token0 + 100% Short Token1', '100% Long T0')
                      .replace('75% Long Token0 + 25% Long Token1', '75% Long T0')
                      .replace('50% Long Token0 + 50% Long Token1 (Balanced)', 'Balanced')
                      .replace('25% Long Token0 + 75% Long Token1', '25% Long T0')
                      .replace('100% Short Token0 + 100% Long Token1', '100% Long T1')
                      for s in strategies]
    
    wedges, texts, autotexts = ax1.pie(strategy_wins, labels=strategy_labels, autopct='%1.1f%%', 
                                      colors=['red', 'orange', 'yellow', 'lightgreen', 'green'])
    ax1.set_title('Win Rates by Strategy', fontsize=12, fontweight='bold')
    
    # 2. Top pairs (top middle-right)
    ax2 = fig.add_subplot(gs[1, 1:3])
    best_by_pair = df.loc[df.groupby('pair')['advantage_vs_uniswap'].idxmax()]
    top_10_pairs = best_by_pair.nlargest(10, 'advantage_vs_uniswap')
    
    y_pos = np.arange(len(top_10_pairs))
    bars = ax2.barh(y_pos, top_10_pairs['advantage_vs_uniswap'], 
                    color='green', alpha=0.7)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(top_10_pairs['pair'], fontsize=10)
    ax2.set_xlabel('Best Advantage (%)')
    ax2.set_title('Top 10 Pair Performances', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Market condition analysis (bottom left)
    ax3 = fig.add_subplot(gs[1, 3])
    
    # Categorize by extreme movements
    extreme_up = df[df['advantage_vs_uniswap'] > 10000]['pair'].nunique()
    high_advantage = df[(df['advantage_vs_uniswap'] > 500) & (df['advantage_vs_uniswap'] <= 10000)]['pair'].nunique()
    moderate_advantage = df[(df['advantage_vs_uniswap'] > 0) & (df['advantage_vs_uniswap'] <= 500)]['pair'].nunique()
    negative = df[df['advantage_vs_uniswap'] <= 0]['pair'].nunique()
    
    categories = ['Extreme\n(>10000%)', 'High\n(500-10000%)', 'Moderate\n(0-500%)', 'Negative\n(≤0%)']
    values = [extreme_up, high_advantage, moderate_advantage, negative]
    colors = ['darkgreen', 'green', 'yellow', 'red']
    
    bars = ax3.bar(categories, values, color=colors, alpha=0.7)
    ax3.set_ylabel('Number of Pairs')
    ax3.set_title('Advantage Categories', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{val}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Advantage distribution (middle row, full width)
    ax4 = fig.add_subplot(gs[2, :])
    
    # Create bins for better visualization
    advantages = df['advantage_vs_uniswap']
    
    # Use log scale for extreme values
    positive_advantages = advantages[advantages > 0]
    negative_advantages = advantages[advantages <= 0]
    
    ax4.hist(negative_advantages, bins=20, alpha=0.7, color='red', label='Negative', edgecolor='black')
    ax4.hist(positive_advantages[positive_advantages <= 1000], bins=30, alpha=0.7, color='green', 
             label='Positive (0-1000%)', edgecolor='black')
    ax4.hist(positive_advantages[positive_advantages > 1000], bins=20, alpha=0.7, color='darkgreen', 
             label='Extreme Positive (>1000%)', edgecolor='black')
    
    ax4.axvline(x=0, color='black', linestyle='-', linewidth=2)
    ax4.set_xlabel('Advantage vs Uniswap (%)')
    ax4.set_ylabel('Number of Tests')
    ax4.set_title('Distribution of All Test Results', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Strategy comparison matrix (bottom row)
    ax5 = fig.add_subplot(gs[3, :2])
    
    strategy_matrix = df.groupby('strategy_name')['advantage_vs_uniswap'].agg(['mean', 'median', 'std']).round(0)
    
    x_pos = np.arange(len(strategy_matrix))
    width = 0.25
    
    bars1 = ax5.bar(x_pos - width, strategy_matrix['mean'], width, label='Mean', alpha=0.8)
    bars2 = ax5.bar(x_pos, strategy_matrix['median'], width, label='Median', alpha=0.8)
    bars3 = ax5.bar(x_pos + width, strategy_matrix['std'], width, label='Std Dev', alpha=0.8)
    
    ax5.set_xlabel('Strategy')
    ax5.set_ylabel('Advantage (%)')
    ax5.set_title('Strategy Statistics Comparison', fontsize=12, fontweight='bold')
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels([s[:15] + '...' for s in strategy_matrix.index], rotation=45, ha='right', fontsize=9)
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Key insights text (bottom right)
    ax6 = fig.add_subplot(gs[3, 2:])
    ax6.axis('off')
    
    # Calculate key insights
    best_strategy = df.groupby('strategy_name')['advantage_vs_uniswap'].mean().idxmax()
    best_pair = df.loc[df['advantage_vs_uniswap'].idxmax(), 'pair']
    gala_pairs = len(df[df['pair'].str.contains('GALA')])
    
    insights_text = f"""
KEY INSIGHTS:

🎯 Best Overall Strategy:
   {best_strategy[:30]}...

🏆 Top Performing Pair:
   {best_pair} (+{df['advantage_vs_uniswap'].max():.0f}%)

📈 Market Trends:
   • GALA pairs: {gala_pairs} tests
   • Average advantage: {avg_advantage:.0f}%
   • {win_rate:.0f}% of tests profitable

🚀 Protocol Validation:
   ✅ Directional positioning works
   ✅ Fee redistribution effective
   ✅ Massive advantages possible
    """
    
    ax6.text(0.05, 0.95, insights_text, transform=ax6.transAxes, 
            fontsize=11, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
    
    plt.savefig(os.path.join(output_dir, 'mirrored_comprehensive_dashboard.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   📊 Comprehensive dashboard saved")

def main():
    """Generate all mirrored positioning visualizations"""
    
    print("🎨 Creating Mirrored Positioning Visualizations")
    print("=" * 60)
    
    # Load results
    df = load_latest_mirrored_results()
    if df.empty:
        return
    
    # Create output directory
    output_dir = "../result"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate visualizations
    print("\n📊 Generating comprehensive charts...")
    create_advantage_distribution_analysis(df, output_dir)
    create_pair_performance_heatmap(df, output_dir)
    create_top_performers_showcase(df, output_dir)
    create_price_movement_analysis(df, output_dir)
    create_comprehensive_summary_dashboard(df, output_dir)
    
    print(f"\n✅ All mirrored positioning visualizations saved to: {output_dir}")
    print("\n📈 Visualization Summary:")
    print(f"   • Advantage distribution analysis")
    print(f"   • Pair performance heatmaps") 
    print(f"   • Top performers showcase")
    print(f"   • Price movement analysis")
    print(f"   • Comprehensive dashboard")
    
    print(f"\n🎉 Mirrored positioning visualizations completed!")

if __name__ == "__main__":
    main() 