# 加密貨幣 AI 交易助手 - MCP System 🚀

基於 MCP (Model Context Protocol) 架構的智能加密貨幣分析與量化交易系統

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-red.svg)](https://pytorch.org/)
[![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)](.)

## ✨ 核心特性

- 🤖 **自然語言交互** - 使用 Ollama + GPT-OSS 20B 模型
- 💰 **實時價格查詢** - 整合 Binance API
- 💭 **情感分析** - FinBERT 新聞情緒分析
- 🔧 **技術分析** - LSTM + Attention 深度學習模型
- 📊 **量化回測** - 三種策略可選（情感/技術/綜合）
- 📈 **圖表可視化** - 實時價格走勢圖、K線圖、自定義數據圖表
- 🌐 **Web 界面** - 友好的操作界面

## 🚀 快速開始

### 1. 啟動系統

```bash
cd /user_data/1141/aiot/final/mcp_system_final
./start.sh
```

### 2. 訪問界面

打開瀏覽器訪問：`http://localhost:11403`

### 3. 開始使用

- **查詢價格**：點擊「查詢 BTC 價格」或輸入「查詢 BTC 價格」
- **技術分析**：點擊「分析 BTC」或輸入「分析 BTC 走勢」
- **圖表可視化**：點擊「價格走勢圖」或輸入「顯示 BTC 過去一週的價格走勢圖」
- **量化回測**：訪問 `/backtest` 頁面執行回測

### 4. 圖表功能 📊

系統支援多種圖表類型：

```
# 價格走勢圖（折線圖）
"顯示 BTC 過去一週的價格走勢圖"
"繪製 ETH/USDT 1小時K線圖"

# K線圖（蠟燭圖）
"顯示 BTC/USDT 的K線圖，時間範圍1天"

# 自定義時間範圍
"顯示 BTC 從 2024-12-01 到 2024-12-15 的價格走勢"
```

## 📊 回測性能

### 長期表現（2024 全年）

| 策略 | 回報率 | 勝率 | 最大回撤 |
|------|--------|------|----------|
| 技術分析 🥇 | **+32.80%** | 77.8% | -17.77% |
| 情感分析 🥈 | +25.50% | N/A | -29.99% |

### 綜合策略優化後

| 指標 | 優化前 | 優化後 |
|------|--------|--------|
| 回報率 | 0.00% | **+5.08%** ✅ |
| 勝率 | N/A | **100%** ✅ |
| 最大回撤 | 0% | -2.83% ✅ |

## 🎯 三種策略

### 1. 情感分析策略 💭
- 使用 FinBERT 分析新聞情感
- 適合新聞驅動的市場
- 捕捉情緒變化

### 2. 技術分析策略 🔧
- LSTM + Attention 深度學習模型
- RSI、MACD、布林帶等技術指標
- **最佳長期回報**（+32.80%）

### 3. 綜合策略 🎯 (推薦)
- 加權評分系統（40% 情感 + 60% 技術）
- **最高勝率**（100%）
- **最小回撤**（-2.83%）
- 風險控制最佳

## 🏗️ 技術架構

```
Python 3.11
├── Flask                  # Web 框架
├── Flask-SocketIO         # WebSocket 實時通信
├── Ollama                 # LLM 推理引擎
├── Transformers           # FinBERT 模型
├── PyTorch                # 深度學習
├── Backtrader             # 量化回測
└── CCXT                   # 加密貨幣 API
```

## 📁 項目結構

```
mcp_system_final/
├── app.py                          # Flask 主應用
├── start.sh                        # 啟動腳本
├── backend/
│   ├── mcp_orchestrator.py         # MCP 協調器
│   ├── mcp_tools/
│   │   ├── crypto_tools.py         # 加密貨幣工具
│   │   └── chart_tool.py           # 圖表工具
│   └── models/
│       ├── backtest_engine.py      # 回測引擎
│       ├── technical_analysis.py   # DL 模型
│       └── sentiment_analysis.py   # 情感分析
├── frontend/
│   ├── index.html                  # 主頁面
│   └── backtest.html              # 回測頁面
└── data/
    └── cryptoNewsDataset/         # 新聞數據集
```

## 🔧 MCP 工具系統

| 工具 | 功能 | 說明 |
|------|------|------|
| `get_crypto_price` | 價格查詢 | 獲取實時價格和市場數據 |
| `get_crypto_data` | 歷史數據 | OHLCV K線數據 |
| `analyze_sentiment` | 情感分析 | FinBERT 新聞情緒分析 |
| `technical_analysis` | 技術分析 | DL 模型 + 技術指標 |
| `run_backtest` | 量化回測 | 執行回測並返回結果 |
| `create_chart` | 圖表生成 | 生成價格走勢圖、K線圖 |

## 📖 文檔

- **[QUICK_GUIDE.md](QUICK_GUIDE.md)** - 快速使用指南
- **[FINAL_COMPLETION.md](FINAL_COMPLETION.md)** - 完整項目報告
- **[OPTION2_COMPLETE.md](OPTION2_COMPLETE.md)** - Option 2 優化報告
- **[COMBINED_STRATEGY_OPTIMIZED.md](COMBINED_STRATEGY_OPTIMIZED.md)** - 綜合策略優化

## 🧪 測試

```bash
# 測試所有工具
python test_tools.py

# 測試時間對齊
python test_alignment.py

# 測試系統
python test_system.py

# Web 回測測試
./test_web_backtest.sh
```

## 💡 使用建議

### 回測建議
1. 先用短期數據（7天）測試
2. 再用長期數據（30-90天）驗證
3. 對比三種策略的結果
4. 注意最大回撤和勝率

### 策略選擇
- **長期投資** → 技術分析策略
- **穩健投資** → 綜合策略（推薦）
- **短期交易** → 根據市場狀況選擇

### 性能優化
- 使用 GPU 加速情感分析
- 較長時間範圍獲得更好結果
- 定期更新新聞數據

## ⚠️ 風險提示

- 回測結果不等於實盤表現
- 加密貨幣市場波動大，注意風險
- 建議從小資金開始測試
- 做好風險管理和止損

## 🎓 參考資料

### 論文
- FinBERT: Financial Sentiment Analysis with Pre-trained Language Models
- Attention Is All You Need (Transformer)
- LSTM: Long Short-Term Memory Networks

### 數據集
- [CryptoNews Dataset](https://github.com/soheilrahsaz/cryptoNewsDataset)

### 工具
- [Ollama](https://ollama.ai)
- [Backtrader](https://www.backtrader.com)
- [CCXT](https://github.com/ccxt/ccxt)

## 📝 更新日誌

### v1.0.0 (2025-12-16)
- ✅ 完整的 MCP 工具系統
- ✅ 三種量化回測策略
- ✅ 時間對齊系統
- ✅ 綜合策略優化
- ✅ Web 界面完善
- ✅ 碎股交易支援

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 📧 聯繫

如有問題，請查看文檔或提交 Issue。

---

**⭐ 如果這個項目對你有幫助，請給個 Star！**

**🚀 系統已可投入使用！**
