#!/usr/bin/env python3
"""
Comprehensive Mirrored Positioning Test
=======================================

Run all 28 trading pairs with the 5 proper mirrored positioning strategies
and generate complete analysis with correct methodology.
"""

import pandas as pd
import numpy as np
import math
from datetime import datetime
import os
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')

# Import from corrected implementation
from corrected_mirrored_positioning import (
    load_price_data, 
    UniswapV2Pool,
    PennysiaMirroredPool,
    run_mirrored_positioning_test
)

def generate_trading_pairs(tokens: List[str]) -> List[Tuple[str, str]]:
    """Generate all meaningful trading pairs"""
    pairs = []
    
    # Sort tokens to ensure consistent ordering
    tokens = sorted(tokens)
    
    for i, token0 in enumerate(tokens):
        for token1 in tokens[i+1:]:
            pairs.append((token0, token1))
    
    print(f"📋 Generated {len(pairs)} trading pairs from {len(tokens)} tokens")
    return pairs

def save_comprehensive_results(results: List[Dict]) -> pd.DataFrame:
    """Save comprehensive results to CSV and generate summary"""
    
    if not results:
        print("❌ No results to save")
        return pd.DataFrame()
    
    # Flatten results for CSV
    flattened_results = []
    
    for result in results:
        base_data = {
            'pair': result['pair'],
            'token0_change_pct': result['token0_change_pct'],
            'token1_change_pct': result['token1_change_pct'],
            'uniswap_return_pct': result['uniswap_return_pct'],
            'uniswap_final_value': result['uniswap_final_value']
        }
        
        for strategy_name, strategy_data in result['strategies'].items():
            row = base_data.copy()
            row.update({
                'strategy_name': strategy_name,
                'token0_long_pct': strategy_data['token0_long_pct'],
                'token1_long_pct': strategy_data['token1_long_pct'],
                'pennysia_return_pct': strategy_data['return_pct'],
                'pennysia_final_value': strategy_data['final_value'],
                'advantage_vs_uniswap': strategy_data['advantage_pct']
            })
            flattened_results.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(flattened_results)
    
    # Save to CSV with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"../result/comprehensive_mirrored_results_{timestamp}.csv"
    df.to_csv(csv_filename, index=False)
    
    # Generate summary statistics
    summary_filename = f"../result/comprehensive_mirrored_summary_{timestamp}.txt"
    with open(summary_filename, 'w') as f:
        f.write("COMPREHENSIVE MIRRORED POSITIONING TEST RESULTS\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Total pairs analyzed: {len(results)}\n")
        f.write(f"Period: 2021-2024\n")
        f.write(f"Methodology: Proper mirrored positioning with equal base liquidity\n\n")
        
        # Overall statistics
        f.write("OVERALL STATISTICS:\n")
        f.write(f"  Average Uniswap Return: {df['uniswap_return_pct'].mean():+.1f}%\n")
        f.write(f"  Average Pennysia Return: {df['pennysia_return_pct'].mean():+.1f}%\n")
        f.write(f"  Average Advantage: {df['advantage_vs_uniswap'].mean():+.1f}%\n\n")
        
        # Strategy performance
        f.write("STRATEGY PERFORMANCE:\n")
        for strategy in df['strategy_name'].unique():
            strategy_data = df[df['strategy_name'] == strategy]
            avg_advantage = strategy_data['advantage_vs_uniswap'].mean()
            win_rate = len(strategy_data[strategy_data['advantage_vs_uniswap'] > 0]) / len(strategy_data) * 100
            f.write(f"  {strategy[:40]:40} Avg: {avg_advantage:+6.1f}% | Win Rate: {win_rate:5.1f}%\n")
        
        f.write("\n")
        
        # Best performers by pair
        f.write("TOP 10 PAIR ADVANTAGES:\n")
        best_pairs = df.loc[df.groupby('pair')['advantage_vs_uniswap'].idxmax()]
        best_pairs = best_pairs.nlargest(10, 'advantage_vs_uniswap')
        
        for _, row in best_pairs.iterrows():
            f.write(f"  {row['pair']:12} {row['advantage_vs_uniswap']:+6.1f}% ({row['strategy_name'][:20]})\n")
        
        f.write("\n")
        
        # Worst performers
        f.write("BOTTOM 5 PAIR DISADVANTAGES:\n")
        worst_pairs = df.loc[df.groupby('pair')['advantage_vs_uniswap'].idxmin()]
        worst_pairs = worst_pairs.nsmallest(5, 'advantage_vs_uniswap')
        
        for _, row in worst_pairs.iterrows():
            f.write(f"  {row['pair']:12} {row['advantage_vs_uniswap']:+6.1f}% ({row['strategy_name'][:20]})\n")
    
    print(f"📊 Comprehensive results saved:")
    print(f"   CSV: {csv_filename}")
    print(f"   Summary: {summary_filename}")
    
    return df

