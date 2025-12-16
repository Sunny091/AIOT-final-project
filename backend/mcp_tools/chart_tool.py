from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import base64
from io import BytesIO


class ChartTool:
    """MCP Tool for generating time-series charts"""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "create_chart",
            "description": "創建時間序列折線圖，可視化數據隨時間的變化（如價格走勢、情感變化等）",
            "parameters": {
                "data_source": "數據來源類型 (price/sentiment/custom)",
                "symbol": "加密貨幣符號 (例如: BTC/USDT)",
                "timeframe": "時間範圍 (1d/3d/1w)",
                "start_date": "開始日期 (可選, 格式: YYYY-MM-DD)",
                "end_date": "結束日期 (可選, 格式: YYYY-MM-DD)",
                "chart_type": "圖表類型 (line/candlestick, 默認: line)",
                "custom_data": "自定義數據 (可選, 格式: [{timestamp, value}])"
            }
        }
    
    def __init__(self):
        from backend.mcp_tools.crypto_tools import CryptoDataTool
        self.crypto_data = CryptoDataTool()
    
    def create_price_chart(self, symbol: str, timeframe: str = '1d', 
                          start_date: str = None, end_date: str = None,
                          chart_type: str = 'line') -> Dict[str, Any]:
        """創建價格走勢圖"""
        try:
            # Fetch OHLCV data
            limit = self._calculate_limit(timeframe, start_date, end_date)
            result = self.crypto_data.get_ohlcv(symbol, timeframe, limit)
            
            if not result.get('success'):
                return result
            
            df = pd.DataFrame(result['data'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter by date range if provided
            if start_date:
                df = df[df['timestamp'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['timestamp'] <= pd.to_datetime(end_date)]
            
            # Create chart
            if chart_type == 'candlestick':
                fig = go.Figure(data=[go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name=symbol
                )])
                title = f'{symbol} K線圖 ({timeframe})'
            else:
                fig = go.Figure(data=[go.Scatter(
                    x=df['timestamp'],
                    y=df['close'],
                    mode='lines',
                    name='價格',
                    line=dict(color='#00D9FF', width=2)
                )])
                title = f'{symbol} 價格走勢 ({timeframe})'
            
            fig.update_layout(
                title=title,
                xaxis_title='時間',
                yaxis_title='價格 (USDT)',
                template='plotly_dark',
                hovermode='x unified',
                height=500
            )
            
            # Convert to HTML
            chart_html = fig.to_html(include_plotlyjs='cdn', div_id='price-chart')
            
            # Also prepare data for frontend
            chart_data = {
                'timestamps': df['timestamp'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
                'values': df['close'].tolist(),
                'type': chart_type,
                'title': title
            }
            
            return {
                "success": True,
                "chart_html": chart_html,
                "chart_data": chart_data,
                "symbol": symbol,
                "timeframe": timeframe,
                "data_points": len(df)
            }
            
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def create_custom_chart(self, data: List[Dict[str, Any]], 
                           title: str = "自定義圖表",
                           x_label: str = "時間",
                           y_label: str = "數值") -> Dict[str, Any]:
        """創建自定義數據的折線圖"""
        try:
            df = pd.DataFrame(data)
            
            # Try to parse timestamp column
            timestamp_col = None
            value_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if any(t in col_lower for t in ['time', 'date', 'timestamp']):
                    timestamp_col = col
                elif any(v in col_lower for v in ['value', 'price', 'score', 'sentiment']):
                    value_col = col
            
            if not timestamp_col or not value_col:
                return {
                    "success": False,
                    "error": "數據必須包含時間戳和數值欄位"
                }
            
            df[timestamp_col] = pd.to_datetime(df[timestamp_col])
            
            fig = go.Figure(data=[go.Scatter(
                x=df[timestamp_col],
                y=df[value_col],
                mode='lines+markers',
                name=y_label,
                line=dict(color='#00D9FF', width=2),
                marker=dict(size=6)
            )])
            
            fig.update_layout(
                title=title,
                xaxis_title=x_label,
                yaxis_title=y_label,
                template='plotly_dark',
                hovermode='x unified',
                height=500
            )
            
            chart_html = fig.to_html(include_plotlyjs='cdn', div_id='custom-chart')
            
            chart_data = {
                'timestamps': df[timestamp_col].dt.strftime('%Y-%m-%d %H:%M').tolist(),
                'values': df[value_col].tolist(),
                'type': 'line',
                'title': title
            }
            
            return {
                "success": True,
                "chart_html": chart_html,
                "chart_data": chart_data,
                "data_points": len(df)
            }
            
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def create_comparison_chart(self, symbols: List[str], timeframe: str = '1d',
                               days: int = 30) -> Dict[str, Any]:
        """創建多個資產的對比圖"""
        try:
            fig = go.Figure()
            
            colors = ['#00D9FF', '#FF6B6B', '#4ECDC4', '#FFE66D', '#A8E6CF']
            
            for i, symbol in enumerate(symbols):
                result = self.crypto_data.get_ohlcv(symbol, timeframe, days)
                if result.get('success'):
                    df = pd.DataFrame(result['data'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    
                    # Normalize to percentage change
                    base_price = df['close'].iloc[0]
                    df['pct_change'] = ((df['close'] - base_price) / base_price) * 100
                    
                    fig.add_trace(go.Scatter(
                        x=df['timestamp'],
                        y=df['pct_change'],
                        mode='lines',
                        name=symbol,
                        line=dict(color=colors[i % len(colors)], width=2)
                    ))
            
            fig.update_layout(
                title='加密貨幣對比 (% 變化)',
                xaxis_title='時間',
                yaxis_title='變化 (%)',
                template='plotly_dark',
                hovermode='x unified',
                height=500
            )
            
            chart_html = fig.to_html(include_plotlyjs='cdn', div_id='comparison-chart')
            
            return {
                "success": True,
                "chart_html": chart_html,
                "symbols": symbols,
                "timeframe": timeframe
            }
            
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _calculate_limit(self, timeframe: str, start_date: str = None, 
                        end_date: str = None) -> int:
        """計算需要獲取的數據點數量"""
        if start_date and end_date:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            days = (end - start).days
            
            timeframe_minutes = {
                '1m': 1,
                '5m': 5,
                '15m': 15,
                '30m': 30,
                '1d': 1440,
                '3d': 4320,
                '1w': 10080
            }
            
            minutes = days * 1440
            tf_minutes = timeframe_minutes.get(timeframe, 1440)
            return min(int(minutes / tf_minutes), 1000)
        
        # Default limits
        default_limits = {
            '1m': 500,
            '5m': 500,
            '15m': 500,
            '1d': 90,   # 3 months
            '3d': 120,  # ~1 year
            '1w': 52    # 1 year
        }
        
        return default_limits.get(timeframe, 100)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行工具"""
        data_source = params.get('data_source', 'price')
        
        if data_source == 'price':
            symbol = params.get('symbol', 'BTC/USDT')
            timeframe = params.get('timeframe', '1d')
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            chart_type = params.get('chart_type', 'line')
            
            return self.create_price_chart(symbol, timeframe, start_date, end_date, chart_type)
        
        elif data_source == 'comparison':
            symbols = params.get('symbols', ['BTC/USDT', 'ETH/USDT'])
            timeframe = params.get('timeframe', '1d')
            days = params.get('days', 30)
            
            return self.create_comparison_chart(symbols, timeframe, days)
        
        elif data_source == 'custom':
            data = params.get('custom_data', [])
            title = params.get('title', '自定義圖表')
            x_label = params.get('x_label', '時間')
            y_label = params.get('y_label', '數值')
            
            if not data:
                return {
                    "success": False,
                    "error": "需要提供 custom_data 參數"
                }
            
            return self.create_custom_chart(data, title, x_label, y_label)
        
        else:
            return {
                "success": False,
                "error": f"未知的數據源: {data_source}"
            }
