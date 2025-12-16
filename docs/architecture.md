# MCP 加密貨幣交易系統 - 專案架構

## 系統概述

本專案實作了一個基於 MCP (Model Context Protocol) 架構的智能加密貨幣交易系統，整合了：

1. **GPT-OSS 20B** - 自然語言理解與工具選擇
2. **FinBERT** - 金融新聞情感分析（SOTA）
3. **Deep Learning** - LSTM+Transformer 技術分析
4. **Backtrader** - 量化交易回測引擎

## MCP 架構設計

```
┌─────────────────────────────────────────────────────────────┐
│                         使用者介面                            │
│                   (Web Chat Interface)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ NLP 指令
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Orchestrator                         │
│                  (協調器 - 核心調度層)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  GPT-OSS 20B (Ollama)                                │  │
│  │  - 理解使用者意圖                                       │  │
│  │  - 選擇適當的 MCP 工具                                  │  │
│  │  - 提取參數                                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ 工具調用
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      MCP Tools Layer                        │
│                      (工具執行層)                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Crypto Data  │  │ Crypto News  │  │  Sentiment   │     │
│  │     Tool     │  │     Tool     │  │  Analysis    │     │
│  │              │  │              │  │     Tool     │     │
│  │  - 價格查詢   │  │  - 新聞抓取   │  │  - FinBERT   │     │
│  │  - K線數據    │  │  - RSS feeds │  │  - 情感分類   │     │
│  │  - 市場深度   │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Technical   │  │   Trading    │  │   Backtest   │     │
│  │  Analysis    │  │   Strategy   │  │     Tool     │     │
│  │              │  │     Tool     │  │              │     │
│  │ - LSTM/Trans │  │  - 策略管理   │  │ - 回測引擎    │     │
│  │ - 技術指標    │  │  - 配置存儲   │  │ - 績效分析    │     │
│  │ - 價格預測    │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Sources Layer                       │
│                      (數據源層)                              │
├─────────────────────────────────────────────────────────────┤
│  • Binance API (CCXT)                                       │
│  • News RSS Feeds                                           │
│  • HuggingFace Models                                       │
│  • Local Storage (JSON/SQLite)                              │
└─────────────────────────────────────────────────────────────┘
```

## 數據流

### 1. 用戶查詢流程
```
用戶輸入 → Ollama Client → MCP Orchestrator
          ↓
    工具選擇與參數提取
          ↓
    對應 MCP Tool 執行
          ↓
    結果格式化 → 返回用戶
```

### 2. 綜合分析流程
```
用戶請求「綜合分析」
    ↓
┌───────────────────────────────┐
│  1. 價格數據 (Crypto Data)     │
│  2. 新聞數據 (Crypto News)     │
│  3. 情感分析 (Sentiment Tool)  │
│  4. 技術分析 (Technical Tool)  │
└───────────────────────────────┘
    ↓
整合所有結果 → 生成投資建議
```

### 3. 回測流程
```
回測請求
    ↓
獲取歷史數據 (OHLCV)
    ↓
載入策略 (Sentiment/MACD/ML)
    ↓
Backtrader 引擎執行
    ↓
計算績效指標 → 保存結果
```

## 核心組件

### 1. Ollama Client
- 封裝 Ollama API 調用
- 支援對話歷史管理
- 工具選擇能力

### 2. MCP Orchestrator
- 管理所有 MCP 工具
- 解析 LLM 響應
- 執行工具調用
- 整合多工具結果

### 3. 情感分析引擎
```python
FinBERT → Tokenization → Model Inference → 
Softmax → Sentiment (Positive/Neutral/Negative)
```

### 4. 技術分析引擎
```python
OHLCV Data → Feature Engineering (20+ indicators) →
LSTM/Transformer → Price Prediction → Trading Signals
```

### 5. 回測引擎
```python
Historical Data + Strategy → Backtrader →
Performance Metrics (Sharpe, Drawdown, Win Rate)
```

## API 端點

| 端點 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 聊天介面頁面 |
| `/backtest` | GET | 回測結果頁面 |
| `/api/chat` | POST | 處理用戶消息 |
| `/api/price/<symbol>` | GET | 獲取價格 |
| `/api/backtest/run` | POST | 運行回測 |
| `/api/backtest/results` | GET | 獲取回測結果 |
| `/api/analysis/combined` | POST | 綜合分析 |
| `/api/strategies` | GET | 獲取策略列表 |
| `/api/strategies` | POST | 創建策略 |
| `/api/reset` | POST | 重置對話 |

## 技術特點

### 1. 模組化設計
每個 MCP 工具都是獨立模組，易於擴展和維護

### 2. 異步處理
使用 Flask-SocketIO 支援實時通訊

### 3. 錯誤處理
完整的異常捕獲和用戶友好的錯誤提示

### 4. 數據持久化
- JSON 存儲策略和回測結果
- 支援擴展到 SQLite/PostgreSQL

### 5. 響應式設計
前端適配桌面和移動設備

## 擴展性

### 添加新工具
1. 創建工具類並實現接口
2. 在 Orchestrator 中註冊
3. 更新工具定義列表

### 添加新策略
1. 繼承 `bt.Strategy`
2. 實現交易邏輯
3. 在回測引擎中註冊

### 添加新模型
1. 實現模型類
2. 集成到技術分析引擎
3. 更新預測接口

## 性能優化

1. **模型懶加載**：只在需要時加載 FinBERT
2. **緩存機制**：價格數據可添加 Redis 緩存
3. **批量處理**：情感分析支援批量文本
4. **異步任務**：長時間運行的回測可改為異步

## 安全考慮

1. API Key 環境變數存儲
2. 輸入驗證和清理
3. CORS 配置
4. 錯誤信息不暴露敏感數據
