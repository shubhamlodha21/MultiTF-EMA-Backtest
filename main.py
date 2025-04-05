import pandas as pd
import warnings
from Strategy import run_multi_timeframe_backtest

if __name__ == "__main__":
    # Suppress warnings
    warnings.filterwarnings('ignore')
    
    # Set pandas display options for better readability
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 120)
    
    # Configure and run the backtest
    trades, equity_curve, returns_df, metrics = run_multi_timeframe_backtest(
        csv_path="bitcoin_data.csv",  # Path to your CSV file with price data
        lower_tf='30T',                # 5-minute timeframe
        higher_tf='4h',              # 4-hour timeframe
        lower_ema_short=9,            # 9-period EMA on lower timeframe
        lower_ema_long=21,            # 21-period EMA on lower timeframe
        higher_ema_short=9,           # 9-period EMA on higher timeframe
        higher_ema_long=21,           # 21-period EMA on higher timeframe
        risk_percent=1,               # 1% risk per trade
        risk_reward_ratio=2,          # Risk-Reward ratio of 2
        initial_capital=100,          # Initial capital of $100
        lot_size=0.01)                # Lot size - 0.01
