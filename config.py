import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Ollama Configuration
    OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY', '')
    OLLAMA_URI = os.getenv('OLLAMA_URI', 'http://140.120.13.248:8787/ollama/')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gpt-oss:20b')
    OLLAMA_CHAT_API = f"{OLLAMA_URI}/api/chat"
    
    # News API
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    
    # Exchange API
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')
    
    # Server Configuration
    FLASK_PORT = int(os.getenv('FLASK_PORT', 11403))
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///crypto_trading.db')
    
    # Model Paths
    FINBERT_MODEL = 'ProsusAI/finbert'
    
    # Data Directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # Trading Parameters
    DEFAULT_INITIAL_CAPITAL = 10000
    DEFAULT_COMMISSION = 0.001
    
    # Supported Cryptocurrencies
    SUPPORTED_SYMBOLS = [
        'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 
        'ADA/USDT', 'SOL/USDT', 'DOT/USDT', 'DOGE/USDT'
    ]
