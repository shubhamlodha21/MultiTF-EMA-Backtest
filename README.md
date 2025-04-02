# MulitTF-EMA-Strategy-BackTesting

A Python-based backtesting framework for multi-timeframe EMA crossover trading strategies in cryptocurrency markets.

## 📈 Overview

This project provides a comprehensive solution for backtesting a dual timeframe EMA crossover strategy on cryptocurrency price data. The strategy uses two different timeframes (e.g., 30-minute and 4-hour) with exponential moving average crossovers to generate trading signals, integrating higher timeframe trend confirmation with lower timeframe entries.

### Key Features

- **Multi-timeframe Analysis**: Combines higher timeframe trend detection with lower timeframe entry signals
- **EMA Crossover Strategy**: Uses exponential moving average crossovers as the primary signal generator
- **Risk Management**: Implements stop loss and take profit based on configurable risk parameters
- **Detailed Performance Metrics**: Comprehensive reporting including win rate, profit factor, drawdown analysis, and more
- **QuantStats Integration**: Optional advanced performance analytics using the QuantStats library

## 🔧 System Requirements

- Python 3.7+
- pandas
- numpy
- quantstats (optional, for advanced reporting)

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CryptoTrader-MTF-Strategy.git
   cd CryptoTrader-MTF-Strategy
   ```

2. Install dependencies:
   ```bash
   pip install pandas numpy
   pip install quantstats  # Optional, for advanced performance metrics
   ```

## 📊 Data Format

The system expects a CSV file with cryptocurrency price data in the following format:

- Required columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`
- Timestamp should be in a format that pandas can parse

Example:
```csv
timestamp,open,high,low,close,volume
2023-01-01 00:00:00,16500.25,16550.75,16475.50,16525.30,125.75
2023-01-01 00:05:00,16525.30,16540.20,16510.40,16530.10,98.23
...
```

## 🚀 Usage

### Basic Usage

```python
from Strategy import run_multi_timeframe_backtest

# Run a backtest
trades, equity_curve, returns_df, metrics = run_multi_timeframe_backtest(
    csv_path="bitcoin_data.csv",  # Path to your price data
    lower_tf='30T',               # 30-minute timeframe
    higher_tf='4h',               # 4-hour timeframe
    lower_ema_short=9,            # 9-period EMA on lower timeframe
    lower_ema_long=21,            # 21-period EMA on lower timeframe
    higher_ema_short=9,           # 9-period EMA on higher timeframe
    higher_ema_long=21,           # 21-period EMA on higher timeframe
    risk_percent=1,               # 1% risk per trade
    risk_reward_ratio=2,          # Risk-Reward ratio of 2
    initial_capital=100,          # Initial capital of $100
    lot_size=0.01                 # Position size of 0.01 BTC
)
```

### Running from the Command Line

You can also run the backtest directly using the `main.py` script:

```bash
python main.py
```

Edit the parameters in `main.py` to configure your backtest settings.

## 🔄 Operational Structure

The system operates through a series of interconnected components that handle different aspects of the backtesting process:

1. **Data Loading & Preparation** (`data_loader.py`):
   - Reads price data from CSV file
   - Converts timestamps to datetime format
   - Resamples data to create lower and higher timeframes
   - Returns prepared DataFrames for both timeframes

2. **Technical Indicator Calculation** (`technical_indicators.py`):
   - Calculates EMAs for both timeframes
   - Provides trend determination functionality
   - Supports the core signal generation logic

3. **Strategy Execution** (`Strategy.py`):
   - Orchestrates the entire backtesting process
   - Connects data loading, indicator calculation, and backtesting
   - Initiates performance reporting

4. **Backtesting Engine** (`backtesting.py`):
   - Simulates trading based on strategy signals
   - Implements risk management rules
   - Tracks positions, equity, and returns
   - Records trade details and portfolio performance

5. **Performance Reporting** (`Reports.py`):
   - Calculates performance metrics
   - Generates detailed trade and portfolio statistics
   - Integrates with QuantStats for advanced analytics
   - Produces formatted output reports

6. **Main Entry Point** (`main.py`):
   - Configures backtest parameters
   - Launches the backtest process
   - Sets up environment for results display

### Data Flow

```
                   +---------------+
                   |    main.py    |
                   | (Entry Point) |
                   +-------+-------+
                           |
                           v
                 +-------------------+
                 |    Strategy.py    |
                 | (Orchestration)   |
                 +--------+----------+
                          |
             +------------+------------+
             |                         |
             v                         v
    +----------------+        +----------------+
    | data_loader.py |        |technical_ind.py|
    | (Data Prep)    |        | (Indicators)   |
    +-------+--------+        +--------+-------+
            |                          |
            v                          v
    +-----------------------------+
    |       backtesting.py       |
    | (Trading Simulation)       |
    +-------------+--------------+
                  |
                  v
          +--------------+
          |  Reports.py  |
          | (Analytics)  |
          +--------------+
```

## 📋 Strategy Logic

The strategy operates on the following principles:

1. **Higher Timeframe Trend Detection**:
   - Uses EMA crossovers on the higher timeframe to determine the overall market trend
   - A bullish trend is identified when the short EMA is above the long EMA
   - A bearish trend is identified when the short EMA is below the long EMA

2. **Lower Timeframe Signal Generation**:
   - Looks for EMA crossovers on the lower timeframe to generate entry signals
   - Enters long positions when the short EMA crosses above the long EMA, but only if the higher timeframe trend is bullish
   - Enters short positions when the short EMA crosses below the long EMA, but only if the higher timeframe trend is bearish

3. **Risk Management**:
   - Sets stop loss based on a percentage of the entry price
   - Sets take profit based on a fixed risk-reward ratio
   - Exits trades when the higher timeframe trend changes

## 📈 Performance Metrics

The backtest generates comprehensive performance metrics including:

- **Basic Performance**: Win rate, total trades, total profit, final capital
- **Risk Metrics**: Maximum drawdown, profit factor, annualized return
- **Trade Analysis**: Long vs short trade performance, exit reason analysis
- **QuantStats Metrics** (if available): Sharpe ratio, Sortino ratio, CAGR, volatility, and more

## 📂 Project Structure

- `main.py`: Entry point for running the backtest
- `Strategy.py`: Main strategy implementation and backtest runner
- `data_loader.py`: Functions for loading and preparing price data
- `technical_indicators.py`: Technical indicator calculations (EMAs, trend detection)
- `backtesting.py`: Backtesting engine for simulating trades
- `Reports.py`: Performance reporting and metrics calculation

## 🛠️ Customization

### Timeframes

The system supports any pandas-compatible time frequency string:
- Minutes: '1T', '5T', '15T', '30T'
- Hours: '1H', '2H', '4H'  
- Days: '1D'

### EMA Periods

You can customize the EMA periods for both timeframes. Common settings include:
- Fast/Short EMA: 9, 12, 20 periods
- Slow/Long EMA: 21, 26, 50, 200 periods

### Risk Parameters

Adjust risk parameters to match your trading style:
- `risk_percent`: Percentage of entry price for stop loss placement
- `risk_reward_ratio`: Ratio between potential profit and risk
- `lot_size`: Size of positions in standard lots or units

## 🔄 Future Improvements

Potential enhancements for the system:

- [ ] Additional technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Machine learning integration for parameter optimization
- [ ] Real-time data feeds for live trading
- [ ] Web interface for visualization and interaction
- [ ] Support for equity and forex markets

## 📝 License

[MIT License](LICENSE)

## 👨‍💻 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please open an issue in the GitHub repository.
