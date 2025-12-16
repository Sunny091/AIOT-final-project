# 技術分析深度學習方法 (Technical Analysis DL Methods)

## 概述 (Overview)

本系統使用**最先進 (SOTA)** 的深度學習方法進行加密貨幣技術分析和價格預測。

## 使用的深度學習架構

### 1. LSTM with Attention (LSTM + 注意力機制)

**位置**: `backend/models/technical_analysis.py` - `LSTMPricePredictor`

**架構組件**:
- **Bidirectional LSTM**: 3層雙向LSTM，hidden_size=128
- **Multi-head Attention**: 4個注意力頭，提取重要時間步特徵
- **全連接層**: 三層FC網絡進行最終預測
- **Dropout**: 0.2的dropout rate防止過擬合

**優勢**:
- 捕捉時間序列的長期依賴關係
- 注意力機制自動聚焦於重要的價格模式
- 雙向處理增強特徵提取能力

### 2. Transformer (變壓器模型)

**位置**: `backend/models/technical_analysis.py` - `TransformerPricePredictor`

**架構組件**:
- **Input Projection**: 將輸入映射到d_model維度 (128)
- **Positional Encoding**: 添加位置信息到序列
- **Transformer Encoder**: 4層encoder，8個注意力頭
- **前饋網絡**: d_model * 4 的維度擴展
- **輸出層**: 預測未來價格

**優勢**:
- 並行處理序列，訓練速度快
- 自注意力機制捕捉全局依賴關係
- 在長序列上表現優異

## 技術指標特徵工程

系統從OHLCV數據中提取以下特徵:

### 價格特徵
- **Returns**: 收益率
- **Log Returns**: 對數收益率
- **移動平均**: SMA (7, 25, 99), EMA (12, 26)

### 動量指標
- **RSI**: 相對強弱指標 (14週期)
- **Stochastic Oscillator**: 隨機指標 (K, D線)
- **MACD**: 移動平均收斂散度 (12, 26, 9)

### 波動率指標
- **Bollinger Bands**: 布林帶 (20週期, 2標準差)
- **ATR**: 平均真實範圍
- **BB Width**: 布林帶寬度
- **BB Position**: 價格在布林帶中的位置

### 趨勢指標
- **ADX**: 平均趨向指數
- **MACD差值**: MACD線與信號線差

### 成交量指標
- **OBV**: 能量潮指標
- **Volume SMA**: 成交量移動平均
- **Volume Ratio**: 成交量比率

## 預測流程

```python
1. 數據獲取 → OHLCV歷史數據
2. 特徵工程 → 提取30+技術指標
3. 數據標準化 → MinMaxScaler歸一化
4. 序列構建 → 60時間步窗口
5. 模型預測 → Transformer/LSTM推理
6. 信號生成 → 買入/賣出/持有信號
```

## 模型選擇

- **默認**: Transformer (更快、更準確)
- **可選**: LSTM with Attention (更穩定)

切換方法:
```python
# Transformer
engine = TechnicalAnalysisEngine(model_type='transformer')

# LSTM
engine = TechnicalAnalysisEngine(model_type='lstm')
```

## 訓練策略

當前實現使用技術指標組合生成信號。在生產環境中建議:

1. 收集歷史數據 (>1年)
2. 構建訓練/驗證/測試集
3. 使用Adam優化器訓練
4. 使用MSE損失函數
5. Early Stopping防止過擬合
6. 定期重新訓練模型

## 參數配置

```python
# LSTM參數
input_size=10        # 輸入特徵數量
hidden_size=128      # 隱藏層大小
num_layers=3         # LSTM層數
dropout=0.2          # Dropout率

# Transformer參數
d_model=128          # 模型維度
nhead=8              # 注意力頭數
num_layers=4         # Encoder層數
dropout=0.2          # Dropout率

# 通用參數
sequence_length=60   # 序列長度
```

## 性能指標

系統評估指標:
- **預測準確度**: 方向預測正確率
- **RMSE**: 均方根誤差
- **MAE**: 平均絕對誤差
- **信號質量**: 夏普比率、勝率

## SOTA方法選擇理由

1. **Transformer**: 當前時間序列預測的SOTA方法，廣泛應用於金融預測
2. **Attention機制**: 自動識別關鍵價格模式
3. **技術指標**: 結合傳統技術分析與深度學習
4. **端到端**: 從原始數據到交易信號的完整pipeline

## 參考文獻

- Vaswani et al. "Attention Is All You Need" (2017)
- Hochreiter & Schmidhuber. "Long Short-Term Memory" (1997)
- Bahdanau et al. "Neural Machine Translation by Jointly Learning to Align and Translate" (2014)
