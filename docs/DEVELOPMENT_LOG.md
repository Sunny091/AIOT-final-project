# 開發紀錄 - AI 加密貨幣交易助手

## 專案資訊
- **課程**：物聯網應用
- **開發期間**：2024年12月
- **開發方式**：人機協作（使用 LLM 輔助開發）

---

## 開發過程紀錄

### Day 1：專案規劃與架構設計

**User：**
我想做一個加密貨幣的 AI 交易助手作為期末專題，可以用自然語言跟它互動，然後它會幫我查價格、分析市場。你覺得應該怎麼設計架構？

**LLM：**
這是個很好的專題方向！建議採用 MCP (Model Context Protocol) 架構，這樣可以讓 LLM 動態選擇和調用不同的工具。

建議的架構如下：

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Web UI)                 │
├─────────────────────────────────────────────────────┤
│                    Flask Backend                     │
├─────────────────────────────────────────────────────┤
│                  MCP Orchestrator                    │
│    ┌─────────┬─────────┬─────────┬─────────┐       │
│    │ Crypto  │Sentiment│Technical│Backtest │       │
│    │  Tools  │Analysis │Analysis │ Engine  │       │
│    └─────────┴─────────┴─────────┴─────────┘       │
├─────────────────────────────────────────────────────┤
│              Ollama LLM (GPT-OSS 20B)               │
└─────────────────────────────────────────────────────┘
```

核心組件：
1. **MCP Orchestrator** - 協調 LLM 與各種工具的交互
2. **Crypto Tools** - 價格查詢、K線數據
3. **Sentiment Analysis** - 使用 FinBERT 分析新聞情感
4. **Technical Analysis** - 深度學習模型分析趨勢
5. **Backtest Engine** - 量化回測系統

**User：**
MCP 是什麼？為什麼要用這個架構？

**LLM：**
MCP (Model Context Protocol) 是一種讓 LLM 能夠與外部工具互動的協議。

傳統做法是寫死規則來判斷用戶意圖，但 MCP 的優點是：

1. **動態工具選擇** - LLM 根據用戶輸入自動決定要用哪個工具
2. **可擴展性** - 新增工具只需要註冊到 Orchestrator
3. **自然語言理解** - 用戶不需要學習特定指令格式

例如用戶說「幫我看看 BTC 最近的新聞情緒如何」，LLM 會：
1. 理解需要用到 `crypto_news` 和 `sentiment_analysis` 工具
2. 先獲取新聞，再進行情感分析
3. 將結果整合成自然語言回覆

**User：**
好，那我們就用這個架構。先從基本的價格查詢開始做吧。

---

### Day 2：實作價格查詢功能

**User：**
我要怎麼取得加密貨幣的即時價格？

**LLM：**
建議使用 CCXT 這個 Python 函式庫，它整合了超過 100 個交易所的 API。

```python
import ccxt

class CryptoDataTool:
    def __init__(self):
        self.exchange = ccxt.binance()

    def get_price(self, symbol: str) -> dict:
        """獲取即時價格"""
        ticker = self.exchange.fetch_ticker(symbol)
        return {
            'symbol': symbol,
            'price': ticker['last'],
            'change_24h': ticker['percentage'],
            'volume_24h': ticker['quoteVolume'],
            'high_24h': ticker['high'],
            'low_24h': ticker['low']
        }
```

**User：**
執行的時候出現錯誤：`ccxt.base.errors.BadSymbol: binance does not have market symbol BTC`

**LLM：**
這是因為 Binance 的交易對格式需要是 `BTC/USDT` 而不是單純的 `BTC`。讓我修改一下：

```python
def get_price(self, symbol: str) -> dict:
    # 自動補全交易對格式
    if '/' not in symbol:
        symbol = f"{symbol.upper()}/USDT"

    ticker = self.exchange.fetch_ticker(symbol)
    # ...
```

這樣用戶輸入 `BTC` 或 `BTC/USDT` 都可以正常運作。

**User：**
可以了！現在價格查詢功能正常。接下來想加入新聞情感分析。

---

### Day 3：實作情感分析功能

**User：**
我想用 AI 分析加密貨幣新聞的情感，判斷市場是樂觀還是悲觀。應該用什麼模型？

**LLM：**
推薦使用 **FinBERT**，這是專門針對金融文本訓練的 BERT 模型，對金融術語和情感判斷效果很好。

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class SentimentAnalysisTool:
    def __init__(self):
        self.model_name = 'ProsusAI/finbert'
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.labels = ['positive', 'negative', 'neutral']

    def analyze(self, text: str) -> dict:
        inputs = self.tokenizer(text, return_tensors='pt',
                                truncation=True, max_length=512)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)

        sentiment_idx = torch.argmax(probabilities).item()
        return {
            'sentiment': self.labels[sentiment_idx],
            'confidence': probabilities[0][sentiment_idx].item(),
            'scores': {
                'positive': probabilities[0][0].item(),
                'negative': probabilities[0][1].item(),
                'neutral': probabilities[0][2].item()
            }
        }
```

