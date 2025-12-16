#!/usr/bin/env python3
"""
解壓加密貨幣新聞數據集
需要系統安裝 unrar: sudo apt install unrar
"""
import os
import subprocess
import sys

def check_unrar():
    """檢查 unrar 是否安裝"""
    try:
        subprocess.run(['unrar'], capture_output=True)
        return True
    except FileNotFoundError:
        return False

def extract_dataset():
    """解壓數據集"""
    dataset_dir = 'data/cryptoNewsDataset/csvOutput'
    
    if not os.path.exists(dataset_dir):
        print(f"❌ 數據集目錄不存在: {dataset_dir}")
        return False
    
    print("=" * 60)
    print("解壓加密貨幣新聞數據集")
    print("=" * 60)
    print()
    
    # Check for unrar
    if not check_unrar():
        print("❌ 未安裝 unrar 工具\n")
        print("請安裝 unrar:")
        print("  Ubuntu/Debian: sudo apt install unrar")
        print("  macOS: brew install unrar")
        print("  或手動下載: https://www.rarlab.com/download.htm")
        print()
        print("或使用在線工具解壓 RAR 文件:")
        print("  - extract.me")
        print("  - online-convert.com")
        return False
    
    # Find RAR files
    rar_files = []
    for f in os.listdir(dataset_dir):
        if f.endswith('.rar'):
            rar_files.append(os.path.join(dataset_dir, f))
    
    if not rar_files:
        print("⚠️  未找到 RAR 文件")
        return False
    
    print(f"找到 {len(rar_files)} 個 RAR 文件\n")
    
    # Extract main file first (joined result)
    main_file = None
    for rar in rar_files:
        if 'joinedResult' in rar:
            main_file = rar
            break
    
    if main_file:
        print(f"📦 優先解壓主文件: {os.path.basename(main_file)}")
        try:
            subprocess.run(
                ['unrar', 'e', '-o+', main_file, dataset_dir],
                check=True,
                capture_output=True
            )
            print(f"✅ 解壓成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ 解壓失敗: {e}")
            return False
    
    # Extract other files
    print(f"\n📦 解壓其他文件...")
    for rar_file in rar_files:
        if rar_file == main_file:
            continue
        
        basename = os.path.basename(rar_file)
        try:
            subprocess.run(
                ['unrar', 'e', '-o+', rar_file, dataset_dir],
                check=True,
                capture_output=True
            )
            print(f"  ✅ {basename}")
        except subprocess.CalledProcessError:
            print(f"  ⚠️  {basename} (跳過)")
    
    # Check extracted files
    print(f"\n📊 檢查解壓後的 CSV 文件:")
    csv_files = []
    for f in os.listdir(dataset_dir):
        if f.endswith('.csv'):
            csv_files.append(f)
            size = os.path.getsize(os.path.join(dataset_dir, f)) / 1024 / 1024
            print(f"  📄 {f} ({size:.2f} MB)")
    
    if csv_files:
        print(f"\n✅ 解壓完成! 共 {len(csv_files)} 個 CSV 文件")
        return True
    else:
        print(f"\n❌ 未找到 CSV 文件")
        return False

if __name__ == '__main__':
    success = extract_dataset()
    sys.exit(0 if success else 1)
