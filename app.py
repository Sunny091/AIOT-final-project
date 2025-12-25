"""
Crypto Trading MCP System - Flask App
(使用 ML 目錄的方法重構)

主要功能:
1. Ollama 對話 (使用 CryptoAgent)
2. 即時價格 (使用 CoinGecko API)
3. 價格趨勢圖 (使用 Chart.js)
4. 回測功能 (保留原有)
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os
import re
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

app = Flask(__name__,
            template_folder='frontend/templates',
            static_folder='frontend/static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Lazy initialization
_agent = None


def get_agent():
    """Lazy load CryptoAgent"""
    global _agent
    if _agent is None:
        print("[INIT] Loading CryptoAgent...")
        from orchestrator.agent import CryptoAgent
        _agent = CryptoAgent(
            ollama_host=Config.OLLAMA_URI.rstrip('/'),
            model=Config.OLLAMA_MODEL,
            timeout=60.0,
            api_key=Config.OLLAMA_API_KEY
        )
        print(f"[INIT] ✅ CryptoAgent loaded (model: {Config.OLLAMA_MODEL})")
    return _agent


# ============================================================
# 頁面路由
# ============================================================

@app.route('/')
def index():
    """主聊天界面"""
    return render_template('index.html')


@app.route('/backtest')
def backtest():
    """回測結果頁面"""
    return render_template('backtest.html')


# ============================================================
# 聊天 API (使用 ML 的方法)
# ============================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint - 使用 CryptoAgent 處理

    智能判斷:
    - 圖表請求 → 返回 chart_data
    - 價格查詢 → 調用工具
    - 一般問題 → LLM 回答
    """
    try:
        data = request.get_json()
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400

        print(f"[API] Received message: {message}")

        # 檢測幣種
        symbol = None
        message_lower = message.lower()
        for s in ['btc', 'eth', 'sol', 'bnb', 'xrp', 'ada', 'dot', 'doge']:
            if s in message_lower:
                symbol = s.upper()
                break

        # 檢測是否為圖表請求
        chart_keywords = ["走勢", "圖表", "chart", "歷史", "價格圖", "趨勢圖", "近", "過去", "最近"]
        is_chart_request = any(kw in message_lower for kw in chart_keywords)

        # 檢測時間範圍
        has_time_range = bool(
            re.search(r'\d{1,2}[月\/]\d{1,2}', message) or
            re.search(r'\d{4}-\d{1,2}-\d{1,2}', message) or
            re.search(r'(\d+)\s*(?:天|日|週|周|月)', message_lower)
        )

        # 如果是明確的圖表請求，直接獲取數據
        if symbol and (is_chart_request or has_time_range):
            from data.scrapers.coincap_client import get_price_history

            # 解析天數
            days = 30
            days_match = re.search(r'(\d+)\s*(?:天|日)', message_lower)
            if days_match:
                days = min(int(days_match.group(1)), 365)
            elif "一週" in message_lower or "一周" in message_lower:
                days = 7
            elif "兩週" in message_lower:
                days = 14
            elif "一個月" in message_lower:
                days = 30
            elif "三個月" in message_lower:
                days = 90

            # 解析日期範圍
            start_date = None
            end_date = None

            # 匹配日期範圍
            date_range_match = re.search(
                r'(\d{1,2}[\/月]\d{1,2}日?|\d{4}-\d{1,2}-\d{1,2})\s*(?:到|至|~)\s*(\d{1,2}[\/月]\d{1,2}日?|\d{4}-\d{1,2}-\d{1,2}|現在|今天)',
                message
            )
            if date_range_match:
                start_date = _parse_date(date_range_match.group(1))
                end_str = date_range_match.group(2)
                if end_str in ['現在', '今天']:
                    end_date = datetime.now().strftime("%Y-%m-%d")
                else:
                    end_date = _parse_date(end_str)

            # 獲取歷史數據
            if start_date and end_date:
                history = get_price_history(symbol, start_date=start_date, end_date=end_date)
                period_label = f"{start_date} ~ {end_date}"
            else:
                history = get_price_history(symbol, days=days)
                period_label = f"近 {days} 天"

            chart_data = {
                "symbol": symbol,
                "timestamps": [p["timestamp"] for p in history["data"]],
                "prices": [p["price_usd"] for p in history["data"]],
                "period": period_label,
                "source": history["source"]
            }

            return jsonify({
                "success": True,
                "response": f"以下是 {symbol} {period_label} 的價格走勢圖：",
                "chart_data": chart_data
            })

        # 使用 CryptoAgent 處理
        try:
            agent = get_agent()
            result = agent.chat(message)

            return jsonify({
                "success": True,
                "response": result.get("response", ""),
                "chart_data": result.get("chart_data"),
                "tool_results": result.get("tool_results", [])
            })

        except Exception as e:
            print(f"[API] Agent error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'response': f'處理請求時發生錯誤: {e}'
            }), 500

    except Exception as e:
        print(f"[API] Request error: {e}")
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


