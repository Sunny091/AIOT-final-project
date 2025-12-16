from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from backend.mcp_orchestrator import MCPOrchestrator

app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Lazy initialization of orchestrator
orchestrator = None

def get_orchestrator():
    """Lazy load orchestrator"""
    global orchestrator
    if orchestrator is None:
        print("[INIT] Loading MCP Orchestrator...")
        orchestrator = MCPOrchestrator()
        print("[INIT] ✅ Orchestrator loaded")
    return orchestrator


@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')


@app.route('/backtest')
def backtest():
    """Backtest results page"""
    return render_template('backtest.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint - process user message through MCP
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400
        
        print(f"[API] Received message: {user_message}")
        
        # Process message through MCP orchestrator
        try:
            orch = get_orchestrator()
            response = orch.process_user_message(user_message)
            print(f"[API] Response generated: {response.get('success', False)}")
            return jsonify(response)
        except Exception as e:
            print(f"[API] Orchestrator error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': '處理請求時發生錯誤',
                'error': str(e)
            }), 500
        
    except Exception as e:
        print(f"[API] Request error: {e}")
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/price/<symbol>', methods=['GET'])
def get_price(symbol):
    """Get current price for a symbol"""
    try:
        from backend.mcp_tools.crypto_tools import CryptoDataTool
        
        tool = CryptoDataTool()
        result = tool.get_current_price(symbol)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    """Run a backtest"""
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
    """Get backtest results"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        from backend.models.backtest_engine import BacktestTool
        tool = BacktestTool()
        result = tool.get_results(limit)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analysis/combined', methods=['POST'])
def combined_analysis():
    """Run combined analysis"""
    try:
        data = request.get_json()
        
        result = orchestrator._combined_analysis(data)
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get all trading strategies"""
    try:
        from backend.mcp_tools.crypto_tools import TradingStrategyTool
        
        tool = TradingStrategyTool()
        result = tool.list_strategies()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/strategies', methods=['POST'])
def create_strategy():
    """Create a new trading strategy"""
    try:
        data = request.get_json()
        
        from backend.mcp_tools.crypto_tools import TradingStrategyTool
        tool = TradingStrategyTool()
        
        result = tool.create_strategy(
            data.get('name'),
            data.get('config', {})
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation history"""
    try:
        orchestrator.reset_conversation()
        return jsonify({'success': True, 'message': 'Conversation reset'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'data': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('message')
def handle_message(data):
    """Handle real-time messages"""
    try:
        message = data.get('message', '')
        
        # Process through orchestrator
        response = orchestrator.process_user_message(message)
        
        # Emit response back to client
        emit('response', response)
        
    except Exception as e:
        emit('error', {'error': str(e)})


if __name__ == '__main__':
    print(f"Starting Crypto Trading MCP System on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"Using Ollama model: {Config.OLLAMA_MODEL}")
    print(f"Access the application at: http://localhost:{Config.FLASK_PORT}")
    
    socketio.run(app, 
                host=Config.FLASK_HOST, 
                port=Config.FLASK_PORT, 
                debug=Config.DEBUG,
                allow_unsafe_werkzeug=True)
