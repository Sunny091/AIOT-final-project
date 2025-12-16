import ccxt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

class CryptoDataTool:
    """MCP Tool for fetching cryptocurrency data"""
    
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "get_crypto_price",
            "description": "Get current price and market data for a cryptocurrency",
            "parameters": {
                "symbol": "Trading pair symbol (e.g., BTC/USDT)",
                "timeframe": "Optional timeframe for OHLCV data (1m, 5m, 15m, 1h, 4h, 1d)"
            }
        }
    
    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker information"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                "success": True,
                "symbol": symbol,
                "price": ticker['last'],
                "bid": ticker['bid'],
                "ask": ticker['ask'],
                "volume_24h": ticker['quoteVolume'],
                "change_24h": ticker['percentage'],
                "high_24h": ticker['high'],
                "low_24h": ticker['low'],
                "timestamp": ticker['timestamp']
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Dict[str, Any]:
        """Get OHLCV (candlestick) data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return {
                "success": True,
                "symbol": symbol,
                "timeframe": timeframe,
                "data": df.to_dict('records')
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_orderbook(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        """Get order book data"""
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return {
                "success": True,
                "symbol": symbol,
                "bids": orderbook['bids'][:limit],
                "asks": orderbook['asks'][:limit],
                "timestamp": orderbook['timestamp']
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_market_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed market information"""
        try:
            markets = self.exchange.load_markets()
            if symbol in markets:
                market = markets[symbol]
                return {
                    "success": True,
                    "symbol": symbol,
                    "base": market['base'],
                    "quote": market['quote'],
                    "active": market['active'],
                    "precision": market['precision'],
                    "limits": market['limits']
                }
            else:
                return {"success": False, "error": f"Symbol {symbol} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        symbol = params.get('symbol', 'BTC/USDT')
        action = params.get('action', 'price')
        
        if action == 'price':
            return self.get_current_price(symbol)
        elif action == 'ohlcv':
            timeframe = params.get('timeframe', '1h')
            limit = params.get('limit', 100)
            return self.get_ohlcv(symbol, timeframe, limit)
        elif action == 'orderbook':
            return self.get_orderbook(symbol)
        elif action == 'info':
            return self.get_market_info(symbol)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}