def _parse_date(date_str: str) -> str:
    """解析日期字串為 YYYY-MM-DD 格式"""
    now = datetime.now()
    year = now.year

    # YYYY-MM-DD
    if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', date_str):
        parts = date_str.split('-')
        return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"

    # MM/DD
    if re.match(r'^\d{1,2}/\d{1,2}$', date_str):
        parts = date_str.split('/')
        return f"{year}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"

    # X月X日
    cn_match = re.match(r'(\d{1,2})月(\d{1,2})日?', date_str)
    if cn_match:
        return f"{year}-{cn_match.group(1).zfill(2)}-{cn_match.group(2).zfill(2)}"

    return None


# ============================================================
# 即時價格 API (使用 CoinGecko)
# ============================================================

@app.route('/api/price/<symbol>', methods=['GET'])
def get_price(symbol):
    """獲取即時價格"""
    try:
        from data.scrapers.coincap_client import get_current_price
        result = get_current_price(symbol.upper())
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# 圖表數據 API
# ============================================================

@app.route('/api/chart-data', methods=['POST'])
def get_chart_data():
    """獲取圖表數據"""
    try:
        from data.scrapers.coincap_client import get_price_history

        data = request.get_json() or {}
        symbol = data.get('symbol', 'BTC').upper()
        days = data.get('days', 30)
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date:
            history = get_price_history(symbol, start_date=start_date, end_date=end_date)
        else:
            history = get_price_history(symbol, days=days)

        return jsonify({
            "success": True,
            "symbol": symbol,
            "timestamps": [p["timestamp"] for p in history["data"]],
            "prices": [p["price_usd"] for p in history["data"]],
            "source": history["source"]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# 回測 API (保留原有功能)
# ============================================================

@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    """執行回測"""
    try:
        data = request.get_json()

        from backend.models.backtest_engine import BacktestTool
        tool = BacktestTool()
        result = tool.execute(data)

        return jsonify(result)

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/backtest/results', methods=['GET'])
def get_backtest_results():
    """獲取回測結果"""
    try:
        limit = request.args.get('limit', 10, type=int)

        from backend.models.backtest_engine import BacktestTool
        tool = BacktestTool()
        result = tool.get_results(limit)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# 策略 API
# ============================================================

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """獲取所有策略"""
    try:
        from backend.mcp_tools.crypto_tools import TradingStrategyTool
        tool = TradingStrategyTool()
        result = tool.list_strategies()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/strategies', methods=['POST'])
def create_strategy():
    """創建新策略"""
    try:
        data = request.get_json()
        from backend.mcp_tools.crypto_tools import TradingStrategyTool
        tool = TradingStrategyTool()
        result = tool.create_strategy(data.get('name'), data.get('config', {}))
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# 工具 API
# ============================================================

@app.route('/api/tools', methods=['GET'])
def list_tools():
    """列出可用工具"""
    from mcp.tools import get_available_tools
    return jsonify({"tools": get_available_tools()})


@app.route('/api/llm/status', methods=['GET'])
def llm_status():
    """檢查 LLM 連接狀態"""
    try:
        agent = get_agent()
        status = agent.check_connection()
        return jsonify(status)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})


@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """重置對話"""
    global _agent
    _agent = None
    return jsonify({'success': True, 'message': 'Conversation reset'})


# ============================================================
# WebSocket
# ============================================================

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('message')
def handle_message(data):
    """處理即時消息"""
    try:
        message = data.get('message', '')
        agent = get_agent()
        result = agent.chat(message)
        emit('response', {
            'success': True,
            'response': result.get('response', ''),
            'chart_data': result.get('chart_data')
        })
    except Exception as e:
        emit('error', {'error': str(e)})


# ============================================================
# 啟動
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Crypto Trading MCP System")
    print("=" * 60)
    print(f"Server: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"Ollama: {Config.OLLAMA_URI}")
    print(f"Model:  {Config.OLLAMA_MODEL}")
    print("=" * 60)

    socketio.run(app,
                host=Config.FLASK_HOST,
                port=Config.FLASK_PORT,
                debug=Config.DEBUG,
                allow_unsafe_werkzeug=True)
