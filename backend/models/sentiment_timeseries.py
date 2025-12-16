"""
Sentiment Time Series Preprocessing Module
Aligns sentiment analysis with technical analysis time periods
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import json
import os
from pathlib import Path
from config import Config


class SentimentTimeSeriesProcessor:
    """Process news sentiment into time-series data aligned with price data"""
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.join(Config.DATA_DIR, 'sentiment_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.sentiment_cache = {}
        
    def load_news_data(self, symbol: str = 'BTC') -> pd.DataFrame:
        """Load news data from dataset"""
        try:
            # Try multiple possible CSV files
            csv_candidates = [
                os.path.join(Config.DATA_DIR, 'cryptoNewsDataset', 
                           'csvOutput', 'news_currencies_source_joinedResult.csv'),
                os.path.join(Config.DATA_DIR, 'cryptoNewsDataset', 
                           'csvOutput', 'cryptonews.csv'),
                os.path.join(Config.DATA_DIR, 'cryptoNewsDataset', 
                           'csvOutput', 'cryptopanic_news.csv'),
            ]
            
            csv_path = None
            for candidate in csv_candidates:
                if os.path.exists(candidate):
                    csv_path = candidate
                    break
            
            if not csv_path:
                print(f"News dataset not found. Tried: {csv_candidates[0]}")
                return pd.DataFrame()
            
            print(f"Loading news from: {os.path.basename(csv_path)}")
            df = pd.read_csv(csv_path)
            df['newsDatetime'] = pd.to_datetime(df['newsDatetime'])
            
            # Filter by symbol if specified
            if symbol and symbol != 'ALL' and 'currencies' in df.columns:
                symbol_filter = df['currencies'].str.contains(symbol, case=False, na=False)
                df = df[symbol_filter]
            
            return df.sort_values('newsDatetime')
            
        except Exception as e:
            print(f"Error loading news data: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def preprocess_sentiment_timeseries(
        self, 
        news_df: pd.DataFrame, 
        sentiment_analyzer,
        timeframe: str = '1d',
        symbol: str = 'BTC',
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Preprocess news sentiment into time-series format
        
        Args:
            news_df: DataFrame with news data
            sentiment_analyzer: FinBERTSentimentAnalyzer instance
            timeframe: Time granularity ('1d', '3d', '5d', '10d', etc.)
            symbol: Cryptocurrency symbol
            use_cache: Whether to use cached results
            
        Returns:
            DataFrame with timestamp and sentiment_score columns
        """
        cache_file = os.path.join(
            self.cache_dir, 
            f'sentiment_{symbol}_{timeframe}.csv'
        )
        
        # Check cache
        if use_cache and os.path.exists(cache_file):
            try:
                print(f"Loading cached sentiment data: {cache_file}")
                df = pd.read_csv(cache_file)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df
            except Exception as e:
                print(f"Cache load error: {e}, regenerating...")
        
        if news_df.empty:
            print("No news data available")
            return pd.DataFrame(columns=['timestamp', 'sentiment_score'])
        
        print(f"Preprocessing sentiment time series for {symbol} at {timeframe}...")
        
        # Group news by time period
        news_df = news_df.copy()
        news_df['period'] = news_df['newsDatetime'].dt.floor(timeframe)
        
        sentiment_data = []
        total_periods = len(news_df['period'].unique())
        
        for idx, (period, group) in enumerate(news_df.groupby('period')):
            if idx % 100 == 0:
                print(f"Processing period {idx + 1}/{total_periods}: {period}")
            
            # Analyze sentiment for this period
            texts = []
            for _, row in group.iterrows():
                text = f"{row.get('title', '')} {row.get('description', '')}"
                if text.strip():
                    texts.append(text)
            
            if not texts:
                continue
            
            # Batch analysis (limit to avoid memory issues)
            batch_size = 50
            sentiments = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_results = sentiment_analyzer.analyze_batch(batch)
                sentiments.extend(batch_results)
            
            # Aggregate sentiment for this period
            if sentiments:
                agg_result = sentiment_analyzer.aggregate_sentiment(sentiments)
                sentiment_data.append({
                    'timestamp': period,
                    'sentiment_score': agg_result['sentiment_score'],
                    'positive_ratio': agg_result['distribution']['positive'] / len(sentiments),
                    'negative_ratio': agg_result['distribution']['negative'] / len(sentiments),
                    'neutral_ratio': agg_result['distribution']['neutral'] / len(sentiments),
                    'news_count': len(texts)
                })
        
        # Create DataFrame
        sentiment_ts = pd.DataFrame(sentiment_data)
        
        if not sentiment_ts.empty:
            sentiment_ts = sentiment_ts.sort_values('timestamp')
            
            # Save cache
            try:
                sentiment_ts.to_csv(cache_file, index=False)
                print(f"Sentiment time series cached: {cache_file}")
            except Exception as e:
                print(f"Error caching sentiment data: {e}")
        
        return sentiment_ts
    
    def align_sentiment_with_price(
        self,
        price_df: pd.DataFrame,
        sentiment_ts: pd.DataFrame,
        fill_method: str = 'forward'
    ) -> pd.DataFrame:
        """
        Align sentiment time series with price data
        
        Args:
            price_df: DataFrame with price data (must have timestamp index)
            sentiment_ts: DataFrame with sentiment time series
            fill_method: Method to fill missing values ('forward', 'backward', 'interpolate')
            
        Returns:
            DataFrame with aligned sentiment scores
        """
        if sentiment_ts.empty:
            # Return neutral sentiment for all periods
            result = price_df.copy()
            result['sentiment_score'] = 0.0
            return result
        
        # Ensure timestamp is datetime
        if 'timestamp' not in price_df.columns:
            price_df = price_df.reset_index()
        
        price_df['timestamp'] = pd.to_datetime(price_df['timestamp'])
        sentiment_ts['timestamp'] = pd.to_datetime(sentiment_ts['timestamp'])
        
        # Merge on timestamp
        merged = pd.merge_asof(
            price_df.sort_values('timestamp'),
            sentiment_ts[['timestamp', 'sentiment_score']].sort_values('timestamp'),
            on='timestamp',
            direction='backward'  # Use most recent sentiment
        )
        
        # Fill missing values
        if fill_method == 'forward':
            merged['sentiment_score'] = merged['sentiment_score'].fillna(method='ffill')
        elif fill_method == 'backward':
            merged['sentiment_score'] = merged['sentiment_score'].fillna(method='bfill')
        elif fill_method == 'interpolate':
            merged['sentiment_score'] = merged['sentiment_score'].interpolate()
        
        # Fill any remaining NaN with neutral (0)
        merged['sentiment_score'] = merged['sentiment_score'].fillna(0.0)
        
        return merged
    
    def get_rolling_sentiment(
        self,
        news_df: pd.DataFrame,
        sentiment_analyzer,
        target_date: datetime,
        window_days: int = 7
    ) -> Dict[str, Any]:
        """
        Get sentiment for a specific date using rolling window
        
        Args:
            news_df: DataFrame with news data
            sentiment_analyzer: FinBERTSentimentAnalyzer instance
            target_date: Target date for sentiment
            window_days: Number of days to look back
            
        Returns:
            Sentiment analysis result
        """
        window_start = target_date - timedelta(days=window_days)
        
        # Filter news in the window
        mask = (news_df['newsDatetime'] >= window_start) & \
               (news_df['newsDatetime'] <= target_date)
        window_news = news_df[mask]
        
        if window_news.empty:
            return {
                'sentiment_score': 0.0,
                'news_count': 0,
                'distribution': {'positive': 0, 'neutral': 0, 'negative': 0}
            }
        
        # Analyze sentiment
        texts = []
        for _, row in window_news.iterrows():
            text = f"{row.get('title', '')} {row.get('description', '')}"
            if text.strip():
                texts.append(text)
        
        sentiments = sentiment_analyzer.analyze_batch(texts)
        result = sentiment_analyzer.aggregate_sentiment(sentiments)
        result['news_count'] = len(texts)
        
        return result
    
    def create_sentiment_features(
        self,
        sentiment_ts: pd.DataFrame,
        lookback_periods: List[int] = [7, 14, 30]
    ) -> pd.DataFrame:
        """
        Create additional sentiment features for ML models
        
        Args:
            sentiment_ts: Sentiment time series DataFrame
            lookback_periods: Periods for rolling statistics
            
        Returns:
            DataFrame with additional features
        """
        df = sentiment_ts.copy()
        
        for period in lookback_periods:
            # Rolling mean
            df[f'sentiment_sma_{period}'] = df['sentiment_score'].rolling(
                window=period, min_periods=1
            ).mean()
            
            # Rolling std (volatility)
            df[f'sentiment_std_{period}'] = df['sentiment_score'].rolling(
                window=period, min_periods=1
            ).std()
            
            # Sentiment momentum
            df[f'sentiment_momentum_{period}'] = df['sentiment_score'].diff(period)
        
        # Fill NaN
        df = df.fillna(0)
        
        return df
    
    def get_sentiment_statistics(
        self,
        sentiment_ts: pd.DataFrame
    ) -> Dict[str, Any]:
        """Get statistics about sentiment time series"""
        if sentiment_ts.empty:
            return {
                'count': 0,
                'mean': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'date_range': None
            }
        
        return {
            'count': len(sentiment_ts),
            'mean': float(sentiment_ts['sentiment_score'].mean()),
            'std': float(sentiment_ts['sentiment_score'].std()),
            'min': float(sentiment_ts['sentiment_score'].min()),
            'max': float(sentiment_ts['sentiment_score'].max()),
            'date_range': {
                'start': sentiment_ts['timestamp'].min().isoformat(),
                'end': sentiment_ts['timestamp'].max().isoformat()
            }
        }
