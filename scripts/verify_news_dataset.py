#!/usr/bin/env python3
"""
Script to verify and test the crypto news dataset integration
"""
import os
import sys
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_dataset():
    """Check if dataset exists and is valid"""
    dataset_path = 'data/cryptoNewsDataset'
    
    print("=" * 60)
    print("📰 加密貨幣新聞數據集檢查")
    print("=" * 60)
    
    # Check if directory exists
    if not os.path.exists(dataset_path):
        print(f"❌ 數據集目錄不存在: {dataset_path}")
        print("\n💡 請執行以下命令下載數據集:")
        print("   cd data")
        print("   git clone https://github.com/soheilrahsaz/cryptoNewsDataset.git")
        return False
    
    print(f"✅ 數據集目錄存在: {dataset_path}")
    
    # Check for csvOutput directory
    csv_dir = os.path.join(dataset_path, 'csvOutput')
    if not os.path.exists(csv_dir):
        print(f"⚠️  csvOutput 目錄不存在")
        return False
    
    # Find CSV files
    csv_files = []
    for root, dirs, files in os.walk(csv_dir):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    # Find RAR files
    rar_files = [f for f in os.listdir(csv_dir) if f.endswith('.rar')]
    
    if csv_files:
        print(f"✅ 找到 {len(csv_files)} 個 CSV 文件")
    elif rar_files:
        print(f"⚠️  找到 {len(rar_files)} 個 RAR 壓縮文件（需要解壓）")
        print("\n💡 解壓方法:")
        print("   方法 1: 運行解壓腳本")
        print("      python extract_news_dataset.py")
        print("")
        print("   方法 2: 手動安裝 unrar 並解壓")
        print("      sudo apt install unrar  # Ubuntu/Debian")
        print("      cd data/cryptoNewsDataset/csvOutput")
        print("      unrar e news_currencies_source_joinedResult.rar")
        print("")
        print("   方法 3: 使用在線工具解壓")
        print("      - https://extract.me/")
        print("      - https://www.online-convert.com/")
        print("")
        print("⚠️  系統將使用 RSS 降級方案")
        return False
    else:
        print("❌ 未找到 CSV 或 RAR 文件")
        return False
    
    # Load and analyze data
    print("\n📊 載入數據...")
    total_rows = 0
    dfs = []
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            dfs.append(df)
            rows = len(df)
            total_rows += rows
            print(f"   ✓ {os.path.basename(csv_file)}: {rows:,} 篇")
        except Exception as e:
            print(f"   ✗ {os.path.basename(csv_file)}: 錯誤 - {e}")
    
    if not dfs:
        print("❌ 無法載入任何數據文件")
        return False
    
    # Combine all dataframes
    print(f"\n✅ 總共載入: {total_rows:,} 篇新聞")
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Analyze columns
    print(f"\n📋 數據欄位:")
    for i, col in enumerate(combined_df.columns, 1):
        print(f"   {i}. {col}")
    
    # Show sample data
    print(f"\n📄 數據樣本 (前 3 筆):")
    print("-" * 60)
    
    # Display based on available columns
    display_cols = []
    for col in combined_df.columns:
        col_lower = col.lower()
        if any(term in col_lower for term in ['title', 'headline', 'text', 'date', 'time']):
            display_cols.append(col)
    
    if display_cols:
        sample = combined_df[display_cols].head(3)
        for idx, row in sample.iterrows():
            print(f"\n文章 {idx + 1}:")
            for col in display_cols:
                value = str(row[col])
                if len(value) > 100:
                    value = value[:100] + "..."
                print(f"  {col}: {value}")
    else:
        print(combined_df.head(3))
    
    return True


def test_news_tool():
    """Test the CryptoNewsTool with dataset"""
    print("\n" + "=" * 60)
    print("🔧 測試 CryptoNewsTool")
    print("=" * 60)
    
    try:
        from backend.mcp_tools.crypto_tools import CryptoNewsTool
        
        print("初始化 CryptoNewsTool...")
        news_tool = CryptoNewsTool()
        
        # Test fetching news for BTC
        print("\n查詢 BTC 新聞 (limit=5)...")
        result = news_tool.fetch_news('BTC', limit=5)
        
        if result['success']:
            print(f"✅ 成功獲取 {result['count']} 篇新聞")
            print(f"   數據來源: {result['source']}")
            
            print("\n📰 新聞列表:")
            for i, article in enumerate(result['articles'], 1):
                print(f"\n{i}. {article['title'][:80]}")
                if article.get('summary'):
                    print(f"   摘要: {article['summary'][:100]}...")
                if article.get('published'):
                    print(f"   日期: {article['published']}")
            
            return True
        else:
            print(f"❌ 獲取新聞失敗: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  加密貨幣新聞數據集 - 驗證與測試                         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Check dataset
    dataset_ok = check_dataset()
    
    if not dataset_ok:
        print("\n⚠️  數據集檢查未通過")
        print("   系統將使用 RSS 降級方案")
        print()
        return
    
    # Test news tool
    tool_ok = test_news_tool()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 測試總結")
    print("=" * 60)
    print(f"數據集檢查: {'✅ 通過' if dataset_ok else '❌ 失敗'}")
    print(f"工具測試: {'✅ 通過' if tool_ok else '❌ 失敗'}")
    
    if dataset_ok and tool_ok:
        print("\n🎉 所有測試通過！數據集整合成功。")
    elif dataset_ok and not tool_ok:
        print("\n⚠️  數據集存在但工具測試失敗，請檢查代碼。")
    else:
        print("\n💡 請下載數據集以使用完整功能。")
    
    print()


if __name__ == '__main__':
    main()
