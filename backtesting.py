import pandas as pd
from technical_indicators import determine_trend

def backtest_strategy(lower_tf_data, higher_tf_data, initial_capital=500, lot_size=0.1, risk_percent=1.0, risk_reward_ratio=2):
    """
    Backtest the multi-timeframe EMA crossover strategy
    
    Parameters:
    lower_tf_data (DataFrame): Lower timeframe data with EMAs
    higher_tf_data (DataFrame): Higher timeframe data with EMAs
    initial_capital (float): Starting capital amount
    lot_size (float): Size of each position
    risk_percent (float): Risk percentage for stop loss
    risk_reward_ratio (float): Risk-reward ratio for take profit
    
    Returns:
    tuple: (trades_df, equity_curve, returns_df)
    """
    if lower_tf_data.empty or higher_tf_data.empty:
        print("Cannot run backtest: Missing data")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    trades = []
    position = None
    entry_price = 0
    stop_loss = 0
    take_profit = 0
    
    # Create a dataframe to track returns
    returns_df = pd.DataFrame(index=lower_tf_data.index)
    returns_df['return'] = 0.0
    
    # Track capital over time
    capital = initial_capital
    portfolio_value = [capital]
    dates = [lower_tf_data.index[0]]
    positions_size = [0]  # Start with 0 since no position at beginning
    
    # Track signals for later analysis
    signal_counts = {'Long': 0, 'Short': 0}
    
    for i in range(1, len(lower_tf_data)):
        row = lower_tf_data.iloc[i]
        prev_row = lower_tf_data.iloc[i-1]
        
        # Get scalar values for the current row
        try:
            current_high = float(row['high'])
            current_low = float(row['low'])
            current_close = float(row['close'])
            current_ema_short = float(row['EMA_Short'])
            current_ema_long = float(row['EMA_Long'])
            
            # Get scalar values for the previous row
            prev_ema_short = float(prev_row['EMA_Short'])
            prev_ema_long = float(prev_row['EMA_Long'])
        except (ValueError, TypeError) as e:
            continue  # Skip this iteration if data conversion fails
        
        # Determine the higher timeframe trend
        current_trend = determine_trend(higher_tf_data, row.name)
        
        trade_made = False
        pnl = 0
        
        # Check for EMA crossover (Long signal) AND higher timeframe is bullish
        if prev_ema_short <= prev_ema_long and current_ema_short > current_ema_long and current_trend == 'Bullish':
            signal_counts['Long'] += 1  # Track long signal
            
            if position:
                # Calculate PnL based on position size
                if position == 'Long':
                    pnl = (current_close - entry_price) * lot_size
                else:  # Short
                    pnl = (entry_price - current_close) * lot_size
                capital += pnl
                trades.append({
                    'Entry': entry_price, 
                    'Exit': current_close, 
                    'Type': position, 
                    'P&L': pnl,
                    'Date': row.name,
                    'Reason': 'New Signal',
                    'Size': lot_size
                })
                trade_made = True
            
            position = 'Long'
            entry_price = current_close
            stop_loss = entry_price - (entry_price * risk_percent / 100)
            take_profit = entry_price + (entry_price - stop_loss) * risk_reward_ratio
            
        # Check for EMA crossover (Short signal) AND higher timeframe is bearish
        elif prev_ema_short >= prev_ema_long and current_ema_short < current_ema_long and current_trend == 'Bearish':
            signal_counts['Short'] += 1  # Track short signal
            
            if position:
                # Calculate PnL based on position size
                if position == 'Long':
                    pnl = (current_close - entry_price) * lot_size
                else:  # Short
                    pnl = (entry_price - current_close) * lot_size
                capital += pnl
                trades.append({
                    'Entry': entry_price, 
                    'Exit': current_close, 
                    'Type': position, 
                    'P&L': pnl,
                    'Date': row.name,
                    'Reason': 'New Signal',
                    'Size': lot_size
                })
                trade_made = True
            
            position = 'Short'
            entry_price = current_close
            stop_loss = entry_price + (entry_price * risk_percent / 100)
            take_profit = entry_price - (stop_loss - entry_price) * risk_reward_ratio
        
        # Exit trades if higher timeframe trend changes against position
        elif (position == 'Long' and current_trend == 'Bearish') or (position == 'Short' and current_trend == 'Bullish'):
            if position:  # Check if we have an open position
                # Calculate PnL based on position size
                if position == 'Long':
                    pnl = (current_close - entry_price) * lot_size
                else:  # Short
                    pnl = (entry_price - current_close) * lot_size
                capital += pnl
                trades.append({
                    'Entry': entry_price, 
                    'Exit': current_close, 
                    'Type': position, 
                    'P&L': pnl,
                    'Date': row.name,
                    'Reason': 'Trend Change',
                    'Size': lot_size
                })
                position = None
                trade_made = True
        
        # Check for hitting SL/TP for Long positions
        elif position == 'Long':
            if current_low <= stop_loss or current_high >= take_profit:
                exit_price = stop_loss if current_low <= stop_loss else take_profit
                pnl = (exit_price - entry_price) * lot_size
                capital += pnl
                reason = 'Stop Loss' if current_low <= stop_loss else 'Take Profit'
                trades.append({
                    'Entry': entry_price, 
                    'Exit': exit_price, 
                    'Type': 'Long', 
                    'P&L': pnl,
                    'Date': row.name,
                    'Reason': reason,
                    'Size': lot_size
                })
                position = None
                trade_made = True
        
        # Check for hitting SL/TP for Short positions
        elif position == 'Short':
            if current_high >= stop_loss or current_low <= take_profit:
                exit_price = stop_loss if current_high >= stop_loss else take_profit
                pnl = (entry_price - exit_price) * lot_size
                capital += pnl
                reason = 'Stop Loss' if current_high >= stop_loss else 'Take Profit'
                trades.append({
                    'Entry': entry_price, 
                    'Exit': exit_price, 
                    'Type': 'Short', 
                    'P&L': pnl,
                    'Date': row.name,
                    'Reason': reason,
                    'Size': lot_size
                })
                position = None
                trade_made = True
        
        # Record the portfolio value and position size
        portfolio_value.append(capital)
        dates.append(row.name)
        positions_size.append(lot_size if position else 0)
        
        # Record return for this period if a trade was made
        if trade_made:
            returns_df.at[row.name, 'return'] = pnl / (capital - pnl) if (capital - pnl) != 0 else 0
    
    # Create equity curve dataframe
    equity_curve = pd.DataFrame({
        'portfolio_value': portfolio_value,
        'position_size': positions_size
    }, index=dates)
    
    # Add signal counts to equity curve for later reporting
    equity_curve.attrs['signal_counts'] = signal_counts
    
    # Calculate returns for analysis (safely)
    try:
        # Fill in the missing values to get continuous returns series
        returns_df = returns_df.fillna(0)
    except Exception as e:
        print(f"Warning: Could not prepare returns: {e}")
    
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame(columns=['Entry', 'Exit', 'Type', 'P&L', 'Date', 'Reason', 'Size'])
    
    return trades_df, equity_curve, returns_df