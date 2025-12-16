#!/usr/bin/env python3
"""
圖表功能演示腳本
Demo script for chart functionality
"""

import sys
sys.path.insert(0, '/user_data/1141/aiot/final/mcp_system_final')

from backend.mcp_orchestrator import MCPOrchestrator
import json

def demo_chart_feature():
    """演示圖表功能"""
    
    print("=" * 60)
    print("📊 圖表功能演示")
    print("=" * 60)
    print()
    
    orchestrator = MCPOrchestrator()
    
    # Test 1: Price chart via natural language
    print("測試 1: 使用自然語言生成圖表")
    print("-" * 60)
    
    user_message = "顯示 BTC 過去一週的價格走勢圖"
    print(f"用戶輸入: {user_message}")
    print()
    
    result = orchestrator.process_user_message(user_message)
    
    if result.get('success'):
        print(f"✅ 處理成功!")
        print(f"   思考過程: {result.get('thinking', 'N/A')}")
        print(f"   使用工具: {result.get('tool_used', 'N/A')}")
        print(f"   回應訊息: {result.get('message', 'N/A')[:100]}...")
        
        if result.get('tool_result'):
            tool_result = result['tool_result']
            if tool_result.get('success'):
                print(f"   數據點數: {tool_result.get('data_points', 'N/A')}")
                print(f"   交易對: {tool_result.get('symbol', 'N/A')}")
                print(f"   時間週期: {tool_result.get('timeframe', 'N/A')}")
                
                if tool_result.get('chart_data'):
                    chart_data = tool_result['chart_data']
                    print(f"   圖表標題: {chart_data.get('title', 'N/A')}")
                    timestamps = chart_data.get('timestamps', [])
                    values = chart_data.get('values', [])
                    if timestamps and values:
                        print(f"   時間範圍: {timestamps[0]} ~ {timestamps[-1]}")
                        print(f"   價格範圍: ${min(values):.2f} ~ ${max(values):.2f}")
    else:
        print(f"❌ 處理失敗: {result.get('error', 'Unknown error')}")
    
    print()
    print("=" * 60)
    print()
    
    # Test 2: Direct tool call
    print("測試 2: 直接調用圖表工具")
    print("-" * 60)
    
    tool_call = {
        'tool': 'create_chart',
        'params': {
            'data_source': 'price',
            'symbol': 'ETH/USDT',
            'timeframe': '4h',
            'chart_type': 'line'
        }
    }
    
    print(f"工具調用: {json.dumps(tool_call, indent=2, ensure_ascii=False)}")
    print()
    
    tool_result = orchestrator._execute_tool(tool_call)
    
    if tool_result.get('success'):
        print(f"✅ 執行成功!")
        print(f"   數據點數: {tool_result.get('data_points', 'N/A')}")
        print(f"   交易對: {tool_result.get('symbol', 'N/A')}")
        
        if tool_result.get('chart_data'):
            chart_data = tool_result['chart_data']
            print(f"   圖表類型: {chart_data.get('type', 'N/A')}")
            print(f"   圖表標題: {chart_data.get('title', 'N/A')}")
    else:
        print(f"❌ 執行失敗: {tool_result.get('error', 'Unknown error')}")
    
    print()
    print("=" * 60)
    print()
    
    # Show available tools
    print("可用的 MCP 工具:")
    print("-" * 60)
    for i, tool_def in enumerate(orchestrator.tool_definitions, 1):
        name = tool_def.get('name', 'Unknown')
        desc = tool_def.get('description', 'No description')
        icon = "📊" if 'chart' in name.lower() else "⚙️"
        print(f"{i:2d}. {icon} {name}")
        print(f"    {desc}")
    
    print()
    print("=" * 60)
    print("✅ 演示完成!")
    print("=" * 60)

if __name__ == '__main__':
    demo_chart_feature()
