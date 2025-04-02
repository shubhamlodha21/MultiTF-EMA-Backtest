from data_loader import load_and_prepare_data
from technical_indicators import calculate_emas
from backtesting import backtest_strategy
from Reports import generate_detailed_report

def run_multi_timeframe_backtest(csv_path, lower_tf='5T', higher_tf='30T', 
                               lower_ema_short=9, lower_ema_long=21,
                               higher_ema_short=9, higher_ema_long=21,
                               risk_percent=1.0, risk_reward_ratio=2,
                               initial_capital=500, lot_size=0.1):
    """
    Run a multi-timeframe backtest with configurable parameters
    
    Parameters:
    csv_path (str): Path to the CSV file with price data
    lower_tf (str): Lower timeframe interval (e.g. '1T', '5T', '15T')
    higher_tf (str): Higher timeframe interval (e.g. '30T', '1H', '4H', '1D')
    lower_ema_short (int): Short EMA period for lower timeframe
    lower_ema_long (int): Long EMA period for lower timeframe
    higher_ema_short (int): Short EMA period for higher timeframe
    higher_ema_long (int): Long EMA period for higher timeframe
    risk_percent (float): Risk percentage for stop loss
    risk_reward_ratio (float): Risk-reward ratio for take profit
    initial_capital (float): Initial capital amount in dollars
    lot_size (float): Size of each position in standard lots
    
    Returns:
    tuple: (trades, equity_curve, returns_df, metrics)
    """
    print(f"Starting multi-timeframe backtest using data from {csv_path}...")
    print(f"Lower TF: {lower_tf}, EMAs: {lower_ema_short}/{lower_ema_long}")
    print(f"Higher TF: {higher_tf}, EMAs: {higher_ema_short}/{higher_ema_long}")
    print(f"Risk: {risk_percent}%, RR: {risk_reward_ratio}")
    print(f"Initial Capital: ${initial_capital}, Lot Size: {lot_size}")
    
    # Load and prepare data from the CSV file
    lower_tf_data, higher_tf_data = load_and_prepare_data(csv_path, lower_tf, higher_tf)
    
    if lower_tf_data.empty or higher_tf_data.empty:
        print("Error: Could not load required data from CSV file. Exiting.")
        return None, None, None, None
    
    # Calculate EMAs for both timeframes
    lower_tf_data = calculate_emas(lower_tf_data, lower_ema_short, lower_ema_long)
    higher_tf_data = calculate_emas(higher_tf_data, higher_ema_short, higher_ema_long)
    
    # Run the backtest
    trades, equity_curve, returns_df = backtest_strategy(
        lower_tf_data, higher_tf_data, initial_capital, lot_size, risk_percent, risk_reward_ratio
    )
    
    # Generate report
    metrics = None
    if not trades.empty:
        metrics = generate_detailed_report(
            trades, equity_curve, returns_df,
            lower_tf, higher_tf,
            lower_ema_short, lower_ema_long,
            higher_ema_short, higher_ema_long,
            risk_percent, risk_reward_ratio,
            initial_capital, lot_size
        )
    else:
        print("No trades were executed during the backtest period.")
    
    return trades, equity_curve, returns_df, metrics