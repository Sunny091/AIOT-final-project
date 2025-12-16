# 依賴安裝指南

## 快速安裝

### 最小化安裝（核心功能）
```bash
pip install flask flask-cors flask-socketio requests python-socketio
pip install ccxt pandas numpy transformers torch
pip install beautifulsoup4 feedparser python-dotenv
pip install backtrader pandas-ta ta scikit-learn sentencepiece
```

### 完整安裝
```bash
pip install -r requirements.txt
```

## 常見問題

### 1. ccxt 版本問題

**錯誤**: `ERROR: No matching distribution found for ccxt==4.2.0`

**解決方案**:
```bash
# 安裝最新版本
pip install ccxt

# 或指定範圍
pip install "ccxt>=4.2.0"
```

### 2. torch 安裝緩慢

**原因**: PyTorch 體積較大（~2GB）

**解決方案**:
```bash
# CPU 版本（較小）
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 或使用清華鏡像
pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. TA-Lib 編譯錯誤

**錯誤**: `error: command 'gcc' failed`

**解決方案**: 使用 pandas-ta 替代
```bash
pip install pandas-ta
# 無需安裝 TA-Lib
```

### 4. vectorbt 依賴過多

**說明**: vectorbt 是可選的高級回測庫

**解決方案**:
```bash
# 僅安裝核心功能（不包含 vectorbt）
pip install -r requirements.txt --no-deps
pip install flask flask-cors flask-socketio ccxt pandas torch transformers
```

## 平台特定說明

### Linux / macOS
```bash
# 1. 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 2. 升級 pip
pip install --upgrade pip

# 3. 安裝依賴
pip install -r requirements.txt
```

### Windows
```bash
# 1. 創建虛擬環境
python -m venv venv
venv\Scripts\activate

# 2. 升級 pip
python -m pip install --upgrade pip

# 3. 安裝依賴
pip install -r requirements.txt
```

### Google Colab
```python
!pip install -q -r requirements.txt
```

## 使用國內鏡像（加速）

### 清華源
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 阿里雲源
```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 永久配置
```bash
# Linux/macOS
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# Windows
# 創建 %APPDATA%\pip\pip.ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
```

## 依賴說明

### 核心依賴（必需）
| 套件 | 版本 | 用途 |
|------|------|------|
| Flask | 3.0.0 | Web 框架 |
| ccxt | >=4.2.0 | 交易所 API |
| pandas | >=2.0.0 | 數據處理 |
| torch | >=2.0.0 | 深度學習 |
| transformers | >=4.30.0 | FinBERT |
| backtrader | >=1.9.78 | 回測引擎 |

### 可選依賴
| 套件 | 用途 | 替代方案 |
|------|------|----------|
| vectorbt | 高級回測 | backtrader |
| mplfinance | 圖表繪製 | Chart.js (前端) |
| redis | 緩存 | 內存緩存 |
| TA-Lib | 技術指標 | pandas-ta |

## 驗證安裝

### 快速驗證
```bash
python -c "
import flask
import ccxt
import pandas
import torch
import transformers
import backtrader
print('✅ 所有核心依賴已安裝')
"
```

### 詳細驗證
```bash
python test_demo.py
```

## 最小化配置（低資源環境）

### requirements-minimal.txt
```
flask==3.0.0
flask-cors==4.0.0
ccxt>=4.2.0
pandas>=2.0.0
numpy>=1.24.0
transformers>=4.30.0
torch>=2.0.0
backtrader>=1.9.78
feedparser>=6.0.0
python-dotenv>=1.0.0
```

安裝：
```bash
pip install -r requirements-minimal.txt
```

## Docker 安裝

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

構建和運行：
```bash
docker build -t mcp-crypto .
docker run -p 11403:11403 mcp-crypto
```

## 故障排除

### 1. 內存不足
```bash
# 減少並行下載
pip install --no-cache-dir -r requirements.txt

# 逐個安裝大型套件
pip install torch
pip install transformers
pip install -r requirements.txt
```

### 2. 網路超時
```bash
# 增加超時時間
pip install --timeout=300 -r requirements.txt

# 使用本地緩存
pip install --cache-dir=/tmp/pip-cache -r requirements.txt
```

### 3. 權限錯誤
```bash
# 用戶安裝
pip install --user -r requirements.txt

# 虛擬環境（推薦）
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 更新依賴

### 檢查過時套件
```bash
pip list --outdated
```

### 更新所有套件
```bash
pip install --upgrade -r requirements.txt
```

### 生成當前環境
```bash
pip freeze > requirements-freeze.txt
```

## 支援

遇到問題？
1. 檢查 Python 版本：`python --version` (需要 3.8+)
2. 更新 pip：`pip install --upgrade pip`
3. 查看錯誤日誌
4. 參考本文檔的常見問題

---

**推薦 Python 版本**: 3.9, 3.10, 3.11
**最低 Python 版本**: 3.8
**測試環境**: Ubuntu 20.04, macOS 13, Windows 11
