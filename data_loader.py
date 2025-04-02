import pandas as pd
import warnings

def load_and_prepare_data(csv_path, lower_tf_interval='5T', higher_tf_interval='30T'):
    """
    Load data from a CSV file and create multiple timeframes
    
    Parameters:
    csv_path (str): Path to the CSV file
    lower_tf_interval (str): Timeframe interval for the lower timeframe (e.g. '1T', '5T', '15T')
    higher_tf_interval (str): Timeframe interval for the higher timeframe (e.g. '30T', '1H', '4H', '1D')
    
    Returns:
    tuple: (lower_tf_data, higher_tf_data) - DataFrames for each timeframe
    """
    try:
        # Load the raw data without setting index first
        raw_data = pd.read_csv(csv_path)
        
        # Print sample timestamps to debug
        # print("Sample timestamp values:", raw_data['timestamp'].head())
        
        # Convert timestamp column to datetime with dayfirst=True
        try:
            raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'], dayfirst=True)
        except Exception as e:
            print(f"Error converting timestamps: {e}")
            print("Try specifying a format, e.g., pd.to_datetime(raw_data['timestamp'], format='%d/%m/%Y %H:%M')")
            return pd.DataFrame(), pd.DataFrame()
        
        # Set the index after conversion
        raw_data.set_index('timestamp', inplace=True)
        
        # Ensure required columns exist
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in raw_data.columns for col in required_columns):
            missing = [col for col in required_columns if col not in raw_data.columns]
            raise ValueError(f"CSV is missing required columns: {missing}")
        
        # Sort by time to ensure correct resampling
        raw_data = raw_data.sort_index()
        
        print(f"Loaded {len(raw_data)} candles from {csv_path}")
        
        # Generate lower timeframe data by resampling
        lower_tf_data = raw_data.resample(lower_tf_interval).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
        
        print(f"Generated {len(lower_tf_data)} {lower_tf_interval} candles by resampling")
        
        # Generate higher timeframe data by resampling
        higher_tf_data = raw_data.resample(higher_tf_interval).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
        
        print(f"Generated {len(higher_tf_data)} {higher_tf_interval} candles by resampling")
        
        return lower_tf_data.dropna(), higher_tf_data.dropna()
    except Exception as e:
        print(f"Error loading data from CSV: {e}")
        return pd.DataFrame(), pd.DataFrame()