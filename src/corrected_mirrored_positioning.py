#!/usr/bin/env python3
"""
Corrected Mirrored Positioning Test
===================================

Proper implementation of the 5 mirrored positioning strategies:
1. 100% Long TokenX + 100% Short TokenY
2. 75% Long TokenX/25% Short TokenX + 75% Short TokenY/25% Long TokenY
3. 50% Long TokenX/50% Short TokenX + 50% Short TokenY/50% Long TokenY
4. 25% Long TokenX/75% Short TokenX + 25% Short TokenY/75% Long TokenY
5. 100% Short TokenX + 100% Long TokenY
"""

import pandas as pd
import numpy as np
import math
from typing import Tuple, Dict

def load_price_data():
    """Load price data"""
    try:
        import yfinance as yf
        
        symbols = {
            'BTC': 'BTC-USD',
            'ETH': 'ETH-USD', 
            'DOT': 'DOT-USD',
            'CRV': 'CRV-USD',
            'GALA': 'GALA-USD',
            'LINK': 'LINK-USD',
            'USDC': 'USDC-USD',
            'USDT': 'USDT-USD'
        }
        
        print("📥 Loading price data...")
        data = {}
        for symbol, yahoo_symbol in symbols.items():
            try:
                ticker = yf.Ticker(yahoo_symbol)
                hist = ticker.history(start='2021-01-01', end='2024-12-31')
                if not hist.empty:
                    data[symbol] = hist['Close']
                    print(f"   ✅ {symbol}: {len(hist)} days")
            except Exception as e:
                print(f"   ❌ {symbol}: Error - {e}")
        
        return pd.DataFrame(data).dropna()
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return pd.DataFrame()

class UniswapV2Pool:
    """Uniswap V2 Pool Implementation"""
    
    def __init__(self, base_amount0: float, base_amount1: float):
        self.reserve0 = base_amount0
        self.reserve1 = base_amount1
        self.user_lp_tokens = 0
        self.total_lp_supply = math.sqrt(base_amount0 * base_amount1)
        
    def add_user_liquidity(self, amount0: float, amount1: float) -> float:
        """Add user liquidity"""
        lp_tokens = min(
            amount0 * self.total_lp_supply / self.reserve0,
            amount1 * self.total_lp_supply / self.reserve1
        )
        
        self.reserve0 += amount0
        self.reserve1 += amount1
        self.total_lp_supply += lp_tokens
        self.user_lp_tokens += lp_tokens
        
        return lp_tokens
    
    def withdraw_user_liquidity(self) -> Tuple[float, float]:
        """Withdraw user's liquidity"""
        if self.total_lp_supply == 0:
            return 0, 0
            
        user_share = self.user_lp_tokens / self.total_lp_supply
        amount0 = self.reserve0 * user_share
        amount1 = self.reserve1 * user_share
        
        return amount0, amount1

class PennysiaMirroredPool:
    """Pennysia Pool with Mirrored Positioning"""
    
    def __init__(self, base_amount0: float, base_amount1: float):
        # Base liquidity (50% long, 50% short for both tokens)
        self.reserve0Long = base_amount0 / 2
        self.reserve0Short = base_amount0 / 2
        self.reserve1Long = base_amount1 / 2
        self.reserve1Short = base_amount1 / 2
        
        # Track user positions
        self.user_token0_long = 0
        self.user_token0_short = 0
        self.user_token1_long = 0
        self.user_token1_short = 0
    
    def add_user_liquidity(self, amount0: float, amount1: float, 
                          token0_long_pct: float, token1_long_pct: float):
        """Add user liquidity with specified positioning
        
        Args:
            amount0: Amount of token0 to add
            amount1: Amount of token1 to add
            token0_long_pct: Percentage of token0 that goes to long positions (0-100)
            token1_long_pct: Percentage of token1 that goes to long positions (0-100)
        """
        # User's token0 allocation
        self.user_token0_long = amount0 * (token0_long_pct / 100)
        self.user_token0_short = amount0 * ((100 - token0_long_pct) / 100)
        
        # User's token1 allocation
        self.user_token1_long = amount1 * (token1_long_pct / 100)
        self.user_token1_short = amount1 * ((100 - token1_long_pct) / 100)
        
        # Add to pool reserves
        self.reserve0Long += self.user_token0_long
        self.reserve0Short += self.user_token0_short
        self.reserve1Long += self.user_token1_long
        self.reserve1Short += self.user_token1_short
    
    def simulate_market_performance(self, price0_multiplier: float, price1_multiplier: float) -> Tuple[float, float]:
        """Simulate final values after market movements with Market.sol mechanics"""
        
        # Simulate fee advantages for long positions (from Market.sol fee redistribution)
        fee_advantage = 1.05  # 5% advantage over period
        
        # Long positions benefit from price increases AND fee advantages
        long0_growth = price0_multiplier * fee_advantage
        long1_growth = price1_multiplier * fee_advantage
        
        # Short positions benefit when prices decrease (inverse relationship)
        short0_growth = max(0.1, 2 - price0_multiplier)  # Floor at 10% to avoid total loss
        short1_growth = max(0.1, 2 - price1_multiplier)  # Floor at 10% to avoid total loss
        
        # Calculate user's final amounts based on position growth
        final_amount0 = (self.user_token0_long * long0_growth + 
                        self.user_token0_short * short0_growth)
        final_amount1 = (self.user_token1_long * long1_growth + 
                        self.user_token1_short * short1_growth)
        
        return final_amount0, final_amount1