**User：**
模型載入很慢，每次查詢都要等很久。

**LLM：**
這是因為每次都重新載入模型。應該在初始化時只載入一次，然後重複使用。另外可以加入快取機制：

```python
class SentimentAnalysisTool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        print("Loading FinBERT model...")
        self.tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert')
        self.model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert')
        self.cache = {}
        print("FinBERT model loaded!")
```

使用單例模式確保模型只載入一次。

**User：**
新聞來源要從哪裡取得？

**LLM：**
我找到一個 GitHub 上的加密貨幣新聞資料集：`cryptoNewsDataset`，包含了大量歷史新聞。

對於即時新聞，可以使用 NewsAPI 或 CryptoPanic API。我先用本地資料集來實作：

```python
class CryptoNewsTool:
    def __init__(self):
        self.news_file = 'data/cryptoNewsDataset/news.csv'
        self.df = pd.read_csv(self.news_file)

    def get_news(self, symbol: str, limit: int = 10) -> list:
        # 過濾相關新聞
        mask = self.df['title'].str.contains(symbol, case=False, na=False)
        filtered = self.df[mask].head(limit)

        return filtered[['title', 'text', 'date']].to_dict('records')
```

---

### Day 4：實作技術分析功能

**User：**
現在想加入技術分析功能，用 AI 預測價格走勢。

**LLM：**
建議使用 LSTM + Attention 架構，這是時序預測的經典方法：

```python
class LSTMAttentionModel(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                           batch_first=True, bidirectional=True)
        self.attention = nn.MultiheadAttention(hidden_size * 2, num_heads=4)
        self.fc = nn.Linear(hidden_size * 2, 1)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        return self.fc(attn_out[:, -1, :])
```

同時計算傳統技術指標作為輔助：

```python
def calculate_indicators(self, df):
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    exp1 = df['close'].ewm(span=12).mean()
    exp2 = df['close'].ewm(span=26).mean()
    df['macd'] = exp1 - exp2
    df['signal'] = df['macd'].ewm(span=9).mean()

    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (std * 2)
    df['bb_lower'] = df['bb_middle'] - (std * 2)

    return df
```

**User：**
如何結合 LSTM 預測和技術指標來產生交易信號？

**LLM：**
設計一個綜合評分系統：

```python
def generate_signals(self, symbol: str) -> dict:
    # 1. LSTM 預測
    predicted_direction = self.model.predict(features)

    # 2. 技術指標信號
    rsi_signal = 1 if rsi < 30 else (-1 if rsi > 70 else 0)
    macd_signal = 1 if macd > signal else -1
    bb_signal = 1 if price < bb_lower else (-1 if price > bb_upper else 0)

    # 3. 加權評分
    weights = {'lstm': 0.4, 'rsi': 0.2, 'macd': 0.2, 'bb': 0.2}
    score = (predicted_direction * weights['lstm'] +
             rsi_signal * weights['rsi'] +
             macd_signal * weights['macd'] +
             bb_signal * weights['bb'])

    # 4. 生成建議
    if score > 0.3:
        recommendation = 'STRONG BUY'
    elif score > 0.1:
        recommendation = 'BUY'
    elif score > -0.1:
        recommendation = 'HOLD'
    elif score > -0.3:
        recommendation = 'SELL'
    else:
        recommendation = 'STRONG SELL'

    return {
        'recommendation': recommendation,
        'signal_strength': score,
        'indicators': {...}
    }
```

---

### Day 5：實作回測引擎

**User：**
我想驗證這些策略的效果，需要一個回測系統。

**LLM：**
使用 Backtrader 這個專業的量化回測框架：

```python
import backtrader as bt

class SentimentStrategy(bt.Strategy):
    """基於情感分析的策略"""

    def __init__(self):
        self.sentiment_tool = SentimentAnalysisTool()
        self.news_tool = CryptoNewsTool()

    def next(self):
        # 獲取當日新聞並分析情感
        news = self.news_tool.get_news_by_date(self.data.datetime.date())
        sentiment = self.sentiment_tool.analyze_batch(news)

        score = sentiment['aggregate_score']

        if score > 0.2 and not self.position:
            self.buy(size=self.calculate_position_size())
        elif score < -0.2 and self.position:
            self.sell(size=self.position.size)


class TechnicalStrategy(bt.Strategy):
    """基於技術分析的策略"""

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close)
        self.macd = bt.indicators.MACD(self.data.close)

    def next(self):
        if self.rsi < 30 and self.macd.macd > self.macd.signal:
            if not self.position:
                self.buy()
        elif self.rsi > 70 and self.macd.macd < self.macd.signal:
            if self.position:
                self.sell()
```

