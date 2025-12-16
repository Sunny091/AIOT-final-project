# 加密貨幣新聞數據集整合說明

## 數據集來源

本系統使用來自 GitHub 的加密貨幣新聞數據集：
- Repository: https://github.com/soheilrahsaz/cryptoNewsDataset
- 位置: `data/cryptoNewsDataset/`

## 數據集特點

### 優勢
1. **大規模數據**: 包含大量歷史新聞文章
2. **結構化數據**: CSV 格式，易於處理
3. **離線使用**: 無需實時 API 調用
4. **穩定可靠**: 不受網路和 API 限制影響

### 數據結構
數據集通常包含以下欄位（根據實際數據集調整）:
- `title` / `headline`: 新聞標題
- `text` / `content` / `body`: 新聞內容
- `date` / `timestamp`: 發布日期
- `source`: 新聞來源
- `symbol` / `coin`: 相關加密貨幣

## 使用方式

### 1. 自動載入
系統會自動載入 `data/cryptoNewsDataset/` 目錄下的所有 CSV 文件:

```python
from backend.mcp_tools.crypto_tools import CryptoNewsTool

# 初始化時自動載入數據集
news_tool = CryptoNewsTool()

# 獲取特定幣種的新聞
result = news_tool.fetch_news(symbol='BTC', limit=10)
```

### 2. 查詢新聞
系統支援以下符號查詢:
- BTC / Bitcoin
- ETH / Ethereum / Ether
- BNB / Binance
- XRP / Ripple
- ADA / Cardano
- SOL / Solana
- DOT / Polkadot
- DOGE / Dogecoin

### 3. 自動降級
如果數據集未載入或未找到相關新聞，系統會自動降級使用 RSS 源:
- CoinDesk RSS
- CoinTelegraph RSS

## 安裝與配置

### 首次安裝
```bash
cd data
git clone https://github.com/soheilrahsaz/cryptoNewsDataset.git
```

### 解壓數據集（重要！）

數據集文件以 RAR 格式壓縮，需要解壓才能使用。

#### 方法一：使用解壓腳本（推薦）
```bash
python extract_news_dataset.py
```

#### 方法二：手動安裝 unrar 並解壓
```bash
# 安裝 unrar
sudo apt install unrar  # Ubuntu/Debian
brew install unrar      # macOS

# 解壓主文件（包含所有數據）
cd data/cryptoNewsDataset/csvOutput
unrar e news_currencies_source_joinedResult.rar

# 或解壓所有文件
unrar e "*.rar"
```

#### 方法三：使用在線工具
如果無法安裝 unrar，可使用在線解壓工具：
- https://extract.me/
- https://www.online-convert.com/
- https://unrar.online/

下載 `news_currencies_source_joinedResult.rar`，解壓後將 CSV 文件放回 `csvOutput` 目錄。

### 驗證安裝
```bash
python verify_news_dataset.py
```

預期輸出：
```
✅ 數據集目錄存在
✅ 找到 X 個 CSV 文件  
✅ 載入 248,000+ 篇新聞
```

## 數據處理流程

```
1. 初始化 CryptoNewsTool
   ↓
2. 載入 CSV 文件 (遞迴掃描)
   ↓
3. 合併所有數據到 DataFrame
   ↓
4. 根據 symbol 過濾新聞
   ↓
5. 排序 (按日期降序)
   ↓
6. 返回結果 (限制數量)
   ↓
7. 如果無結果 → RSS 降級
```

## 整合 FinBERT 情感分析

新聞獲取後會自動送入 FinBERT 進行情感分析:

```python
# 1. 獲取新聞
news_result = news_tool.fetch_news('BTC', limit=10)

# 2. 情感分析
from backend.models.sentiment_analyzer import SentimentAnalysisTool
sentiment_tool = SentimentAnalysisTool()
sentiment_result = sentiment_tool.execute({
    'articles': news_result['articles']
})

# 3. 獲取整體情緒
overall = sentiment_result['aggregate_sentiment']
print(f"Overall: {overall['overall_sentiment']}")
print(f"Score: {overall['sentiment_score']}")
```

## 性能優化

### 數據緩存
系統在初始化時一次性載入所有數據到內存:
```python
self.news_df = pd.concat(dfs, ignore_index=True)
```

### 快速查詢
使用 pandas 的向量化操作進行快速過濾:
```python
mask = df['title'].str.contains('bitcoin', na=False)
filtered = df[mask]
```

### 內存管理
對於大型數據集，可以考慮:
1. 只載入最近 N 個月的數據
2. 按需載入 (lazy loading)
3. 使用 Dask 處理超大數據集

## 故障排除

### 問題 1: 數據集未載入
```bash
# 檢查目錄
ls -la data/cryptoNewsDataset/

# 檢查 CSV 文件
find data/cryptoNewsDataset -name "*.csv"

# 重新克隆
rm -rf data/cryptoNewsDataset
git clone https://github.com/soheilrahsaz/cryptoNewsDataset.git data/cryptoNewsDataset
```

### 問題 2: CSV 讀取錯誤
可能原因:
- 編碼問題: 嘗試 `encoding='utf-8'` 或 `encoding='latin-1'`
- 分隔符問題: 檢查是否為逗號分隔
- 欄位名稱不匹配: 根據實際數據集調整代碼

### 問題 3: 找不到相關新聞
- 檢查 symbol_map 是否包含該幣種
- 檢查搜索詞是否正確
- 確認數據集中是否包含該幣種的新聞

## 擴展功能

### 添加新幣種
在 `fetch_news` 方法中更新 `symbol_map`:
```python
symbol_map = {
    'BTC': ['bitcoin', 'btc'],
    'NEW_COIN': ['newcoin', 'nc'],  # 添加新幣種
}
```

### 自定義過濾
```python
def fetch_news_custom(self, keywords: List[str], limit: int = 10):
    mask = self.news_df['title'].str.contains('|'.join(keywords))
    return self.news_df[mask].head(limit)
```

### 時間範圍過濾
```python
def fetch_news_by_date(self, symbol: str, start_date: str, end_date: str):
    df = self.news_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    return df[mask]
```

## 數據集統計

系統啟動時會顯示載入的新聞數量:
```
Loaded 50000 news articles from dataset
```

可以通過以下方式查看統計:
```python
print(f"Total articles: {len(news_tool.news_df)}")
print(f"Date range: {news_tool.news_df['date'].min()} to {news_tool.news_df['date'].max()}")
print(f"Coins covered: {news_tool.news_df['symbol'].unique()}")
```

## 與原 RSS 方法對比

| 特性 | 數據集方法 | RSS 方法 |
|------|-----------|----------|
| 數據量 | 大量歷史數據 | 僅最新數據 |
| 穩定性 | 高（離線） | 依賴網路 |
| 速度 | 快（內存） | 慢（網路） |
| 更新頻率 | 需手動更新 | 即時 |
| 適用場景 | 回測、研究 | 實時監控 |

## 最佳實踐

1. **定期更新**: 每週更新一次數據集
2. **數據驗證**: 檢查載入的數據完整性
3. **降級處理**: 保留 RSS 作為後備方案
4. **性能監控**: 監控載入時間和內存使用
5. **日誌記錄**: 記錄數據載入和查詢情況

## 參考資料

- Dataset Repository: https://github.com/soheilrahsaz/cryptoNewsDataset
- FinBERT Paper: https://arxiv.org/abs/1908.10063
- Pandas Documentation: https://pandas.pydata.org/docs/

---

**更新日期**: 2024-12-16
**版本**: 2.0
