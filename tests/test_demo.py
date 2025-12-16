"""
Demo script to test the MCP system components
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models.ollama_client import OllamaClient
from backend.mcp_tools.crypto_tools import CryptoDataTool, CryptoNewsTool
from backend.mcp_orchestrator import MCPOrchestrator

def test_ollama_connection():
    """Test Ollama API connection"""
    print("=" * 60)
    print("測試 1: Ollama API 連接")
    print("=" * 60)
    
    try:
        client = OllamaClient()
        response = client.chat("你好，請簡單介紹你自己", temperature=0.7)
        print(f"✅ Ollama 連接成功")
        print(f"回應: {response[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Ollama 連接失敗: {e}")
        return False

def test_crypto_data():
    """Test crypto data fetching"""
    print("\n" + "=" * 60)
    print("測試 2: 加密貨幣數據獲取")
    print("=" * 60)
    
    try:
        tool = CryptoDataTool()
        result = tool.get_current_price('BTC/USDT')
        
        if result.get('success'):
            print(f"✅ 數據獲取成功")
            print(f"   交易對: {result['symbol']}")
            print(f"   價格: ${result['price']:,.2f}")
            print(f"   24h 漲跌: {result['change_24h']:.2f}%")
            return True
        else:
            print(f"❌ 數據獲取失敗: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_news_fetching():
    """Test news fetching"""
    print("\n" + "=" * 60)
    print("測試 3: 新聞獲取")
    print("=" * 60)
    
    try:
        tool = CryptoNewsTool()
        result = tool.fetch_news('BTC', limit=3)
        
        if result.get('success'):
            print(f"✅ 新聞獲取成功")
            print(f"   獲取文章數: {result['count']}")
            for i, article in enumerate(result['articles'][:2], 1):
                print(f"   {i}. {article['title'][:60]}...")
            return True
        else:
            print(f"❌ 新聞獲取失敗: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_mcp_orchestrator():
    """Test MCP orchestrator"""
    print("\n" + "=" * 60)
    print("測試 4: MCP 協調器（需要 Ollama API Key）")
    print("=" * 60)
    
    try:
        orchestrator = MCPOrchestrator()
        
        # Test with a simple query
        print("發送查詢: '查詢 BTC 的價格'")
        response = orchestrator.process_user_message("查詢 BTC 的價格")
        
        if response.get('success'):
            print(f"✅ MCP 協調器工作正常")
            print(f"   使用工具: {response.get('tool_used', 'N/A')}")
            print(f"   響應: {response.get('message', '')[:100]}...")
            return True
        else:
            print(f"❌ MCP 協調器失敗: {response.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 MCP 加密貨幣交易系統 - 組件測試")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Ollama API", test_ollama_connection()))
    results.append(("加密貨幣數據", test_crypto_data()))
    results.append(("新聞獲取", test_news_fetching()))
    results.append(("MCP 協調器", test_mcp_orchestrator()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 測試總結")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{name:20s}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("\n🎉 所有測試通過！系統已準備就緒。")
    else:
        print("\n⚠️  部分測試失敗，請檢查配置和網絡連接。")
    
    print("\n💡 提示:")
    print("   - 確保已設置 OLLAMA_API_KEY 在 .env 文件中")
    print("   - 確保網絡連接正常")
    print("   - 運行 'python app.py' 啟動 Web 介面")

if __name__ == '__main__':
    main()