def run_mirrored_positioning_test(price_data: pd.DataFrame, token0: str, token1: str) -> Dict:
    """Test all 5 mirrored positioning strategies"""
    
    if token0 not in price_data.columns or token1 not in price_data.columns:
        return {}
    
    price0_series = price_data[token0].dropna()
    price1_series = price_data[token1].dropna()
    
    # Align series
    common_dates = price0_series.index.intersection(price1_series.index)
    price0_series = price0_series.loc[common_dates]
    price1_series = price1_series.loc[common_dates]
    
    if len(price0_series) < 100:
        return {}
    
    # Calculate price changes
    price0_multiplier = price0_series.iloc[-1] / price0_series.iloc[0]
    price1_multiplier = price1_series.iloc[-1] / price1_series.iloc[0]
    
    price0_change_pct = (price0_multiplier - 1) * 100
    price1_change_pct = (price1_multiplier - 1) * 100
    
    # Setup: Equal base liquidity + equal user investment
    total_investment = 100000
    base_liquidity = 50000
    user_investment = 50000
    
    initial_price0 = price0_series.iloc[0]
    initial_price1 = price1_series.iloc[0]
    final_price0 = price0_series.iloc[-1]
    final_price1 = price1_series.iloc[-1]
    
    # Base liquidity amounts (50/50 split)
    base_amount0 = (base_liquidity / 2) / initial_price0
    base_amount1 = (base_liquidity / 2) / initial_price1
    
    # User investment amounts (50/50 split)
    user_amount0 = (user_investment / 2) / initial_price0
    user_amount1 = (user_investment / 2) / initial_price1
    
    # Test Uniswap V2 baseline
    uniswap_pool = UniswapV2Pool(base_amount0, base_amount1)
    uniswap_pool.add_user_liquidity(user_amount0, user_amount1)
    
    # Simulate impermanent loss for Uniswap V2
    price_ratio_change = price1_multiplier / price0_multiplier
    final_uni_amount0 = user_amount0 / math.sqrt(price_ratio_change)
    final_uni_amount1 = user_amount1 * math.sqrt(price_ratio_change)
    
    # Add modest fee boost for Uniswap
    fee_boost = 1.03  # 3% fee collection over period
    final_uni_amount0 *= fee_boost
    final_uni_amount1 *= fee_boost
    
    uniswap_final_value = final_uni_amount0 * final_price0 + final_uni_amount1 * final_price1
    uniswap_return = (uniswap_final_value / user_investment - 1) * 100
    
    # Define the 5 mirrored positioning strategies
    strategies = [
        {
            'name': '100% Long Token0 + 100% Short Token1',
            'token0_long_pct': 100,  # 100% of token0 goes long
            'token1_long_pct': 0     # 0% of token1 goes long (100% short)
        },
        {
            'name': '75% Long Token0 + 25% Long Token1', 
            'token0_long_pct': 75,   # 75% long token0, 25% short token0
            'token1_long_pct': 25    # 25% long token1, 75% short token1
        },
        {
            'name': '50% Long Token0 + 50% Long Token1 (Balanced)',
            'token0_long_pct': 50,   # 50% long token0, 50% short token0
            'token1_long_pct': 50    # 50% long token1, 50% short token1
        },
        {
            'name': '25% Long Token0 + 75% Long Token1',
            'token0_long_pct': 25,   # 25% long token0, 75% short token0
            'token1_long_pct': 75    # 75% long token1, 25% short token1
        },
        {
            'name': '100% Short Token0 + 100% Long Token1',
            'token0_long_pct': 0,    # 0% of token0 goes long (100% short)
            'token1_long_pct': 100   # 100% of token1 goes long
        }
    ]
    
    results = {
        'pair': f"{token0}/{token1}",
        'token0_change_pct': price0_change_pct,
        'token1_change_pct': price1_change_pct,
        'uniswap_return_pct': uniswap_return,
        'uniswap_final_value': uniswap_final_value,
        'strategies': {}
    }
    
    # Test each strategy
    for strategy in strategies:
        pennysia_pool = PennysiaMirroredPool(base_amount0, base_amount1)
        pennysia_pool.add_user_liquidity(
            user_amount0, user_amount1,
            strategy['token0_long_pct'], strategy['token1_long_pct']
        )
        
        # Simulate market performance
        final_amount0, final_amount1 = pennysia_pool.simulate_market_performance(
            price0_multiplier, price1_multiplier
        )
        
        pennysia_final_value = final_amount0 * final_price0 + final_amount1 * final_price1
        pennysia_return = (pennysia_final_value / user_investment - 1) * 100
        advantage = pennysia_return - uniswap_return
        
        results['strategies'][strategy['name']] = {
            'final_value': pennysia_final_value,
            'return_pct': pennysia_return,
            'advantage_pct': advantage,
            'token0_long_pct': strategy['token0_long_pct'],
            'token1_long_pct': strategy['token1_long_pct']
        }
    
    return results

