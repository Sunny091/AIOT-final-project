# MCP 加密貨幣交易系統 - 文檔中心

## 📖 文檔列表

### 新手入門
1. [安裝指南](INSTALL_GUIDE.md)
   - 系統要求
   - 依賴安裝
   - 常見問題排除
   - 平台特定說明

2. [使用指南](USAGE_GUIDE.md)
   - 快速開始
   - 基本操作
   - 高級功能
   - 示例和教程

3. [訪問指南](ACCESS_GUIDE.md)
   - 服務器訪問方法
   - 端口配置
   - SSH 端口轉發
   - 故障排除

4. [端口配置](PORT_CONFIG.md)
   - 統一端口：11403
   - 端口修改方法
   - 防火牆配置
   - 測試和驗證

### 功能文檔
5. [功能說明](FEATURES.md)
   - 完整功能列表
   - 使用場景
   - API 說明
   - 配置選項

### 技術文檔
6. [架構設計](architecture.md)
   - 系統架構
   - 模塊說明
   - MCP 工具集
   - 數據流程

7. [新聞數據集](NEWS_DATASET_README.md)
   - 數據集介紹
   - 安裝和解壓
   - 使用方法
   - API 文檔

## 🔗 快速鏈接

### 常見問題
- [依賴安裝失敗](INSTALL_GUIDE.md#常見問題)
- [無法訪問服務器](ACCESS_GUIDE.md#常見問題)
- [新聞數據集解壓](NEWS_DATASET_README.md#解壓數據集)

### 快速命令
```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動服務器
./start.sh

# 驗證安裝
python check_dependencies.py

# 驗證數據集
python verify_news_dataset.py
```

## 📊 文檔結構

```
docs/
├── README.md                    # 本文件（文檔索引）
├── INSTALL_GUIDE.md            # 安裝指南
├── USAGE_GUIDE.md              # 使用指南
├── ACCESS_GUIDE.md             # 訪問指南
├── PORT_CONFIG.md              # 端口配置（統一使用 11403）
├── FEATURES.md                 # 功能說明
├── architecture.md             # 架構設計
└── NEWS_DATASET_README.md      # 新聞數據集
```

## 🌐 訪問地址

**主應用**: http://localhost:11403  
**API**: http://localhost:11403/api/chat  
**回測**: http://localhost:11403/backtest

## 🆘 需要幫助？

1. 查看對應的文檔章節
2. 檢查 [主 README](../README.md)
3. 查看服務器日誌：`tail -f server.log`
4. 運行驗證腳本

## 📝 文檔維護

- 最後更新：2024-12-16
- 版本：2.0
- 維護者：MCP Team

---

**返回 [主頁](../README.md)**
