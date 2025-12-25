import ccxt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import urllib.request
import urllib.error
import ssl

# ============================================================
# CoinGecko API Client (參考 ML 目錄的做法)
# ============================================================

# SSL context for certificate issues
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Symbol to CoinGecko ID mapping
COINGECKO_SYMBOL_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOT": "polkadot",
    "DOGE": "dogecoin",
}

# Mock 價格數據（當所有 API 都不可用時）
MOCK_PRICES = {
    "BTC/USDT": {"price": 98500.00, "change": 1.85, "volume": 32.5e9, "high": 99200, "low": 97100},
    "ETH/USDT": {"price": 3520.50, "change": 2.15, "volume": 18.2e9, "high": 3580, "low": 3450},
    "SOL/USDT": {"price": 195.30, "change": -0.45, "volume": 4.2e9, "high": 198, "low": 192},
    "BNB/USDT": {"price": 715.20, "change": 0.95, "volume": 1.8e9, "high": 720, "low": 708},
    "XRP/USDT": {"price": 2.35, "change": 3.25, "volume": 5.5e9, "high": 2.42, "low": 2.28},
    "ADA/USDT": {"price": 1.05, "change": 1.55, "volume": 1.2e9, "high": 1.08, "low": 1.02},
    "DOT/USDT": {"price": 7.85, "change": -1.20, "volume": 0.8e9, "high": 8.05, "low": 7.72},
    "DOGE/USDT": {"price": 0.325, "change": 4.50, "volume": 2.1e9, "high": 0.335, "low": 0.312},
}