def main():
    """Run the corrected mirrored positioning test"""
    
    print("🎯 CORRECTED MIRRORED POSITIONING TEST")
    print("=" * 60)
    print("Testing the 5 proper mirrored positioning strategies:")
    print("1. 100% Long TokenX + 100% Short TokenY")
    print("2. 75% Long TokenX/25% Short TokenX + 25% Long TokenY/75% Short TokenY")
    print("3. 50% Long TokenX/50% Short TokenX + 50% Long TokenY/50% Short TokenY")
    print("4. 25% Long TokenX/75% Short TokenX + 75% Long TokenY/25% Short TokenY")
    print("5. 100% Short TokenX + 100% Long TokenY")
    print()
    
    # Load data
    price_data = load_price_data()
    if price_data.empty:
        return
    
    # Test key pairs
    test_pairs = [('BTC', 'ETH'), ('ETH', 'USDC'), ('BTC', 'USDC'), ('DOT', 'USDC'), ('CRV', 'USDC')]
    
    for token0, token1 in test_pairs:
        print(f"\n📊 {token0}/{token1}")
        
        result = run_mirrored_positioning_test(price_data, token0, token1)
        if not result:
            print("   ❌ Insufficient data")
            continue
        
        print(f"   Price changes: {token0} {result['token0_change_pct']:+.1f}%, {token1} {result['token1_change_pct']:+.1f}%")
        print(f"   Uniswap V2: {result['uniswap_return_pct']:+.1f}% (${result['uniswap_final_value']:,.0f})")
        print("   Pennysia Mirrored Strategies:")
        
        for strategy_name, strategy_data in result['strategies'].items():
            t0_long = strategy_data['token0_long_pct']
            t1_long = strategy_data['token1_long_pct']
            advantage = strategy_data['advantage_pct']
            return_pct = strategy_data['return_pct']
            
            print(f"     {strategy_name[:40]:40} {return_pct:+6.1f}% (Adv: {advantage:+5.1f}%) [{t0_long}%L{token0}/{t1_long}%L{token1}]")
        
        # Find best strategy
        best_strategy = max(result['strategies'].items(), key=lambda x: x[1]['return_pct'])
        print(f"   🏆 Best: {best_strategy[0][:30]} with {best_strategy[1]['advantage_pct']:+.1f}% advantage")
    
    print(f"\n🎉 Corrected mirrored positioning test completed!")

if __name__ == "__main__":
    main() 