class CryptoNewsTool:
    """MCP Tool for fetching cryptocurrency news from local dataset"""
    
    def __init__(self, dataset_path: Optional[str] = None):
        self.dataset_path = dataset_path or 'data/cryptoNewsDataset'
        self.news_df = None
        self._load_dataset()
        
    def _load_dataset(self):
        """Load the crypto news dataset"""
        import os
        try:
            csv_dir = os.path.join(self.dataset_path, 'csvOutput')
            
            # Check if CSV files exist
            if not os.path.exists(csv_dir):
                print(f"數據集目錄不存在: {csv_dir}")
                print("系統將使用 RSS 降級方案")
                return
            
            csv_files = []
            for root, dirs, files in os.walk(csv_dir):
                for file in files:
                    if file.endswith('.csv'):
                        csv_files.append(os.path.join(root, file))
            
            if not csv_files:
                # Check for RAR files
                rar_files = [f for f in os.listdir(csv_dir) if f.endswith('.rar')]
                if rar_files:
                    print(f"⚠️  找到 {len(rar_files)} 個 RAR 壓縮文件")
                    print("   請先解壓數據集:")
                    print("   python extract_news_dataset.py")
                    print("")
                    print("   或手動解壓 data/cryptoNewsDataset/csvOutput/*.rar")
                    print("")
                print("系統將使用 RSS 降級方案")
                return
            
            # Load and combine all CSV files
            dfs = []
            for csv_file in csv_files:
                try:
                    # Try different encodings
                    for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                        try:
                            df = pd.read_csv(csv_file, encoding=encoding, low_memory=False)
                            dfs.append(df)
                            break
                        except UnicodeDecodeError:
                            continue
                except Exception as e:
                    print(f"⚠️  載入 {os.path.basename(csv_file)} 失敗: {e}")
            
            if dfs:
                self.news_df = pd.concat(dfs, ignore_index=True)
                print(f"✅ 載入 {len(self.news_df):,} 篇新聞 (來自 {len(csv_files)} 個文件)")
            else:
                print("系統將使用 RSS 降級方案")
                
        except Exception as e:
            print(f"載入數據集錯誤: {e}")
            print("系統將使用 RSS 降級方案")
            self.news_df = None
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "get_crypto_news",
            "description": "Fetch cryptocurrency news from local dataset for sentiment analysis",
            "parameters": {
                "symbol": "Cryptocurrency symbol (e.g., BTC, ETH, Bitcoin, Ethereum)",
                "limit": "Number of news articles to fetch (default: 10)"
            }
        }
    
    def fetch_news(self, symbol: str = 'BTC', limit: int = 10) -> Dict[str, Any]:
        """Fetch news articles about a cryptocurrency from dataset"""
        try:
            articles = []
            
            # If dataset is loaded, use it
            if self.news_df is not None and len(self.news_df) > 0:
                # Map symbol variations
                symbol_map = {
                    'BTC': ['bitcoin', 'btc'],
                    'ETH': ['ethereum', 'eth', 'ether'],
                    'BNB': ['binance', 'bnb'],
                    'XRP': ['ripple', 'xrp'],
                    'ADA': ['cardano', 'ada'],
                    'SOL': ['solana', 'sol'],
                    'DOT': ['polkadot', 'dot'],
                    'DOGE': ['dogecoin', 'doge']
                }
                
                search_terms = symbol_map.get(symbol.upper(), [symbol.lower()])
                
                # Filter news by symbol (search in title and content)
                filtered_df = self.news_df.copy()
                
                # Assuming dataset has 'title', 'text', 'date' columns
                # Adjust column names based on actual dataset structure
                title_col = None
                text_col = None
                date_col = None
                
                # Find column names
                for col in filtered_df.columns:
                    col_lower = col.lower()
                    if 'title' in col_lower or 'headline' in col_lower:
                        title_col = col
                    elif 'text' in col_lower or 'content' in col_lower or 'body' in col_lower:
                        text_col = col
                    elif 'date' in col_lower or 'time' in col_lower:
                        date_col = col
                
                if title_col:
                    # Filter by search terms
                    mask = filtered_df[title_col].str.lower().str.contains('|'.join(search_terms), na=False)
                    if text_col:
                        mask |= filtered_df[text_col].str.lower().str.contains('|'.join(search_terms), na=False)
                    
                    filtered_df = filtered_df[mask]
                    
                    # Sort by date if available
                    if date_col:
                        try:
                            filtered_df[date_col] = pd.to_datetime(filtered_df[date_col])
                            filtered_df = filtered_df.sort_values(date_col, ascending=False)
                        except:
                            pass
                    
                    # Get limited results
                    for _, row in filtered_df.head(limit).iterrows():
                        article = {
                            'title': str(row[title_col]) if title_col else 'No title',
                            'summary': str(row[text_col])[:500] if text_col else '',
                            'link': '',
                            'published': str(row[date_col]) if date_col else ''
                        }
                        articles.append(article)
            
            # Fallback: use RSS feeds if dataset not available or no results
            if len(articles) == 0:
                articles = self._fetch_from_rss(symbol, limit)
            
            return {
                "success": True,
                "symbol": symbol,
                "articles": articles,
                "count": len(articles),
                "source": "dataset" if self.news_df is not None else "rss"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _fetch_from_rss(self, symbol: str, limit: int) -> List[Dict[str, str]]:
        """Fallback method using RSS feeds"""
        try:
            import feedparser
            
            rss_urls = {
                'BTC': 'https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml',
                'ETH': 'https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml',
                'general': 'https://cointelegraph.com/rss'
            }
            
            feed_url = rss_urls.get(symbol.upper(), rss_urls['general'])
            feed = feedparser.parse(feed_url)
            
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title,
                    'summary': entry.get('summary', '')[:500],
                    'link': entry.link,
                    'published': entry.get('published', ''),
                })
            return articles
        except Exception as e:
            print(f"RSS fallback error: {e}")
            return []
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        symbol = params.get('symbol', 'BTC')
        limit = params.get('limit', 10)
        return self.fetch_news(symbol, limit)


class TradingStrategyTool:
    """MCP Tool for managing trading strategies"""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "manage_trading_strategy",
            "description": "Create, update, or get information about quantitative trading strategies",
            "parameters": {
                "action": "Action to perform (create, list, get, update, delete)",
                "strategy_name": "Name of the strategy",
                "config": "Strategy configuration (for create/update)"
            }
        }
    
    def __init__(self):
        self.strategies_file = 'data/strategies.json'
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure strategies file exists"""
        import os
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.strategies_file):
            with open(self.strategies_file, 'w') as f:
                json.dump({}, f)
    
    def create_strategy(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new trading strategy"""
        try:
            strategies = self._load_strategies()
            
            if name in strategies:
                return {"success": False, "error": "Strategy already exists"}
            
            strategies[name] = {
                "name": name,
                "config": config,
                "created_at": datetime.now().isoformat(),
                "status": "inactive"
            }
            
            self._save_strategies(strategies)
            return {"success": True, "message": f"Strategy '{name}' created", "strategy": strategies[name]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_strategies(self) -> Dict[str, Any]:
        """List all strategies"""
        try:
            strategies = self._load_strategies()
            return {"success": True, "strategies": list(strategies.values())}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_strategy(self, name: str) -> Dict[str, Any]:
        """Get a specific strategy"""
        try:
            strategies = self._load_strategies()
            if name in strategies:
                return {"success": True, "strategy": strategies[name]}
            else:
                return {"success": False, "error": "Strategy not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _load_strategies(self) -> Dict:
        """Load strategies from file"""
        with open(self.strategies_file, 'r') as f:
            return json.load(f)
    
    def _save_strategies(self, strategies: Dict):
        """Save strategies to file"""
        with open(self.strategies_file, 'w') as f:
            json.dump(strategies, f, indent=2)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        action = params.get('action', 'list')
        
        if action == 'create':
            name = params.get('strategy_name', '')
            config = params.get('config', {})
            return self.create_strategy(name, config)
        elif action == 'list':
            return self.list_strategies()
        elif action == 'get':
            name = params.get('strategy_name', '')
            return self.get_strategy(name)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
