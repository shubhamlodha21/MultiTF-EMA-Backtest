import pandas as pd
import numpy as np
from datetime import timedelta
import warnings
import quantstats

# Try to import quantstats
try:
    import quantstats as qs
    QUANTSTATS_AVAILABLE = True
except ImportError:
    QUANTSTATS_AVAILABLE = False
    warnings.warn("QuantStats not available. Install with 'pip install quantstats' for advanced reporting.")

def generate_detailed_report(trades, equity_curve, returns_df, lower_tf, higher_tf, lower_ema_short, lower_ema_long, 
                            higher_ema_short, higher_ema_long, risk_percent, risk_reward_ratio, initial_capital, lot_size,
                            symbol="", start_date="", end_date=""):
    """
    Generate a detailed performance report for the backtest
    
    Parameters:
    trades (DataFrame): Trades executed during backtest
    equity_curve (DataFrame): Portfolio equity curve over time
    returns_df (DataFrame): Returns data
    lower_tf, higher_tf (str): Lower and higher timeframe intervals
    lower_ema_short, lower_ema_long (int): Short/long EMA periods for lower timeframe
    higher_ema_short, higher_ema_long (int): Short/long EMA periods for higher timeframe
    risk_percent (float): Risk percentage for stop loss
    risk_reward_ratio (float): Risk-reward ratio for take profit
    initial_capital (float): Initial capital amount
    lot_size (float): Size of each position
    symbol, start_date, end_date (str): Trading symbol and date range
    
    Returns:
    dict: Performance metrics
    """
    if trades.empty:
        print("No trades executed.")
        return None
    
    # Initialize metrics dictionary with basic info
    metrics = {
        'symbol': symbol,
        'start_date': start_date,
        'end_date': end_date
    }
    
    # Calculate basic trade statistics
    trades['Win'] = trades['P&L'] > 0
    metrics['win_rate'] = trades['Win'].mean() * 100
    metrics['total_trades'] = len(trades)
    metrics['total_profit'] = trades['P&L'].sum()
    metrics['avg_profit'] = trades['P&L'].mean()
    
    # Separate profitable and losing trades
    profitable_trades = trades[trades['P&L'] > 0]
    losing_trades = trades[trades['P&L'] <= 0]
    
    metrics['profitable_trades'] = len(profitable_trades)
    metrics['losing_trades'] = len(losing_trades)
    metrics['profit_from_winners'] = profitable_trades['P&L'].sum()
    metrics['loss_from_losers'] = losing_trades['P&L'].sum()
    
    # Calculate returns metrics
    if initial_capital > 0:
        metrics['returns_from_winners'] = (metrics['profit_from_winners'] / initial_capital) * 100
        metrics['returns_from_losers'] = (metrics['loss_from_losers'] / initial_capital) * 100
    else:
        metrics['returns_from_winners'] = metrics['returns_from_losers'] = 0
    
    # Long vs Short trade analysis
    metrics['num_long_trades'] = len(trades[trades['Type'] == 'Long'])
    metrics['num_short_trades'] = len(trades[trades['Type'] == 'Short'])
    
    # Signal counts
    signal_counts = getattr(equity_curve, 'attrs', {}).get('signal_counts', {'Long': 0, 'Short': 0})
    metrics['total_signals'] = signal_counts['Long'] + signal_counts['Short']
    
    # Calculate profit factor
    metrics['profit_factor'] = (metrics['profit_from_winners'] / abs(metrics['loss_from_losers']) 
                              if metrics['loss_from_losers'] < 0 else float('inf'))
    
    # Portfolio performance
    metrics['final_capital'] = equity_curve['portfolio_value'].iloc[-1]
    metrics['total_return_pct'] = ((metrics['final_capital'] - initial_capital) / initial_capital) * 100
    
    # Calculate drawdown
    try:
        equity_curve['drawdown'] = equity_curve['portfolio_value'].cummax() - equity_curve['portfolio_value']
        equity_curve['drawdown_pct'] = equity_curve['drawdown'] / equity_curve['portfolio_value'].cummax()
        metrics['max_drawdown'] = equity_curve['drawdown_pct'].max() * 100
    except Exception as e:
        print(f"Warning: Could not calculate drawdown: {e}")
        metrics['max_drawdown'] = 0
    
    # Calculate trade durations and market time
    try:
        trades['Date'] = pd.to_datetime(trades['Date'])
        
        # Calculate trade durations
        trades['Duration'] = pd.Series(dtype='timedelta64[ns]')
        for i in range(1, len(trades)):
            if i > 0:
                trades.loc[trades.index[i], 'Duration'] = trades.loc[trades.index[i], 'Date'] - trades.loc[trades.index[i-1], 'Date']
        
        metrics['avg_duration'] = trades['Duration'].mean()
        
        # Calculate market time metrics
        total_time = equity_curve.index[-1] - equity_curve.index[0]
        metrics['total_days'] = total_time.total_seconds() / (24 * 60 * 60)
        
        # Calculate days in market
        in_market = equity_curve[equity_curve['position_size'] > 0]
        metrics['days_in_market'] = (in_market.index[-1] - in_market.index[0]).days if not in_market.empty else 0
        metrics['days_in_market_pct'] = (metrics['days_in_market'] / metrics['total_days']) * 100 if metrics['total_days'] > 0 else 0
        metrics['time_in_market_pct'] = len(in_market) / len(equity_curve) * 100
    except Exception as e:
        print(f"Warning: Could not calculate trade duration: {e}")
        metrics['avg_duration'] = pd.NaT
        metrics['total_days'] = metrics['days_in_market'] = metrics['days_in_market_pct'] = metrics['time_in_market_pct'] = 0
    
    # Calculate win/loss metrics
    metrics['avg_win'] = profitable_trades['P&L'].mean() if len(profitable_trades) > 0 else 0
    metrics['avg_loss'] = losing_trades['P&L'].mean() if len(losing_trades) > 0 else 0
    metrics['win_loss_ratio'] = abs(metrics['avg_win'] / metrics['avg_loss']) if metrics['avg_loss'] != 0 else float('inf')
    
    # Calculate annualized return
    try:
        days_in_market_total = (equity_curve.index[-1] - equity_curve.index[0]).days
        metrics['days_in_market_total'] = days_in_market_total
        if days_in_market_total > 0:
            metrics['annualized_return'] = ((metrics['final_capital'] / initial_capital) ** (365 / days_in_market_total) - 1) * 100
        else:
            metrics['annualized_return'] = 0
    except Exception as e:
        print(f"Warning: Could not calculate annualized return: {e}")
        metrics['annualized_return'] = 0
    
    # Trade consistency analysis
    win_streak = loss_streak = 0
    max_win_streak = max_loss_streak = 0
    
    for win in trades['Win']:
        if win:
            win_streak += 1
            loss_streak = 0
            max_win_streak = max(max_win_streak, win_streak)
        else:
            loss_streak += 1
            win_streak = 0
            max_loss_streak = max(max_loss_streak, loss_streak)
    
    metrics['max_win_streak'] = max_win_streak
    metrics['max_loss_streak'] = max_loss_streak
    
    # Exit reasons analysis
    metrics['exit_reasons'] = trades['Reason'].value_counts().to_dict()
    
    # Generate QuantStats metrics if available
    qs_metrics = {}
    qs_tearsheet = {}
    
    if QUANTSTATS_AVAILABLE:
        try:
            # Convert equity curve to returns for quantstats
            returns_series = equity_curve['portfolio_value'].pct_change().fillna(0)
            
            # Generate full report to HTML file
            report_filename = f"strategy_report_{symbol}_{start_date}_{end_date}.html"
            benchmark_returns = returns_df.get('benchmark', None)
            
            # Generate metrics
            if benchmark_returns is not None:
                qs_metrics_df = qs.reports.metrics(returns=returns_series, benchmark=benchmark_returns, display=False)
            else:
                qs_metrics_df = qs.reports.metrics(returns=returns_series, display=False)
            
            qs_tearsheet = qs_metrics_df.to_dict()
            
            # Generate HTML report
            qs.reports.html(returns_series, benchmark=benchmark_returns, output=report_filename, 
                          title=f"Strategy Report for {symbol} ({start_date} to {end_date})")
            print(f"\nQuantStats full report generated: {report_filename}")
            
            # Calculate key QuantStats metrics
            qs_metrics = {
                'cagr': qs.stats.cagr(returns_series) * 100,
                'volatility': qs.stats.volatility(returns_series) * 100,
                'sharpe': qs.stats.sharpe(returns_series),
                'sortino': qs.stats.sortino(returns_series),
                'calmar': qs.stats.calmar(returns_series),
                'max_drawdown': qs.stats.max_drawdown(returns_series) * 100,
                'win_rate': qs.stats.win_rate(returns_series) * 100,
                'avg_win': qs.stats.avg_win(returns_series) * 100,
                'avg_loss': qs.stats.avg_loss(returns_series) * 100,
                'best_day': qs.stats.best(returns_series) * 100,
                'worst_day': qs.stats.worst(returns_series) * 100,
                'recovery_time': qs.stats.recovery_time(returns_series),
                'risk_of_ruin': qs.stats.risk_of_ruin(returns_series),
                'value_at_risk': qs.stats.value_at_risk(returns_series) * 100,
                'expected_shortfall': qs.stats.expected_shortfall(returns_series) * 100,
                'tail_ratio': qs.stats.tail_ratio(returns_series),
                'common_sense_ratio': qs.stats.common_sense_ratio(returns_series)
            }
            metrics.update(qs_metrics)
            metrics['qs_tearsheet'] = qs_tearsheet
        except Exception as e:
            print(f"Warning: Could not generate quantstats metrics: {e}")
    
    # Print formatted report
    print_strategy_report(metrics, trades, lower_tf, higher_tf, lower_ema_short, lower_ema_long, 
                         higher_ema_short, higher_ema_long, risk_percent, risk_reward_ratio, 
                         initial_capital, lot_size, qs_metrics, qs_tearsheet)
    
    return metrics

