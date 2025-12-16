# 端口配置說明

## 🔌 統一端口：11403

本專案統一使用端口 **11403**，不使用 5000。

## 📋 配置位置

### 1. 環境變量 (.env)
```bash
FLASK_PORT=11403
```

### 2. 默認配置 (config.py)
```python
FLASK_PORT = int(os.getenv('FLASK_PORT', 11403))
```

## 🌐 訪問地址

### 主頁面
```
http://localhost:11403
```

### API 端點
```
http://localhost:11403/api/chat
http://localhost:11403/api/price/{symbol}
http://localhost:11403/api/backtest/run
```

### 回測頁面
```
http://localhost:11403/backtest
```

## 🚀 使用方式

### 本地開發
```bash
# 確認端口配置
cat .env | grep FLASK_PORT

# 啟動服務器
python app.py

# 訪問
open http://localhost:11403
```

### Docker 部署
```bash
# 端口映射
docker run -p 11403:11403 mcp-crypto

# 訪問
curl http://localhost:11403
```

### SSH 端口轉發
```bash
# 遠程服務器轉發
ssh -L 11403:localhost:11403 user@server

# 本地訪問
open http://localhost:11403
```

## 🔥 防火牆配置

### Linux (ufw)
```bash
sudo ufw allow 11403
sudo ufw reload
```

### Linux (firewalld)
```bash
sudo firewall-cmd --add-port=11403/tcp --permanent
sudo firewall-cmd --reload
```

### 檢查端口占用
```bash
# 檢查端口是否被占用
netstat -tlnp | grep 11403
lsof -i :11403

# 查看服務器進程
ps aux | grep app.py
```

## 📊 端口測試

```bash
# 測試連接
curl http://localhost:11403/

# 測試 API
curl -X POST http://localhost:11403/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# 測試響應時間
time curl http://localhost:11403/
```

## ⚠️ 常見問題

### Q: 為什麼不用 5000？
A: 
- 避免與其他 Flask 應用衝突
- 11403 是自定義端口，減少衝突
- 已在 .env 中配置

### Q: 如何修改端口？
A: 修改 `.env` 文件中的 `FLASK_PORT`
```bash
FLASK_PORT=YOUR_PORT
```

### Q: 端口被占用怎麼辦？
A: 
```bash
# 找到占用端口的進程
lsof -i :11403

# 殺掉進程
kill -9 PID

# 或選擇其他端口
```

## 🎯 端口規範

| 服務 | 端口 | 說明 |
|------|------|------|
| Web 服務器 | 11403 | 主應用 |
| Ollama API | 8787 | 外部服務 |
| Redis (可選) | 6379 | 緩存 |

## ✅ 確認配置

```bash
# 檢查所有配置文件
grep -r "FLASK_PORT\|11403" --include="*.py" --include="*.env" .

# 應該看到：
# .env:FLASK_PORT=11403
# config.py:FLASK_PORT = int(os.getenv('FLASK_PORT', 11403))
```

---

**端口**: 11403  
**協議**: HTTP  
**地址**: 0.0.0.0 (所有網路接口)  
**最後更新**: 2024-12-16
