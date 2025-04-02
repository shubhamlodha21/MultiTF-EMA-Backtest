def calculate_emas(data, short_period, long_period):
    """
    Calculate EMAs for the given data with specified periods
    
    Parameters:
    data (DataFrame): Price data with 'close' column
    short_period (int): Period for short EMA
    long_period (int): Period for long EMA
    
    Returns:
    DataFrame: Original data with 'EMA_Short' and 'EMA_Long' columns added
    """
    df = data.copy()
    df['EMA_Short'] = df['close'].ewm(span=short_period, adjust=False).mean()
    df['EMA_Long'] = df['close'].ewm(span=long_period, adjust=False).mean()
    return df

def determine_trend(higher_tf_data, timestamp):
    """
    Determine the trend on the higher timeframe at the given timestamp
    
    Parameters:
    higher_tf_data (DataFrame): Higher timeframe data with EMA columns
    timestamp (datetime): Timestamp to check trend at
    
    Returns:
    str: 'Bullish', 'Bearish', or 'Neutral'
    """
    # Find the most recent candle on the higher timeframe
    prev_candles = higher_tf_data[higher_tf_data.index <= timestamp]
    
    if prev_candles.empty:
        return 'Neutral'  # Default to neutral if no data
    
    latest_candle = prev_candles.iloc[-1]
    
    # Determine trend based on EMA crossover
    # Access the scalar values to avoid Series comparison ambiguity
    ema_short_value = float(latest_candle['EMA_Short'])
    ema_long_value = float(latest_candle['EMA_Long'])
    
    if ema_short_value > ema_long_value:
        return 'Bullish'
    elif ema_short_value < ema_long_value:
        return 'Bearish'
    else:
        return 'Neutral'