def print_strategy_report(metrics, trades, lower_tf, higher_tf, lower_ema_short, lower_ema_long, 
                         higher_ema_short, higher_ema_long, risk_percent, risk_reward_ratio, 
                         initial_capital, lot_size, qs_metrics, qs_tearsheet):
    """Print a formatted performance report based on calculated metrics"""
    
    print("\n===== MULTI-TIMEFRAME STRATEGY PERFORMANCE REPORT =====\n")
    
    # Print basic information
    if metrics.get('symbol'):
        print(f"Symbol: {metrics['symbol']}")
    if metrics.get('start_date') and metrics.get('end_date'):
        print(f"Period: {metrics['start_date']} to {metrics['end_date']}")
    
    # Print strategy parameters
    print(f"\nStrategy Parameters:")
    print(f"Lower Timeframe: {lower_tf}, EMAs: {lower_ema_short}/{lower_ema_long}")
    print(f"Higher Timeframe: {higher_tf}, EMAs: {higher_ema_short}/{higher_ema_long}")
    print(f"Risk: {risk_percent}%, Risk-Reward Ratio: {risk_reward_ratio}")
    print(f"Initial Capital: ${initial_capital}, Lot Size: {lot_size}")
    
    # Print core performance metrics
    print("\n----- Performance Metrics -----")
    print(f"Total Trades: {metrics['total_trades']}")
    print(f"Win Rate: {metrics['win_rate']:.2f}%")
    print(f"Total Profit: ${metrics['total_profit']:.2f}")
    print(f"Final Capital: ${metrics['final_capital']:.2f}")
    print(f"Total Return: {metrics['total_return_pct']:.2f}%")
    
    if metrics.get('days_in_market_total', 0) > 0:
        print(f"Annualized Return: {metrics['annualized_return']:.2f}%")
        print(f"Total Days in Market: {metrics['days_in_market']} out of {metrics['days_in_market_total']} ({metrics['days_in_market_pct']:.2f}%)")
    
    print(f"Time in Market: {metrics['time_in_market_pct']:.2f}%")
    print(f"Avg Profit per Trade: ${metrics['avg_profit']:.2f}")
    print(f"Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
    
    # Print trade analysis
    print("\n----- Trade Analysis -----")
    print(f"Number of Long Signals Traded: {metrics['num_long_trades']}")
    print(f"Number of Short Signals Traded: {metrics['num_short_trades']}")
    print(f"Total Number of Signals Generated: {metrics['total_signals']}")
    print(f"Number of Profitable Trades: {metrics['profitable_trades']}")
    print(f"Number of Loss Making Trades: {metrics['losing_trades']}")
    print(f"Profit from Profitable Trades: ${metrics['profit_from_winners']:.2f}")
    print(f"Loss from Loss Making Trades: ${metrics['loss_from_losers']:.2f}")
    print(f"Returns from Winning Trades: {metrics['returns_from_winners']:.2f}%")
    print(f"Returns from Losing Trades: {metrics['returns_from_losers']:.2f}%")
    print(f"Avg Win: ${metrics['avg_win']:.2f}")
    print(f"Avg Loss: ${metrics['avg_loss']:.2f}")
    
    if metrics['avg_loss'] != 0:
        print(f"Avg Win/Loss Ratio: {metrics['win_loss_ratio']:.2f}")
    
    print(f"Longest Win Streak: {metrics['max_win_streak']}")
    print(f"Longest Loss Streak: {metrics['max_loss_streak']}")
    
    # Print exit reasons
    if metrics.get('exit_reasons'):
        print("\n----- Exit Reasons -----")
        for reason, count in metrics['exit_reasons'].items():
            print(f"{reason}: {count} trades ({count/metrics['total_trades']*100:.1f}%)")
    
    # Print QuantStats metrics if available
    if qs_metrics:
        print("\n----- QuantStats Metrics -----")
        metrics_to_display = [
            ('CAGR', 'cagr', '%'),
            ('Volatility', 'volatility', '%'),
            ('Sharpe Ratio', 'sharpe', ''),
            ('Sortino Ratio', 'sortino', ''),
            ('Calmar Ratio', 'calmar', ''),
            ('QuantStats Max Drawdown', 'max_drawdown', '%'),
            ('QuantStats Win Rate', 'win_rate', '%'),
            ('QuantStats Avg Win', 'avg_win', '%'),
            ('QuantStats Avg Loss', 'avg_loss', '%'),
            ('Best Day', 'best_day', '%'),
            ('Worst Day', 'worst_day', '%'),
            ('Recovery Time', 'recovery_time', ''),
            ('Risk of Ruin', 'risk_of_ruin', ''),
            ('Value at Risk (95%)', 'value_at_risk', '%'),
            ('Expected Shortfall (95%)', 'expected_shortfall', '%'),
            ('Tail Ratio', 'tail_ratio', ''),
            ('Common Sense Ratio', 'common_sense_ratio', '')
        ]
        
        for label, key, suffix in metrics_to_display:
            value = qs_metrics.get(key, 0)
            if key == 'recovery_time':
                print(f"{label}: {value}")
            elif key == 'risk_of_ruin':
                print(f"{label}: {value:.6f}")
            else:
                print(f"{label}: {value:.2f}{suffix}")
    
    # Print QuantStats tearsheet if available and not empty
    if qs_tearsheet and len(qs_tearsheet) > 0:
        print("\n===== QUANTSTATS TEARSHEET =====")
        
        # Define which metrics to display in the tearsheet - common QuantStats metrics
        all_possible_metrics = [
            "Start Period", "End Period", "Risk-Free Rate", "Time in Market",
            "Cumulative Return", "CAGR﹪", "Sharpe", "Sortino", 
            "Max Drawdown", "Volatility (ann.)", "Calmar",
            "Expected Yearly %", "Kelly Criterion", "Risk of Ruin",
            "Daily Value-at-Risk", "Expected Shortfall (cVaR)",
            "Max Consecutive Wins", "Max Consecutive Losses", "Profit Factor",
            "Common Sense Ratio", "Best Day", "Worst Day", "Win Days %",
            # Additional metrics that might be present
            "Total Return", "Benchmark Return", "Alpha", "Beta"
        ]
        
        # Get available columns
        columns = list(qs_tearsheet.keys())
        
        if columns:
            # Check which metrics are actually present in the tearsheet
            available_metrics = []
            for col in columns:
                available_metrics.extend(list(qs_tearsheet[col].keys()))
            available_metrics = list(set(available_metrics))  # Remove duplicates
            
            # If no intersection between our list and available metrics
            if not any(metric in available_metrics for metric in all_possible_metrics):
                print("No standard metrics found in tearsheet. Displaying all available metrics:")
                display_metrics = available_metrics
            else:
                display_metrics = [m for m in all_possible_metrics if m in available_metrics]
            
            # Safety check to avoid the empty sequence error
            if not display_metrics:
                print("No metrics available in tearsheet.")
                return
            
            # Find maximum width for metrics column
            metric_width = max(len(metric) for metric in display_metrics)
            
            # Print header
            print(f"{'':>{metric_width}}  {columns[0]:<15} {columns[1] if len(columns) > 1 else ''}")
            print(f"{'-'*metric_width}  {'-'*15} {'-'*15 if len(columns) > 1 else ''}")
            
            # Print each selected metric
            for metric in display_metrics:
                values = []
                for col in columns:
                    val = qs_tearsheet[col].get(metric, "-")
                    if isinstance(val, (float, np.float64)):
                        if "%" in metric:
                            values.append(f"{val:.2f}%")
                        else:
                            values.append(f"{val:.2f}")
                    else:
                        values.append(str(val))
                
                print(f"{metric:>{metric_width}}  {values[0]:<15} {values[1] if len(values) > 1 else ''}")
        else:
            print("No columns available in tearsheet.")