def main():
    """Run comprehensive mirrored positioning test for all pairs"""
    
    print("🎯 COMPREHENSIVE MIRRORED POSITIONING TEST")
    print("=" * 60)
    print("Testing all trading pairs with 5 proper mirrored positioning strategies:")
    print("1. 100% Long TokenX + 100% Short TokenY")
    print("2. 75% Long TokenX/25% Short TokenX + 25% Long TokenY/75% Short TokenY")
    print("3. 50% Long TokenX/50% Short TokenX + 50% Long TokenY/50% Short TokenY")
    print("4. 25% Long TokenX/75% Short TokenX + 75% Long TokenY/25% Short TokenY")
    print("5. 100% Short TokenX + 100% Long TokenY")
    print()
    
    # Load data
    price_data = load_price_data()
    if price_data.empty:
        print("❌ No price data available")
        return
    
    # Generate all pairs
    available_tokens = list(price_data.columns)
    pairs = generate_trading_pairs(available_tokens)
    
    print(f"\n🚀 Starting comprehensive tests for {len(pairs)} pairs...")
    print("-" * 60)
    
    results = []
    successful = 0
    
    for i, (token0, token1) in enumerate(pairs):
        print(f"\n{i+1:2d}/{len(pairs)} {token0}/{token1}")
        
        if token0 in price_data.columns and token1 in price_data.columns:
            try:
                result = run_mirrored_positioning_test(price_data, token0, token1)
                if result:
                    results.append(result)
                    successful += 1
                    
                    # Show quick results - find best strategy
                    best_strategy = max(result['strategies'].items(), key=lambda x: x[1]['return_pct'])
                    best_advantage = best_strategy[1]['advantage_pct']
                    best_name = best_strategy[0][:25]
                    
                    print(f"   Price changes: {token0} {result['token0_change_pct']:+6.1f}%, {token1} {result['token1_change_pct']:+6.1f}%")
                    print(f"   Uniswap: {result['uniswap_return_pct']:+6.1f}% | Best: {best_name} {best_advantage:+6.1f}%")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print(f"   ❌ Missing price data")
    
    print(f"\n✅ Completed {successful}/{len(pairs)} tests successfully")
    
    # Save and analyze results
    if results:
        df = save_comprehensive_results(results)
        
        # Show final summary statistics
        print(f"\n📈 FINAL COMPREHENSIVE SUMMARY:")
        print(f"   Total Pairs Tested: {len(results)}")
        print(f"   Total Strategy Tests: {len(df)}")
        
        print(f"\n   Average Performance:")
        print(f"     Uniswap V2:           {df['uniswap_return_pct'].mean():+6.1f}%")
        print(f"     Pennysia (All):       {df['pennysia_return_pct'].mean():+6.1f}%")
        print(f"     Average Advantage:    {df['advantage_vs_uniswap'].mean():+6.1f}%")
        
        # Strategy breakdown
        print(f"\n   Strategy Win Rates:")
        for strategy in df['strategy_name'].unique():
            strategy_data = df[df['strategy_name'] == strategy]
            wins = len(strategy_data[strategy_data['advantage_vs_uniswap'] > 0])
            total = len(strategy_data)
            win_rate = wins / total * 100
            avg_adv = strategy_data['advantage_vs_uniswap'].mean()
            print(f"     {strategy[:35]:35} {wins:2d}/{total:2d} ({win_rate:5.1f}%) Avg: {avg_adv:+6.1f}%")
        
        # Best overall results
        print(f"\n🏆 TOP 5 BEST RESULTS:")
        top5 = df.nlargest(5, 'advantage_vs_uniswap')
        for _, row in top5.iterrows():
            print(f"     {row['pair']:12} {row['advantage_vs_uniswap']:+6.1f}% ({row['strategy_name'][:25]})")
    
    print(f"\n🎉 Comprehensive mirrored positioning test completed!")

if __name__ == "__main__":
    main() 