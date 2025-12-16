# 圖表功能更新總結 📊

## 更新日期
2024-12-16

## 新增功能

### 1. 圖表工具（Chart Tool）

新增 `ChartTool` 類，提供時間序列數據的視覺化功能。

**文件位置：** `backend/mcp_tools/chart_tool.py`

**主要功能：**
- 價格走勢圖（折線圖）
- K線圖（蠟燭圖）
- 自定義數據圖表
- 多幣種對比圖（未來擴展）

**支援的時間週期：**
- 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w

### 2. MCP 整合

將 Chart Tool 整合到 MCP Orchestrator 中。

**修改文件：** `backend/mcp_orchestrator.py`

**變更內容：**
- 添加 `ChartTool` 實例到 `self.tools`
- 新增 `create_chart` 工具定義
- 實現 `create_chart` 工具執行邏輯
- 添加圖表結果格式化

### 3. 前端界面更新

**修改文件：**
- `frontend/templates/index.html`
- `frontend/static/js/main.js`
- `frontend/static/css/style.css`

**新增元素：**
- 圖表顯示容器 (`#chartContainer`)
- Plotly.js 庫引入
- 快速按鈕：「價格走勢圖」
- 圖表渲染函數 `displayChart()`

**樣式更新：**
- 圖表容器樣式
- 響應式佈局
- 深色主題適配

### 4. 依賴更新

**文件：** `requirements.txt`

**新增依賴：**
```
plotly>=5.18.0
```

### 5. 文檔更新

**更新的文檔：**
- `README.md` - 添加圖表功能說明
- 新增 `docs/CHART_GUIDE.md` - 詳細使用指南

## 使用方式

### 自然語言指令

用戶可以使用以下方式調用圖表功能：

```
"顯示 BTC 過去一週的價格走勢圖"
"繪製 ETH/USDT 的K線圖"
"顯示 BTC 從 2024-12-01 到 2024-12-15 的價格變化"
```

### 快速按鈕

在聊天界面點擊「📊 價格走勢圖」按鈕可快速生成 BTC 價格圖表。

### API 調用

```python
from backend.mcp_tools.chart_tool import ChartTool

tool = ChartTool()

# 價格走勢圖
result = tool.execute({
    'data_source': 'price',
    'symbol': 'BTC/USDT',
    'timeframe': '1h',
    'chart_type': 'line'
})

# K線圖
result = tool.execute({
    'data_source': 'price',
    'symbol': 'ETH/USDT',
    'timeframe': '4h',
    'chart_type': 'candlestick'
})

# 自定義時間範圍
result = tool.execute({
    'data_source': 'price',
    'symbol': 'BTC/USDT',
    'timeframe': '1d',
    'start_date': '2024-12-01',
    'end_date': '2024-12-15'
})
```

## 技術亮點

### 1. 使用 Plotly.js
- 互動式圖表，支援縮放、平移
- 專業的金融圖表展示
- 響應式設計

### 2. 整合 MCP 架構
- 通過自然語言觸發
- LLM 自動識別圖表需求
- 無縫整合到現有工具系統

### 3. 數據來源
- 使用 CCXT 獲取實時和歷史數據
- 支援多個交易所（目前使用 Binance）
- 可擴展到其他數據源

## 測試結果

### 功能測試

✅ **價格走勢圖測試**
- 成功生成 BTC/USDT 1小時圖表
- 數據點：168 個
- 加載時間：< 2 秒

✅ **K線圖測試**
- 成功生成蠟燭圖
- 正確顯示 OHLC 數據

✅ **MCP 整合測試**
- Chart tool 成功註冊
- LLM 能正確識別圖表需求
- 工具執行無錯誤

### 性能測試

- **數據獲取速度：** 1-3 秒（取決於數據點數量）
- **圖表渲染速度：** < 500ms
- **內存使用：** 增加約 20MB（Plotly.js）

## 文件清單

### 新增文件
```
backend/mcp_tools/chart_tool.py          # 圖表工具核心
docs/CHART_GUIDE.md                      # 使用指南
```

### 修改文件
```
backend/mcp_orchestrator.py              # MCP 整合
frontend/templates/index.html            # UI 更新
frontend/static/js/main.js               # 前端邏輯
frontend/static/css/style.css            # 樣式
requirements.txt                          # 依賴
README.md                                 # 文檔
```

## 未來擴展

### 計劃功能

1. **多幣種對比圖**
   - 在同一圖表顯示多個加密貨幣
   - 百分比變化對比

2. **技術指標疊加**
   - 移動平均線（MA, EMA）
   - 布林帶（Bollinger Bands）
   - MACD、RSI 等指標

3. **情感分析圖表**
   - 新聞情感分數隨時間變化
   - 情感與價格的相關性展示

4. **交易信號標記**
   - 在圖表上標記買入/賣出信號
   - 回測結果視覺化

5. **實時更新**
   - WebSocket 實時數據推送
   - 圖表自動刷新

## 相關問題與解決

### Q1: 為什麼選擇 Plotly.js？

**A:** 
- 專業的金融圖表庫
- 支援互動功能
- 良好的文檔和社區支援
- 可以直接在瀏覽器運行，無需後端渲染

### Q2: 數據從哪裡獲取？

**A:** 
- 使用 CCXT 庫從 Binance 獲取
- 支援實時和歷史數據
- 可以輕鬆切換到其他交易所

### Q3: 圖表可以下載嗎？

**A:** 
- Plotly.js 內建下載功能
- 支援 PNG、SVG、CSV 格式
- 可在圖表右上角找到下載按鈕

## 結論

圖表功能的添加大大增強了系統的視覺化能力，使用戶能夠更直觀地查看和分析加密貨幣價格走勢。通過整合到 MCP 架構，用戶可以使用自然語言輕鬆生成各種圖表，提升了系統的易用性和專業性。

## 相關文檔

- [圖表使用指南](CHART_GUIDE.md)
- [項目結構說明](../PROJECT_STRUCTURE.md)
- [README](../README.md)
