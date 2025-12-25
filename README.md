# AI Crypto Trading Assistant

基於 MCP (Model Context Protocol) 架構的智能加密貨幣分析與量化交易系統

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-red.svg)](https://pytorch.org/)

## Demo

查看系統演示：[Demo](demo/README.md)

## Features

-   **自然語言交互** - Ollama + GPT-OSS 20B 模型
-   **實時價格查詢** - Binance API
-   **情感分析** - FinBERT 新聞情緒分析
-   **技術分析** - LSTM + Attention 深度學習模型
-   **量化回測** - 情感/技術/綜合策略
-   **圖表可視化** - 價格走勢圖、K 線圖

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start server
./start.sh
```

Open browser: `http://localhost:11404`

## Usage

| Command       | Description             |
| ------------- | ----------------------- |
| 查詢 BTC 價格 | Get real-time price     |
| 分析 BTC 走勢 | Technical analysis      |
| BTC 新聞情感  | News sentiment analysis |
| 顯示 BTC 圖表 | Price chart             |

## Project Structure

```
.
├── app.py                 # Flask application
├── config.py              # Configuration
├── start.sh               # Start script
├── backend/
│   ├── mcp_orchestrator.py
│   ├── mcp_tools/         # MCP tools
│   └── models/            # ML models
├── frontend/              # Web UI
├── demo/                  # Demo videos
├── docs/                  # Documentation
└── data/                  # Datasets
```

## MCP Tools

| Tool                 | Function                    |
| -------------------- | --------------------------- |
| `get_crypto_price`   | Real-time price query       |
| `get_crypto_ohlcv`   | OHLCV candlestick data      |
| `analyze_sentiment`  | FinBERT sentiment analysis  |
| `technical_analysis` | DL-based technical analysis |
| `run_backtest`       | Quantitative backtesting    |
| `create_chart`       | Chart generation            |

## Backtest Performance

| Strategy  | Return  | Win Rate | Max Drawdown |
| --------- | ------- | -------- | ------------ |
| Technical | +32.80% | 77.8%    | -17.77%      |
| Sentiment | +25.50% | N/A      | -29.99%      |
| Combined  | +5.08%  | 100%     | -2.83%       |

## Documentation

See [docs/](docs/) for detailed documentation.

## License

MIT License