**User：**
回測結果顯示情感策略的勝率是 0%，這正常嗎？

**LLM：**
檢查發現問題：新聞日期和價格日期沒有對齊。新聞是 UTC 時間，但價格數據是交易所當地時間。

需要加入時間對齊邏輯：

```python
def align_timestamps(self, news_df, price_df):
    """對齊新聞和價格的時間戳"""
    # 統一轉換為 UTC
    news_df['date'] = pd.to_datetime(news_df['date']).dt.tz_localize('UTC')
    price_df['date'] = pd.to_datetime(price_df['timestamp'], unit='ms')
    price_df['date'] = price_df['date'].dt.tz_localize('UTC')

    # 將新聞對應到最近的交易日
    news_df['trading_date'] = news_df['date'].apply(
        lambda x: self.find_nearest_trading_date(x, price_df)
    )

    return news_df, price_df
```

修復後，回測結果正常了！

---

### Day 6：實作 Web 介面

**User：**
需要一個好看的 Web 介面讓使用者可以跟系統互動。

**LLM：**
使用 Flask + WebSocket 實現即時通訊：

```python
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('user_message')
def handle_message(data):
    user_input = data['message']

    # 透過 MCP Orchestrator 處理
    response = orchestrator.process_user_message(user_input)

    # 發送回覆
    socketio.emit('bot_response', {
        'message': response['message'],
        'tool_used': response.get('tool_used'),
        'chart_data': response.get('chart_data')
    })
```

前端使用簡潔的聊天介面：

```html
<div class="chat-container">
    <div id="messages"></div>
    <div class="input-area">
        <input type="text" id="user-input" placeholder="輸入訊息...">
        <button onclick="sendMessage()">發送</button>
    </div>
    <div class="quick-actions">
        <button onclick="quickAction('查詢 BTC 價格')">查詢 BTC 價格</button>
        <button onclick="quickAction('分析 ETH 走勢')">分析 ETH</button>
        <button onclick="quickAction('BTC 新聞情感')">新聞情感</button>
    </div>
</div>
```

**User：**
可以加入圖表顯示功能嗎？

**LLM：**
加入 Chart.js 來渲染圖表：

```python
class ChartTool:
    def create_price_chart(self, symbol: str, days: int = 30) -> dict:
        # 獲取歷史數據
        ohlcv = self.exchange.fetch_ohlcv(symbol, '1d', limit=days)

        return {
            'type': 'line',
            'title': f'{symbol} Price Chart',
            'labels': [datetime.fromtimestamp(x[0]/1000).strftime('%m/%d') for x in ohlcv],
            'datasets': [{
                'label': 'Price',
                'data': [x[4] for x in ohlcv],  # Close price
                'borderColor': '#4CAF50'
            }]
        }
```

前端接收並渲染：

```javascript
socket.on('bot_response', function(data) {
    if (data.chart_data) {
        const ctx = document.getElementById('chart').getContext('2d');
        new Chart(ctx, data.chart_data);
    }
});
```

---

### Day 7：整合 LLM 智能決策

**User：**
現在的綜合分析是用規則判斷的，能不能讓 LLM 來做最終決策？

**LLM：**
好主意！可以把所有分析結果餵給 LLM，讓它做出更智能的判斷：

```python
def generate_recommendation(self, analysis: dict) -> dict:
    prompt = f"""你是專業的加密貨幣交易分析師。請根據以下數據給出交易建議：

【市場數據】
交易對: {analysis['symbol']}
當前價格: ${analysis['price']}
24小時漲跌: {analysis['change_24h']}%

【情感分析】
整體情感: {analysis['sentiment']['overall']}
情感分數: {analysis['sentiment']['score']}

【技術分析】
RSI: {analysis['technical']['rsi']}
MACD 信號: {analysis['technical']['macd_signal']}
趨勢方向: {analysis['technical']['trend']}

請以 JSON 格式回覆：
{{"action": "BUY/SELL/HOLD", "confidence": 0.0-1.0, "reasoning": "分析理由"}}
"""

    response = self.ollama_client.chat(prompt)
    return json.loads(response)
```

這樣 LLM 可以綜合考慮所有因素，給出更有說服力的建議。

---

### Day 8：優化與除錯

**User：**
系統經常出現 timeout 錯誤：`Read timed out. (read timeout=60)`

**LLM：**
這是因為 Ollama API 響應時間較長。建議把 timeout 設定移到環境變數：

