# 訪問指南

## ✅ 服務器已啟動

服務器正在運行在：
- **本地訪問**: http://localhost:11403
- **網路訪問**: http://0.0.0.0:11403
- **容器內部**: http://127.0.0.1:11403

## 🌐 訪問方法

### 方法一：本地訪問（推薦）
如果您在服務器本機：
```
http://localhost:11403
```

### 方法二：遠程訪問
如果您從其他機器訪問，需要使用服務器的 IP 地址：
```
http://YOUR_SERVER_IP:11403
```

### 方法三：SSH 端口轉發
如果您通過 SSH 連接，可以使用端口轉發：
```bash
ssh -L 11403:localhost:11403 user@server
```
然後訪問：http://localhost:11403

## 🔍 檢查服務器狀態

```bash
# 查看服務器是否運行
ps aux | grep "app.py"

# 查看服務器日誌
tail -f /user_data/1141/aiot/final/mcp_system_final/server.log

# 測試連接
curl http://localhost:11403
```

## 📊 當前狀態

✅ 服務器運行中
✅ 端口: 11403
✅ 主機: 0.0.0.0 (所有接口)
✅ 新聞數據: 929,252 篇已載入
✅ Debug 模式: ON

## ⚠️ 常見問題

### Q: 連接被拒絕 (Connection Refused)

**原因**: 
1. 防火牆阻擋
2. 端口未正確綁定
3. 使用錯誤的 IP 地址

**解決**:
```bash
# 檢查端口
netstat -tlnp | grep 11403

# 檢查防火牆 (如果有)
sudo ufw status
sudo ufw allow 11403

# 確認服務器在運行
ps aux | grep app.py
```

### Q: 頁面載入緩慢

**原因**: 服務器正在載入大量新聞數據

**解決**: 等待載入完成（查看日誌）

### Q: 無法從外部訪問

**原因**: 可能在 Docker/容器環境中

**解決**: 
1. 檢查容器端口映射
2. 使用 SSH 端口轉發
3. 配置反向代理

## 🚀 快速啟動

```bash
cd /user_data/1141/aiot/final/mcp_system_final
./start.sh
```

## 📝 API 端點

- `GET  /` - 主頁面（聊天界面）
- `GET  /backtest` - 回測結果頁面
- `POST /api/chat` - 聊天 API
- `POST /api/backtest` - 回測 API

## 💡 提示

如果您在瀏覽器中看到 "連接被拒絕"，請：
1. 確認服務器正在運行
2. 檢查使用的是正確的 IP 和端口
3. 嘗試使用 SSH 端口轉發

---

**服務器地址**: http://0.0.0.0:11403
**狀態**: ✅ 運行中
**新聞數據**: ✅ 已載入 (929,252 篇)
