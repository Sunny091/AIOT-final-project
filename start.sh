#!/bin/bash

echo "======================================"
echo "  MCP 加密貨幣交易系統 - 快速啟動"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 創建虛擬環境..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 激活虛擬環境..."
source venv/bin/activate

# Install dependencies
echo "📥 安裝依賴包..."
pip install -q --upgrade pip

# Try to install from requirements.txt
if pip install -q -r requirements.txt 2>/dev/null; then
    echo "✅ 依賴安裝成功"
else
    echo "⚠️  完整依賴安裝失敗，嘗試最小化安裝..."
    if [ -f "requirements-minimal.txt" ]; then
        pip install -q -r requirements-minimal.txt
    else
        # Fallback to manual installation
        pip install -q flask flask-cors flask-socketio ccxt pandas numpy torch transformers backtrader feedparser python-dotenv
    fi
fi

# Check dependencies
echo ""
echo "🔍 檢查依賴..."
python check_dependencies.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 部分依賴缺失，請手動安裝:"
    echo "   pip install -r requirements.txt"
    echo ""
    echo "或參考安裝指南: INSTALL_GUIDE.md"
    echo ""
    read -p "是否繼續啟動? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在，使用 .env.example 創建"
    cp .env.example .env
    echo "⚙️  請編輯 .env 文件並填入您的 API 密鑰"
fi

# Create data directory
mkdir -p data

# Initialize data files
if [ ! -f "data/strategies.json" ]; then
    echo "{}" > data/strategies.json
fi

if [ ! -f "data/backtest_results.json" ]; then
    echo "[]" > data/backtest_results.json
fi

# Check for news dataset
if [ ! -d "data/cryptoNewsDataset" ]; then
    echo ""
    echo "💡 提示: 未找到新聞數據集"
    echo "   建議下載以獲得更好的新聞分析體驗:"
    echo "   cd data && git clone https://github.com/soheilrahsaz/cryptoNewsDataset.git"
    echo "   系統將使用 RSS 降級方案"
fi

echo ""
echo "✅ 安裝完成！"
echo ""
echo "🚀 啟動應用程序..."
echo "   訪問: http://localhost:11403"
echo ""
echo "按 Ctrl+C 停止服務器"
echo ""

# Run the application
python app.py
