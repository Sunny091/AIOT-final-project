"""
MCP Tools - 工具定義層
(從 /user_data/1141/ML/ 複製並適配)

定義所有可供 LLM 調用的工具。
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ===== 工具定義 =====

TOOLS = [
    {
        "name": "get_current_price",
        "description": "獲取加密貨幣的即時價格。返回價格、24小時漲跌幅、成交量等資訊。",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "enum": ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOT", "DOGE"],
                    "description": "加密貨幣符號"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_price_history",
        "description": "獲取加密貨幣的歷史價格數據。可以用 days 指定近幾天，或用 start_date/end_date 指定日期範圍。",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "enum": ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOT", "DOGE"],
                    "description": "加密貨幣符號"
                },
                "days": {
                    "type": "integer",
                    "description": "查詢近幾天的數據 (1-365)"
                },
                "start_date": {
                    "type": "string",
                    "description": "開始日期，格式 YYYY-MM-DD"
                },
                "end_date": {
                    "type": "string",
                    "description": "結束日期，格式 YYYY-MM-DD"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_technical_analysis",
        "description": "獲取技術分析指標，包括 RSI、波動率、移動平均線等。",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "enum": ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOT", "DOGE"],
                    "description": "加密貨幣符號"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "run_backtest",
        "description": "執行交易策略回測。",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "交易對符號"
                },
                "strategy": {
                    "type": "string",
                    "enum": ["combined", "macd", "technical", "sentiment"],
                    "description": "策略類型"
                },
                "start_date": {
                    "type": "string",
                    "description": "回測開始日期"
                },
                "end_date": {
                    "type": "string",
                    "description": "回測結束日期"
                }
            },
            "required": []
        }
    },
]


def get_available_tools() -> list[dict]:
    """獲取所有可用工具的定義"""
    return TOOLS


def get_tools_for_llm() -> list[dict]:
    """獲取 LLM function calling 格式的工具定義"""
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
        }
        for tool in TOOLS
    ]


# ===== 工具實現 =====

def _get_current_price(symbol: str) -> dict:
    """獲取即時價格"""
    from data.scrapers.coincap_client import get_current_price
    return get_current_price(symbol)


def _get_price_history(symbol: str, days: int = None, start_date: str = None, end_date: str = None) -> dict:
    """獲取歷史價格"""
    from data.scrapers.coincap_client import get_price_history
    return get_price_history(symbol, days=days, start_date=start_date, end_date=end_date)


def _get_technical_analysis(symbol: str) -> dict:
    """技術分析（簡化版）"""
    from data.scrapers.coincap_client import get_price_history
    import random

    # 獲取歷史數據計算指標
    history = get_price_history(symbol, days=60)
    prices = [p["price_usd"] for p in history.get("data", [])]

    if len(prices) < 14:
        return {"error": "數據不足以計算技術指標"}

    # 計算簡單指標
    current_price = prices[-1] if prices else 0
    sma_20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else current_price
    sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else current_price

    # 簡單 RSI 計算
    gains = []
    losses = []
    for i in range(1, min(15, len(prices))):
        change = prices[-i] - prices[-i-1]
        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))

    avg_gain = sum(gains) / 14 if gains else 0.001
    avg_loss = sum(losses) / 14 if losses else 0.001
    rs = avg_gain / avg_loss if avg_loss > 0 else 1
    rsi = 100 - (100 / (1 + rs))

    # RSI 解讀
    if rsi > 70:
        rsi_signal = "超買（可能回調）"
    elif rsi < 30:
        rsi_signal = "超賣（可能反彈）"
    else:
        rsi_signal = "中性"

    # 計算波動率
    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
    volatility = (sum([r**2 for r in returns[-7:]]) / 7) ** 0.5 if len(returns) >= 7 else 0

    return {
        "symbol": symbol,
        "indicators": {
            "rsi_14": round(rsi, 2),
            "rsi_signal": rsi_signal,
            "volatility_7d": f"{volatility*100:.2f}%",
            "sma_20": round(sma_20, 2),
            "sma_50": round(sma_50, 2),
            "current_price": round(current_price, 2),
        },
        "trend": "上升" if current_price > sma_20 else "下降",
        "timestamp": datetime.now().isoformat()
    }


def _run_backtest(symbol: str = "BTC/USDT", strategy: str = "combined",
                  start_date: str = None, end_date: str = None) -> dict:
    """執行回測"""
    try:
        from backend.models.backtest_engine import BacktestTool
        tool = BacktestTool()
        params = {
            "symbol": symbol,
            "strategy_name": strategy,
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return tool.execute(params)
    except Exception as e:
        return {"error": f"回測執行失敗: {e}"}


# ===== 工具執行器 =====

def execute_tool(tool_name: str, arguments: dict) -> dict:
    """執行指定的工具"""
    tool_map = {
        "get_current_price": _get_current_price,
        "get_price_history": _get_price_history,
        "get_technical_analysis": _get_technical_analysis,
        "run_backtest": _run_backtest,
    }

    if tool_name not in tool_map:
        return {"error": f"未知工具: {tool_name}"}

    try:
        result = tool_map[tool_name](**arguments)
        return result
    except Exception as e:
        return {"error": str(e)}