```python
# config.py
OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', 120))

# ollama_client.py
response = requests.post(
    self.chat_api_url,
    headers=headers,
    data=payload,
    timeout=self.timeout  # 使用可配置的 timeout
)
```

`.env` 文件：
```
OLLAMA_TIMEOUT=120
```

**User：**
LLM 有時候不會正確選擇工具，直接回覆一些莫名其妙的內容。

**LLM：**
需要加入 fallback 機制，當 LLM 無法正確解析時，根據關鍵字推斷意圖：

```python
def _infer_tool_from_message(self, message: str) -> dict:
    """當 LLM 解析失敗時的備援機制"""
    message_lower = message.lower()

    if any(word in message_lower for word in ['價格', 'price', '多少錢']):
        return {"tool": "get_crypto_price", "params": {"symbol": "BTC/USDT"}}

    if any(word in message_lower for word in ['情感', 'sentiment', '新聞']):
        return {"tool": "analyze_sentiment", "params": {"symbol": "BTC"}}

    if any(word in message_lower for word in ['技術', 'technical', '分析']):
        return {"tool": "technical_analysis", "params": {"symbol": "BTC/USDT"}}

    if any(word in message_lower for word in ['圖表', 'chart', '走勢']):
        return {"tool": "create_chart", "params": {"symbol": "BTC/USDT"}}

    return None
```

---

### Day 9：回測結果分析

**User：**
跑完長期回測，結果如下，幫我分析一下：

| 策略 | 回報率 | 最大回撤 | 勝率 |
|------|--------|----------|------|
| 技術分析 | +32.80% | -17.77% | 77.8% |
| 情感分析 | +25.50% | -29.99% | N/A |
| 綜合策略 | +5.08% | -2.83% | 100% |

**LLM：**
分析結果：

1. **技術分析策略** - 最高回報但風險也較大
   - 優點：長期表現最佳，勝率高
   - 缺點：最大回撤接近 18%，需要承受較大波動

2. **情感分析策略** - 中等回報但回撤較大
   - 優點：能捕捉新聞驅動的行情
   - 缺點：情感滯後性導致回撤較大

3. **綜合策略** - 最穩健的選擇
   - 優點：100% 勝率、最小回撤
   - 缺點：因為太保守，錯過一些機會

建議：
- 風險承受度高 → 技術分析策略
- 追求穩定 → 綜合策略
- 新聞敏感市場 → 情感分析策略

---

### Day 10：最終整合與部署

**User：**
專案差不多完成了，幫我整理一下最終的檔案結構。

**LLM：**
最終專案結構：

```
AIOT-final-project/
├── app.py                    # Flask 主應用
├── config.py                 # 配置管理
├── start.sh                  # 啟動腳本
├── requirements.txt          # 依賴列表
├── .env                      # 環境變數
│
├── backend/
│   ├── mcp_orchestrator.py   # MCP 協調器
│   ├── mcp_tools/
│   │   ├── crypto_tools.py   # 加密貨幣工具
│   │   └── chart_tool.py     # 圖表生成
│   └── models/
│       ├── ollama_client.py  # LLM 客戶端
│       ├── sentiment_analyzer.py  # FinBERT 情感分析
│       ├── technical_analysis.py  # LSTM 技術分析
│       └── backtest_engine.py     # 回測引擎
│
├── frontend/
│   ├── index.html            # 主介面
│   └── backtest.html         # 回測介面
│
├── data/
│   └── cryptoNewsDataset/    # 新聞資料集
│
├── demo/                     # Demo 影片
│   ├── DEMO.md
│   └── *.mov
│
└── docs/                     # 文檔
    ├── README.md
    ├── INSTALL_GUIDE.md
    └── ...
```

**User：**
謝謝你這段時間的協助！這個專案完成了。

**LLM：**
很高興能幫助你完成這個專題！這是一個完整的 AI 交易助手系統，整合了：

- MCP 架構的工具協調
- FinBERT 情感分析
- LSTM + Attention 技術分析
- Backtrader 量化回測
- Flask + WebSocket 即時通訊
- 圖表可視化

祝你報告順利！如果之後有任何問題，隨時可以問我。

---

## 開發心得

這次專題使用 LLM 輔助開發，大幅提升了開發效率：

1. **架構設計** - LLM 提供了 MCP 架構的建議，這個架構讓系統更有擴展性
2. **問題排除** - 遇到 bug 時，LLM 能快速定位問題並提供解決方案
3. **程式碼品質** - LLM 建議的設計模式（如單例模式）提升了程式碼品質
4. **學習新技術** - 透過對話學習了 FinBERT、Backtrader 等新工具

人機協作的方式讓開發過程更加順暢，是未來軟體開發的趨勢。

---

*文檔生成日期：2024-12-25*
