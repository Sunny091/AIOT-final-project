import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import os


class SentimentStrategy(bt.Strategy):
    """Strategy combining sentiment analysis with technical indicators"""
    
    params = (
        ('sentiment_threshold', 0.2),
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('sma_fast', 20),
        ('sma_slow', 50),
        ('position_size', 0.95),
    )
    
    def __init__(self):
        self.order = None
        
        # Technical indicators
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.sma_fast = bt.indicators.SMA(self.data.close, period=self.params.sma_fast)
        self.sma_slow = bt.indicators.SMA(self.data.close, period=self.params.sma_slow)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
        self.order = None
    
    def log(self, txt):
        dt = self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
    
    def next(self):
        if self.order:
            return
        
        # Get sentiment from data feed
        sentiment_score = self.data.sentiment[0] if len(self.data.sentiment) > 0 else 0.0
        
        # Check if we have a position
        if not self.position:
            # Buy signals
            bullish_sentiment = sentiment_score > self.params.sentiment_threshold
            rsi_oversold = self.rsi[0] < self.params.rsi_oversold
            golden_cross = self.crossover[0] > 0
            
            if (bullish_sentiment and rsi_oversold) or golden_cross:
                value = self.broker.getcash() * self.params.position_size
                self.order = self.buy(size=value / self.data.close[0])
                
        else:
            # Sell signals
            bearish_sentiment = sentiment_score < -self.params.sentiment_threshold
            rsi_overbought = self.rsi[0] > self.params.rsi_overbought
            death_cross = self.crossover[0] < 0
            
            if (bearish_sentiment and rsi_overbought) or death_cross:
                self.order = self.sell(size=self.position.size)


class MACDStrategy(bt.Strategy):
    """MACD-based trading strategy"""
    
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
        ('position_size', 0.95),
    )
    
    def __init__(self):
        self.order = None
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.fast_period,
            period_me2=self.params.slow_period,
            period_signal=self.params.signal_period
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
        self.order = None
    
    def log(self, txt):
        dt = self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
    
    def next(self):
        if self.order:
            return
        
        if not self.position:
            if self.crossover[0] > 0:  # MACD crosses above signal
                value = self.broker.getcash() * self.params.position_size
                self.order = self.buy(size=value / self.data.close[0])
        else:
            if self.crossover[0] < 0:  # MACD crosses below signal
                self.order = self.sell(size=self.position.size)


class TechnicalStrategy(bt.Strategy):
    """Strategy based on technical analysis with DL predictions"""
    
    params = (
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('bb_period', 20),
        ('bb_devs', 2),
        ('position_size', 0.95),
    )
    
    def __init__(self):
        self.order = None
        
        # Technical indicators
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal
        )
        self.bbands = bt.indicators.BollingerBands(
            self.data.close, 
            period=self.params.bb_period,
            devfactor=self.params.bb_devs
        )
        self.macd_cross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
        self.order = None
    
    def log(self, txt):
        dt = self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
    
    def next(self):
        if self.order:
            return
        
        if not self.position:
            # Buy signals - more aggressive entry
            macd_bullish = self.macd_cross[0] > 0
            rsi_oversold = self.rsi[0] < self.params.rsi_oversold
            rsi_neutral_buy = self.rsi[0] < 50  # RSI below 50
            bb_lower = self.data.close[0] < self.bbands.lines.bot[0]
            bb_mid_lower = self.data.close[0] < self.bbands.lines.mid[0]  # Below middle band
            
            # Buy if strong MACD signal OR RSI oversold OR multiple weaker signals
            buy_signals = sum([rsi_oversold, bb_lower])
            weak_signals = sum([macd_bullish, rsi_neutral_buy, bb_mid_lower])
            
            if macd_bullish and weak_signals >= 1:  # MACD cross with 1 other signal
                # Use value-based position sizing for fractional shares
                value = self.broker.getcash() * self.params.position_size
                self.order = self.buy(size=value / self.data.close[0])
            elif buy_signals >= 1:  # Any strong signal
                # Use value-based position sizing for fractional shares
                value = self.broker.getcash() * self.params.position_size
                self.order = self.buy(size=value / self.data.close[0])
        else:
            # Sell signals - more aggressive exit
            macd_bearish = self.macd_cross[0] < 0
            rsi_overbought = self.rsi[0] > self.params.rsi_overbought
            rsi_neutral_sell = self.rsi[0] > 50  # RSI above 50
            bb_upper = self.data.close[0] > self.bbands.lines.top[0]
            bb_mid_upper = self.data.close[0] > self.bbands.lines.mid[0]  # Above middle band
            
            # Sell if strong signal OR trend reversal
            sell_signals = sum([rsi_overbought, bb_upper])
            weak_signals = sum([macd_bearish, bb_mid_upper])
            
            if macd_bearish and rsi_neutral_sell:  # MACD reversal with RSI confirmation
                self.order = self.sell(size=self.position.size)
            elif sell_signals >= 1:  # Any strong sell signal
                self.order = self.sell(size=self.position.size)


