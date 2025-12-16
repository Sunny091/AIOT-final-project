#!/usr/bin/env python3
"""
測試所有必需的依賴是否已正確安裝
"""
import sys

def test_dependencies():
    """測試所有核心依賴"""
    print("=" * 60)
    print("檢查系統依賴")
    print("=" * 60)
    
    # Python version
    print(f"\nPython 版本: {sys.version}")
    py_ver = sys.version_info
    if py_ver < (3, 8):
        print("❌ Python 版本過低，需要 3.8+")
        return False
    else:
        print("✅ Python 版本符合要求")
    
    # Required packages
    required_packages = {
        'flask': 'Web 框架',
        'flask_cors': 'CORS 支援',
        'flask_socketio': 'WebSocket 支援',
        'requests': 'HTTP 請求',
        'pandas': '數據處理',
        'numpy': '數值計算',
        'ccxt': '交易所 API',
        'torch': '深度學習',
        'transformers': 'FinBERT 模型',
        'backtrader': '回測引擎',
        'feedparser': 'RSS 解析',
        'bs4': '網頁解析',
    }
    
    print(f"\n檢查必需套件:")
    print("-" * 60)
    
    failed = []
    for package, description in required_packages.items():
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✅ {package:20s} {version:15s} ({description})")
        except ImportError as e:
            print(f"❌ {package:20s} 未安裝       ({description})")
            failed.append(package)
    
    # Optional packages
    optional_packages = {
        'pandas_ta': '技術分析',
        'ta': '技術指標',
        'yfinance': '金融數據',
        'sentencepiece': 'FinBERT Tokenizer',
        'sklearn': '機器學習',
    }
    
    print(f"\n檢查可選套件:")
    print("-" * 60)
    
    for package, description in optional_packages.items():
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✅ {package:20s} {version:15s} ({description})")
        except ImportError:
            print(f"⚠️  {package:20s} 未安裝       ({description})")
    
    # Summary
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)
    
    if failed:
        print(f"❌ {len(failed)} 個必需套件未安裝:")
        for pkg in failed:
            print(f"   - {pkg}")
        print(f"\n請運行: pip install {' '.join(failed)}")
        return False
    else:
        print("✅ 所有必需套件已安裝!")
        print("\n系統已準備就緒，可以運行:")
        print("   python app.py")
        return True

if __name__ == '__main__':
    success = test_dependencies()
    sys.exit(0 if success else 1)