class CoinGeckoClient:
    """CoinGecko API 客戶端 - 免費，無需 API Key"""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def _request(self, endpoint: str, params: dict = None) -> dict:
        """發送 HTTP GET 請求到 CoinGecko API"""
        url = f"{COINGECKO_BASE_URL}{endpoint}"

        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            url = f"{url}?{query}"

        try:
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/json')
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urllib.request.urlopen(req, timeout=self.timeout, context=SSL_CONTEXT) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            raise Exception(f"CoinGecko API error: {e}")

    def get_price(self, symbol: str) -> Dict[str, Any]:
        """獲取即時價格數據"""
        # 從交易對中提取幣種符號 (e.g., BTC/USDT -> BTC)
        base_symbol = symbol.split('/')[0].upper()
        asset_id = COINGECKO_SYMBOL_MAP.get(base_symbol)

        if not asset_id:
            raise ValueError(f"Unknown symbol: {base_symbol}")

        params = {
            "ids": asset_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
        }
        response = self._request("/simple/price", params)

        data = response.get(asset_id, {})
        return {
            "success": True,
            "symbol": symbol,
            "price": data.get("usd", 0),
            "bid": data.get("usd", 0) * 0.9999,  # 估算
            "ask": data.get("usd", 0) * 1.0001,  # 估算
            "volume_24h": data.get("usd_24h_vol", 0),
            "change_24h": data.get("usd_24h_change", 0),
            "high_24h": data.get("usd", 0) * 1.02,  # 估算
            "low_24h": data.get("usd", 0) * 0.98,   # 估算
            "market_cap": data.get("usd_market_cap", 0),
            "timestamp": int(datetime.now().timestamp() * 1000),
            "source": "coingecko"
        }

    def get_ohlcv(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """獲取歷史價格數據"""
        base_symbol = symbol.split('/')[0].upper()
        asset_id = COINGECKO_SYMBOL_MAP.get(base_symbol)

        if not asset_id:
            raise ValueError(f"Unknown symbol: {base_symbol}")

        params = {
            "vs_currency": "usd",
            "days": str(days),
        }
        response = self._request(f"/coins/{asset_id}/market_chart", params)

        prices = response.get("prices", [])

        # 轉換為 OHLCV 格式（簡化版，只有收盤價）
        data = []
        for p in prices:
            timestamp_ms = p[0]
            price = p[1]
            data.append({
                'timestamp': pd.to_datetime(timestamp_ms, unit='ms'),
                'open': price,
                'high': price * 1.005,
                'low': price * 0.995,
                'close': price,
                'volume': 0
            })

        return {
            "success": True,
            "symbol": symbol,
            "timeframe": "1d",
            "data": data,
            "source": "coingecko"
        }


def get_mock_price(symbol: str) -> Dict[str, Any]:
    """獲取 Mock 價格數據（當所有 API 都不可用時）"""
    mock = MOCK_PRICES.get(symbol, MOCK_PRICES["BTC/USDT"])
    return {
        "success": True,
        "symbol": symbol,
        "price": mock["price"],
        "bid": mock["price"] * 0.9999,
        "ask": mock["price"] * 1.0001,
        "volume_24h": mock["volume"],
        "change_24h": mock["change"],
        "high_24h": mock["high"],
        "low_24h": mock["low"],
        "timestamp": int(datetime.now().timestamp() * 1000),
        "source": "mock"
    }


def get_mock_ohlcv(symbol: str, days: int = 30) -> Dict[str, Any]:
    """獲取 Mock OHLCV 數據"""
    import hashlib

    mock = MOCK_PRICES.get(symbol, MOCK_PRICES["BTC/USDT"])
    base_price = mock["price"]

    data = []
    now = datetime.now()

    for i in range(days):
        date = now - timedelta(days=days - i - 1)
        # 使用確定性哈希產生一致的結果
        seed_str = f"{symbol}{date.strftime('%Y-%m-%d')}"
        hash_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        variation = ((hash_val % 10000) / 10000 - 0.5) * 0.1
        price = base_price * (1 + variation)

        data.append({
            'timestamp': date,
            'open': price * 0.998,
            'high': price * 1.01,
            'low': price * 0.99,
            'close': price,
            'volume': mock["volume"] / days
        })

    return {
        "success": True,
        "symbol": symbol,
        "timeframe": "1d",
        "data": data,
        "source": "mock"
    }


# Singleton CoinGecko client
_coingecko_client: CoinGeckoClient = None

def get_coingecko_client() -> CoinGeckoClient:
    """獲取 CoinGecko 客戶端單例"""
    global _coingecko_client
    if _coingecko_client is None:
        _coingecko_client = CoinGeckoClient()
    return _coingecko_client


# ============================================================
# CryptoDataTool (整合多數據源)
# ============================================================

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
                "timeframe": "Optional timeframe for OHLCV data (1m, 5m, 15m, 1d, 3d)"
            }
        }
    
    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current ticker information
        數據源優先順序: Binance -> CoinGecko -> Mock
        """
        # 1. 嘗試 Binance
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
                "timestamp": ticker['timestamp'],
                "source": "binance"
            }
        except Exception as binance_error:
            print(f"[Binance] API failed: {binance_error}, trying CoinGecko...")

        # 2. 嘗試 CoinGecko
        try:
            client = get_coingecko_client()
            return client.get_price(symbol)
        except Exception as coingecko_error:
            print(f"[CoinGecko] API failed: {coingecko_error}, using mock data...")

        # 3. 使用 Mock 數據
        return get_mock_price(symbol)
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1d', limit: int = 100) -> Dict[str, Any]:
        """
        Get OHLCV (candlestick) data
        數據源優先順序: Binance -> CoinGecko -> Mock
        """
        # 1. 嘗試 Binance
        try:
            # Handle custom timeframes not supported by CCXT
            if timeframe in ['3d']:
                # Use 1d data and resample
                days = int(timeframe[:-1])  # Extract number from '3d'
                actual_limit = limit * days  # Fetch more 1d candles
                ohlcv = self.exchange.fetch_ohlcv(symbol, '1d', limit=actual_limit)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

                # Resample to custom timeframe
                df.set_index('timestamp', inplace=True)
                resampled = df.resample(f'{days}D').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna()
                resampled.reset_index(inplace=True)

                return {
                    "success": True,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "data": resampled.to_dict('records'),
                    "source": "binance"
                }
            else:
                # Use native CCXT timeframe
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

                return {
                    "success": True,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "data": df.to_dict('records'),
                    "source": "binance"
                }
        except Exception as binance_error:
            print(f"[Binance] OHLCV API failed: {binance_error}, trying CoinGecko...")

        # 2. 嘗試 CoinGecko
        try:
            client = get_coingecko_client()
            # 將 limit 轉換為天數（估算）
            days = min(limit, 365)
            result = client.get_ohlcv(symbol, days=days)
            return result
        except Exception as coingecko_error:
            print(f"[CoinGecko] OHLCV API failed: {coingecko_error}, using mock data...")

        # 3. 使用 Mock 數據
        days = min(limit, 365)
        return get_mock_ohlcv(symbol, days=days)
    
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
            timeframe = params.get('timeframe', '1d')
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