class CombinedStrategy(bt.Strategy):
    """Combined strategy using sentiment + technical analysis with weighted scoring"""
    
    params = (
        ('sentiment_threshold', 0.1),  # Lowered threshold
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('sma_fast', 20),
        ('sma_slow', 50),
        ('bb_period', 20),
        ('bb_devs', 2),
        ('position_size', 0.95),
        ('sentiment_weight', 0.3),  # Reduced sentiment weight
        ('technical_weight', 0.7),  # Increased technical weight
        ('buy_threshold', 0.45),  # Add configurable thresholds
        ('sell_threshold', 0.45),
    )
    
    def __init__(self):
        self.order = None
        
        # Technical indicators
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal
        )
        self.sma_fast = bt.indicators.SMA(self.data.close, period=self.params.sma_fast)
        self.sma_slow = bt.indicators.SMA(self.data.close, period=self.params.sma_slow)
        self.bbands = bt.indicators.BollingerBands(
            self.data.close, 
            period=self.params.bb_period,
            devfactor=self.params.bb_devs
        )
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)
        self.macd_cross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
        self.order = None
    
    def log(self, txt):
        dt = self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
    
    def _calculate_buy_score(self, sentiment_score):
        """Calculate weighted buy signal score"""
        # Sentiment component (normalized to 0-1)
        sentiment_signal = max(0, min(1, (sentiment_score + 1) / 2))  # Map [-1,1] to [0,1]
        
        # Technical components
        tech_signals = []
        
        # RSI signals (0-1 scale)
        if self.rsi[0] < self.params.rsi_oversold:
            tech_signals.append(1.0)  # Strong buy
        elif self.rsi[0] < 50:
            tech_signals.append(0.5)  # Moderate buy
        else:
            tech_signals.append(0.0)
        
        # MACD signals
        if self.macd_cross[0] > 0:
            tech_signals.append(1.0)  # Strong bullish cross
        elif self.macd.macd[0] > self.macd.signal[0]:
            tech_signals.append(0.5)  # Moderate bullish
        else:
            tech_signals.append(0.0)
        
        # Moving average signals
        if self.crossover[0] > 0:
            tech_signals.append(1.0)  # Golden cross
        elif self.sma_fast[0] > self.sma_slow[0]:
            tech_signals.append(0.5)  # Uptrend
        else:
            tech_signals.append(0.0)
        
        # Bollinger Bands signals
        if self.data.close[0] < self.bbands.lines.bot[0]:
            tech_signals.append(0.8)  # Oversold
        elif self.data.close[0] < self.bbands.lines.mid[0]:
            tech_signals.append(0.4)  # Below mid
        else:
            tech_signals.append(0.0)
        
        # Average technical signals
        tech_signal = sum(tech_signals) / len(tech_signals)
        
        # Weighted combined score
        combined_score = (sentiment_signal * self.params.sentiment_weight + 
                         tech_signal * self.params.technical_weight)
        
        return combined_score
    
    def _calculate_sell_score(self, sentiment_score):
        """Calculate weighted sell signal score"""
        # Sentiment component (normalized to 0-1)
        sentiment_signal = max(0, min(1, (-sentiment_score + 1) / 2))  # Inverted for sell
        
        # Technical components
        tech_signals = []
        
        # RSI signals (0-1 scale)
        if self.rsi[0] > self.params.rsi_overbought:
            tech_signals.append(1.0)  # Strong sell
        elif self.rsi[0] > 50:
            tech_signals.append(0.5)  # Moderate sell
        else:
            tech_signals.append(0.0)
        
        # MACD signals
        if self.macd_cross[0] < 0:
            tech_signals.append(1.0)  # Strong bearish cross
        elif self.macd.macd[0] < self.macd.signal[0]:
            tech_signals.append(0.5)  # Moderate bearish
        else:
            tech_signals.append(0.0)
        
        # Moving average signals
        if self.crossover[0] < 0:
            tech_signals.append(1.0)  # Death cross
        elif self.sma_fast[0] < self.sma_slow[0]:
            tech_signals.append(0.5)  # Downtrend
        else:
            tech_signals.append(0.0)
        
        # Bollinger Bands signals
        if self.data.close[0] > self.bbands.lines.top[0]:
            tech_signals.append(0.8)  # Overbought
        elif self.data.close[0] > self.bbands.lines.mid[0]:
            tech_signals.append(0.4)  # Above mid
        else:
            tech_signals.append(0.0)
        
        # Average technical signals
        tech_signal = sum(tech_signals) / len(tech_signals)
        
        # Weighted combined score
        combined_score = (sentiment_signal * self.params.sentiment_weight + 
                         tech_signal * self.params.technical_weight)
        
        return combined_score
    
    def next(self):
        if self.order:
            return
        
        # Get sentiment from data feed
        sentiment_score = self.data.sentiment[0] if len(self.data.sentiment) > 0 else 0.0
        
        if not self.position:
            # Calculate buy score
            buy_score = self._calculate_buy_score(sentiment_score)
            
            # Buy if combined score exceeds threshold
            if buy_score > self.params.buy_threshold:
                value = self.broker.getcash() * self.params.position_size
                self.order = self.buy(size=value / self.data.close[0])
                self.log(f'BUY SIGNAL - Score: {buy_score:.2f}, Sentiment: {sentiment_score:.2f}, RSI: {self.rsi[0]:.1f}')
        else:
            # Calculate sell score
            sell_score = self._calculate_sell_score(sentiment_score)
            
            # Sell if combined score exceeds threshold
            if sell_score > self.params.sell_threshold:
                self.order = self.sell(size=self.position.size)
                self.log(f'SELL SIGNAL - Score: {sell_score:.2f}, Sentiment: {sentiment_score:.2f}, RSI: {self.rsi[0]:.1f}')


