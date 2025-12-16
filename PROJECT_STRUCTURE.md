# 專案結構說明

## 📁 目錄結構

```
mcp_system_final/
├── README.md                    # 專案主要說明
├── requirements.txt             # Python 依賴列表
├── requirements-minimal.txt     # 最小化依賴
├── start.sh                     # 快速啟動腳本
├── app.py                       # Flask 應用主程序
├── config.py                    # 配置文件
├── server.log                   # 服務器日誌
│
├── docs/                        # 📚 文檔目錄
│   ├── README.md               # 文檔索引
│   ├── INSTALL_GUIDE.md        # 安裝指南
│   ├── USAGE_GUIDE.md          # 使用指南
│   ├── ACCESS_GUIDE.md         # 訪問指南
│   ├── FEATURES.md             # 功能說明
│   ├── architecture.md         # 架構設計
│   └── NEWS_DATASET_README.md  # 新聞數據集說明
│
├── backend/                     # 🔧 後端代碼
│   ├── __init__.py
│   ├── mcp_orchestrator.py     # MCP 協調器
│   ├── ollama_client.py        # Ollama 客戶端
│   │
│   ├── mcp_tools/              # MCP 工具集
│   │   ├── __init__.py
│   │   ├── crypto_tools.py     # 加密貨幣工具
│   │   └── trading_tools.py    # 交易工具
│   │
│   ├── models/                 # AI 模型
│   │   ├── __init__.py
│   │   ├── sentiment_analyzer.py    # FinBERT 情感分析
│   │   ├── technical_analysis.py    # 技術分析模型
│   │   └── price_predictor.py       # 價格預測模型
│   │
│   └── strategies/             # 交易策略
│       ├── __init__.py
│       ├── base_strategy.py    # 基礎策略類
│       └── backtest_engine.py  # 回測引擎
│
├── frontend/                    # 🎨 前端代碼
│   ├── templates/              # HTML 模板
│   │   ├── index.html         # 主頁面（聊天界面）
│   │   └── backtest.html      # 回測結果頁面
│   │
│   ├── static/                # 靜態資源
│   │   ├── css/
│   │   │   └── style.css      # 樣式表
│   │   ├── js/
│   │   │   └── main.js        # 主要 JavaScript
│   │   └── images/            # 圖片資源
│
├── data/                       # 📊 數據目錄
│   ├── cryptoNewsDataset/     # 新聞數據集
│   │   └── csvOutput/         # CSV 文件（需解壓 RAR）
│   ├── strategies.json        # 保存的策略
│   └── backtest_results.json  # 回測結果
│
├── tests/                      # 🧪 測試代碼
│   ├── __init__.py
│   └── test_*.py              # 測試文件
│
└── scripts/                    # 🔨 工具腳本
    ├── check_dependencies.py   # 依賴檢查
    ├── verify_news_dataset.py  # 數據集驗證
    └── extract_news_dataset.py # 數據集解壓
```

## 📝 核心文件說明

### 根目錄文件

| 文件 | 說明 |
|------|------|
| `README.md` | 專案主要說明文檔 |
| `app.py` | Flask 應用主程序，處理路由和 API |
| `config.py` | 系統配置（Ollama、API 密鑰等）|
| `start.sh` | 一鍵啟動腳本 |
| `requirements.txt` | 完整 Python 依賴 |
| `requirements-minimal.txt` | 最小化依賴（用於測試）|

### Backend 模塊

#### `mcp_orchestrator.py`
- MCP 協調器，核心邏輯
- 處理用戶消息
- 選擇和調用 MCP 工具
- 與 Ollama 通訊

#### `mcp_tools/`
- **crypto_tools.py**: 加密貨幣相關工具
  - 價格查詢
  - 新聞獲取
  - 市場數據
  
- **trading_tools.py**: 交易相關工具
  - 策略執行
  - 回測運行
  - 訂單管理

#### `models/`
- **sentiment_analyzer.py**: FinBERT 情感分析
- **technical_analysis.py**: 技術指標計算（DL 模型）
- **price_predictor.py**: 價格預測（Bi-LSTM + Attention）

#### `strategies/`
- **base_strategy.py**: 策略基類
- **backtest_engine.py**: Backtrader 回測引擎

### Frontend 結構

#### `templates/`
- `index.html`: 主聊天界面
- `backtest.html`: 回測結果展示

#### `static/`
- CSS: 樣式和主題
- JS: 前端邏輯、WebSocket 通訊
- Images: 圖標和圖片

### Data 目錄

#### `cryptoNewsDataset/`
- 248,000+ 篇新聞數據
- 支援 660+ 種幣種
- 時間範圍：2017-2023

#### 運行時數據
- `strategies.json`: 用戶保存的交易策略
- `backtest_results.json`: 回測結果歷史

## 🔄 數據流程

```
用戶輸入 (前端)
    ↓
WebSocket / HTTP API
    ↓
app.py (Flask 路由)
    ↓
MCPOrchestrator (協調器)
    ↓
Ollama (gpt-oss:20b) - 理解意圖
    ↓
選擇 MCP Tool
    ↓
執行工具 (查詢、分析、交易)
    ↓
返回結果
    ↓
前端展示
```

## 🛠️ 開發工作流

1. **修改後端邏輯**: 編輯 `backend/` 下的文件
2. **修改前端界面**: 編輯 `frontend/` 下的文件
3. **添加新工具**: 在 `backend/mcp_tools/` 添加新類
4. **添加新策略**: 在 `backend/strategies/` 創建新策略
5. **測試**: 運行 `tests/` 下的測試文件

## 📦 依賴管理

```bash
# 安裝完整依賴
pip install -r requirements.txt

# 僅安裝核心依賴
pip install -r requirements-minimal.txt

# 檢查依賴
python scripts/check_dependencies.py
```

## 🚀 啟動流程

1. **安裝依賴**: `pip install -r requirements.txt`
2. **配置環境**: 編輯 `config.py` 或 `.env`
3. **下載數據集**: `git clone` 新聞數據集（可選）
4. **啟動服務**: `./start.sh` 或 `python app.py`
5. **訪問界面**: http://localhost:11403

## 📚 擴展指南

### 添加新的 MCP 工具

1. 在 `backend/mcp_tools/` 創建新文件
2. 繼承基礎工具類
3. 實現 `execute()` 方法
4. 在 `mcp_orchestrator.py` 註冊工具

### 添加新的 AI 模型

1. 在 `backend/models/` 創建新文件
2. 實現模型載入和推理邏輯
3. 在 MCP 工具中調用

### 添加新頁面

1. 在 `frontend/templates/` 創建 HTML
2. 在 `app.py` 添加路由
3. 在 `frontend/static/` 添加 CSS/JS

## 🔍 日誌和調試

- **服務器日誌**: `server.log`
- **Ollama 日誌**: 檢查 Ollama 服務
- **瀏覽器控制台**: 查看前端錯誤
- **Python 調試**: 設置 `DEBUG=True` in `config.py`

---

**最後更新**: 2024-12-16
**版本**: 2.0