class PortfolioValueRecorder(bt.Observer):
    """Custom observer to record portfolio value over time"""
    lines = ('value',)
    
    def next(self):
        self.lines.value[0] = self._owner.broker.getvalue()


class BacktestEngine:
    """Backtesting engine for quantitative trading strategies"""
    
    def __init__(self, initial_cash: float = 10000, commission: float = 0.001):
        self.initial_cash = initial_cash
        self.commission = commission
        self.sentiment_processor = None
        self.sentiment_analyzer = None
        
    def run_backtest(self, df: pd.DataFrame, strategy_name: str = 'sentiment',
                     strategy_params: Optional[Dict] = None, 
                     symbol: str = 'BTC', use_aligned_sentiment: bool = True) -> Dict[str, Any]:
        """
        Run backtest with specified strategy
        
        Args:
            df: DataFrame with OHLCV data
            strategy_name: Name of strategy to use
            strategy_params: Parameters for the strategy
            symbol: Symbol for sentiment analysis
            use_aligned_sentiment: Whether to use time-aligned sentiment
            
        Returns:
            Backtest results with performance metrics
        """
        try:
            # Initialize Cerebro
            cerebro = bt.Cerebro()
            
            # Prepare data
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Add time-aligned sentiment if needed
            sentiment_data = None
            if strategy_name in ['sentiment', 'combined'] and use_aligned_sentiment:
                sentiment_data = self._add_aligned_sentiment(df, symbol, strategy_name)
            
            # Merge sentiment data if available
            if sentiment_data is not None and not sentiment_data.empty:
                # Ensure sentiment_data timestamp is datetime type
                sentiment_data = sentiment_data.copy()
                sentiment_data['timestamp'] = pd.to_datetime(sentiment_data['timestamp'])

                # Use merge_asof for time-series alignment (more robust)
                df = df.sort_values('timestamp')
                sentiment_data = sentiment_data.sort_values('timestamp')
                df = pd.merge_asof(
                    df,
                    sentiment_data[['timestamp', 'sentiment_score']],
                    on='timestamp',
                    direction='backward'
                )
                df['sentiment_score'] = df['sentiment_score'].fillna(0.0)
            else:
                df['sentiment_score'] = 0.0
            
            df.set_index('timestamp', inplace=True)
            
            # Create custom data feed with sentiment
            class PandasDataWithSentiment(bt.feeds.PandasData):
                lines = ('sentiment',)
                params = (('sentiment', -1),)
            
            # Create data feed
            data = PandasDataWithSentiment(
                dataname=df,
                open='open',
                high='high',
                low='low',
                close='close',
                volume='volume',
                sentiment='sentiment_score',
                openinterest=-1
            )
            cerebro.adddata(data)
            
            # Add strategy
            if strategy_name == 'sentiment':
                if strategy_params:
                    cerebro.addstrategy(SentimentStrategy, **strategy_params)
                else:
                    cerebro.addstrategy(SentimentStrategy)
            elif strategy_name == 'technical':
                if strategy_params:
                    cerebro.addstrategy(TechnicalStrategy, **strategy_params)
                else:
                    cerebro.addstrategy(TechnicalStrategy)
            elif strategy_name == 'combined':
                if strategy_params:
                    cerebro.addstrategy(CombinedStrategy, **strategy_params)
                else:
                    cerebro.addstrategy(CombinedStrategy)
            else:
                return {"success": False, "error": f"Unknown strategy: {strategy_name}"}
            
            # Set initial cash and commission
            cerebro.broker.setcash(self.initial_cash)
            cerebro.broker.setcommission(commission=self.commission)
            
            # Enable fractional trading for crypto
            cerebro.broker.set_fundmode(fundmode=True, fundstartval=self.initial_cash)
            
            # Add analyzers
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', 
                              riskfreerate=0.0, annualize=True, timeframe=bt.TimeFrame.Days)
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
            cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
            cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
            
            # Add custom observer to track portfolio value
            cerebro.addobserver(PortfolioValueRecorder)
            
            # Run backtest
            print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
            results = cerebro.run()
            final_value = cerebro.broker.getvalue()
            print(f'Final Portfolio Value: {final_value:.2f}')
            
            # Extract results
            strat = results[0]
            
            # Get analyzer results
            sharpe_analysis = strat.analyzers.sharpe.get_analysis()
            drawdown = strat.analyzers.drawdown.get_analysis()
            returns_analysis = strat.analyzers.returns.get_analysis()
            trades = strat.analyzers.trades.get_analysis()
            
            # Calculate metrics
            total_return = ((final_value - self.initial_cash) / self.initial_cash) * 100
            
            # Safely extract trade statistics
            total_trades = 0
            winning_trades = 0
            losing_trades = 0
            avg_win = 0
            avg_loss = 0
            
            try:
                if hasattr(trades, 'total') and hasattr(trades.total, 'total'):
                    total_trades = trades.total.total
            except:
                pass
            
            try:
                if hasattr(trades, 'won') and hasattr(trades.won, 'total'):
                    winning_trades = trades.won.total
                if hasattr(trades, 'won') and hasattr(trades.won, 'pnl'):
                    if hasattr(trades.won.pnl, 'average'):
                        avg_win = trades.won.pnl.average
            except:
                pass
            
            try:
                if hasattr(trades, 'lost') and hasattr(trades.lost, 'total'):
                    losing_trades = trades.lost.total
                if hasattr(trades, 'lost') and hasattr(trades.lost, 'pnl'):
                    if hasattr(trades.lost.pnl, 'average'):
                        avg_loss = trades.lost.pnl.average
            except:
                pass
            
            # Calculate Sharpe ratio manually if backtrader returns None or 0
            sharpe_ratio = sharpe_analysis.get('sharperatio', None)
            if sharpe_ratio is None or (isinstance(sharpe_ratio, (int, float)) and sharpe_ratio == 0):
                # Calculate using returns
                try:
                    # Get portfolio values from observer
                    portfolio_values = []
                    for i in range(len(strat.observers[0].lines.value)):
                        portfolio_values.append(strat.observers[0].lines.value[i])
                    
                    if len(portfolio_values) > 1:
                        # Calculate daily returns
                        portfolio_values = np.array(portfolio_values)
                        returns = np.diff(portfolio_values) / portfolio_values[:-1]
                        
                        if len(returns) > 0 and returns.std() > 0:
                            # Annualized Sharpe ratio (assuming daily data)
                            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(365)
                        else:
                            sharpe_ratio = 0.0
                    else:
                        sharpe_ratio = 0.0
                except Exception as e:
                    print(f"Error calculating manual Sharpe ratio: {e}")
                    sharpe_ratio = 0.0
            
            # Ensure winning_trades + losing_trades <= total_trades
            # Backtrader sometimes counts open/closed trades differently
            closed_trades = winning_trades + losing_trades
            
            # If closed trades don't match total, use closed count
            if closed_trades != total_trades:
                # Total should be closed trades (won + lost)
                # Open positions are not counted as trades until closed
                total_trades = closed_trades
            
            result = {
                "success": True,
                "strategy": strategy_name,
                "initial_capital": self.initial_cash,
                "final_value": float(final_value),
                "total_return_pct": float(total_return),
                "sharpe_ratio": float(sharpe_ratio) if sharpe_ratio is not None else 0.0,
                "max_drawdown_pct": float(drawdown.max.drawdown or 0),
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": 0,
                "avg_trade_return": 0,
                "avg_win": float(avg_win) if avg_win else 0.0,
                "avg_loss": float(avg_loss) if avg_loss else 0.0
            }
            
            if result['total_trades'] > 0:
                result['win_rate'] = (result['winning_trades'] / result['total_trades']) * 100
                
            if result['winning_trades'] > 0 and result['losing_trades'] > 0:
                # Calculate profit factor
                total_wins = result['winning_trades'] * result['avg_win']
                total_losses = abs(result['losing_trades'] * result['avg_loss'])
                if total_losses > 0:
                    result['profit_factor'] = total_wins / total_losses
            
            return result
            
        except Exception as e:
            import traceback
            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
    
    def _add_aligned_sentiment(self, df: pd.DataFrame, symbol: str, strategy_name: str) -> pd.DataFrame:
        """Add time-aligned sentiment data to price DataFrame"""
        try:
            import signal
            
            # Define timeout handler
            def timeout_handler(signum, frame):
                raise TimeoutError("Sentiment loading timed out")
            
            # Set 30 second timeout for sentiment loading
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            try:
                # Lazy load sentiment processor and analyzer
                if self.sentiment_processor is None:
                    from backend.models.sentiment_timeseries import SentimentTimeSeriesProcessor
                    from backend.models.sentiment_analyzer import FinBERTSentimentAnalyzer
                    
                    print("Initializing sentiment analysis for backtest...")
                    self.sentiment_processor = SentimentTimeSeriesProcessor()
                    self.sentiment_analyzer = FinBERTSentimentAnalyzer()
                
                # Load news data
                print(f"Loading news data for {symbol}...")
                news_df = self.sentiment_processor.load_news_data(symbol)
                
                if news_df.empty:
                    print("No news data available, using neutral sentiment")
                    signal.alarm(0)  # Cancel alarm
                    return pd.DataFrame()
                
                # Determine timeframe from data
                df_temp = df.copy()
                df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'])
                time_diff = df_temp['timestamp'].diff().median()
                
                # Map timedelta to timeframe string
                if time_diff <= pd.Timedelta(days=1):
                    timeframe = '1d'
                else:
                    timeframe = '3d'
                
                print(f"Detected timeframe: {timeframe}")
                
                # Preprocess sentiment time series
                sentiment_ts = self.sentiment_processor.preprocess_sentiment_timeseries(
                    news_df=news_df,
                    sentiment_analyzer=self.sentiment_analyzer,
                    timeframe=timeframe,
                    symbol=symbol,
                    use_cache=True
                )
                
                signal.alarm(0)  # Cancel alarm
                
                if sentiment_ts.empty:
                    print("No sentiment data generated, using neutral sentiment")
                    return pd.DataFrame()
                
                # Return time series with sentiment scores
                avg_sentiment = sentiment_ts['sentiment_score'].mean()
                print(f"Average sentiment score: {avg_sentiment:.4f}")
                print(f"Sentiment data points: {len(sentiment_ts)}")
                
                return sentiment_ts
                
            except TimeoutError:
                signal.alarm(0)  # Cancel alarm
                print("Sentiment analysis timed out, using neutral sentiment")
                return pd.DataFrame()
            
        except Exception as e:
            print(f"Error in sentiment alignment: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()


class SentimentSetter(bt.Observer):
    """Observer to set sentiment score in strategies"""
    params = (('sentiment_score', 0.0),)
    
    def next(self):
        for strat in self._owner.runstrats:
            for s in strat:
                if hasattr(s, 'set_sentiment'):
                    s.set_sentiment(self.params.sentiment_score)


class BacktestTool:
    """MCP Tool for running backtests"""
    
    def __init__(self):
        self.engine = BacktestEngine()
        self.results_file = 'data/backtest_results.json'
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure results file exists"""
        import os
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.results_file):
            with open(self.results_file, 'w') as f:
                json.dump([], f)
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "run_backtest",
            "description": "Run quantitative trading strategy backtest",
            "parameters": {
                "symbol": "Trading pair symbol",
                "timeframe": "Timeframe for backtest",
                "strategy": "Strategy to test (sentiment, technical, combined)",
                "start_date": "Start date for backtest (YYYY-MM-DD, optional)",
                "end_date": "End date for backtest (YYYY-MM-DD, optional)",
                "initial_capital": "Initial capital (default: 10000)"
            }
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute backtest"""
        try:
            from backend.mcp_tools.crypto_tools import CryptoDataTool
            
            symbol = params.get('symbol', 'BTC/USDT')
            timeframe = params.get('timeframe', '1d')
            strategy = params.get('strategy', 'sentiment')
            initial_capital = params.get('initial_capital', 10000)
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            
            # Extract symbol name for sentiment (e.g., BTC from BTC/USDT)
            symbol_name = symbol.split('/')[0] if '/' in symbol else symbol
            
            # Fetch historical data
            data_tool = CryptoDataTool()
            ohlcv_result = data_tool.get_ohlcv(symbol, timeframe, limit=1000)
            
            if not ohlcv_result['success']:
                return ohlcv_result
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv_result['data'])
            
            # Filter by date range if specified
            if start_date or end_date:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                if start_date:
                    start_dt = pd.to_datetime(start_date)
                    df = df[df['timestamp'] >= start_dt]
                    
                if end_date:
                    end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)  # Include end date
                    df = df[df['timestamp'] < end_dt]
                
                if len(df) == 0:
                    return {"success": False, "error": "指定日期範圍內沒有數據"}

            # Check minimum data requirement for indicators
            # SMA slow period is 50, which requires at least 50+ data points
            MIN_DATA_POINTS = 60  # Buffer for indicator warm-up
            if len(df) < MIN_DATA_POINTS:
                return {
                    "success": False,
                    "error": f"數據量不足：需要至少 {MIN_DATA_POINTS} 個數據點來計算技術指標，但只有 {len(df)} 個。請擴大日期範圍或使用更短的時間週期。"
                }

            # Run backtest with time-aligned sentiment
            self.engine.initial_cash = initial_capital
            result = self.engine.run_backtest(
                df, 
                strategy, 
                symbol=symbol_name,
                use_aligned_sentiment=True
            )
            
            if result['success']:
                # Save result
                result['symbol'] = symbol
                result['timeframe'] = timeframe
                result['timestamp'] = datetime.now().isoformat()
                if start_date:
                    result['start_date'] = start_date
                if end_date:
                    result['end_date'] = end_date
                self._save_result(result)
            
            return result
            
        except Exception as e:
            import traceback
            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
    
    def _save_result(self, result: Dict[str, Any]):
        """Save backtest result"""
        try:
            with open(self.results_file, 'r') as f:
                results = json.load(f)
            
            results.append(result)
            
            # Keep only last 100 results
            results = results[-100:]
            
            with open(self.results_file, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            print(f"Error saving result: {e}")
    
    def get_results(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent backtest results"""
        try:
            with open(self.results_file, 'r') as f:
                results = json.load(f)
            
            return {
                "success": True,
                "results": results[-limit:]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
