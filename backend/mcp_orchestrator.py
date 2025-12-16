from typing import Dict, Any, List
from backend.models.ollama_client import OllamaClient
from backend.mcp_tools.crypto_tools import CryptoDataTool, CryptoNewsTool, TradingStrategyTool
from backend.mcp_tools.chart_tool import ChartTool
from backend.models.sentiment_analyzer import SentimentAnalysisTool
from backend.models.technical_analysis import TechnicalAnalysisTool
from backend.models.backtest_engine import BacktestTool


class MCPOrchestrator:
    """
    MCP (Model Context Protocol) Orchestrator
    Manages tool selection and execution based on LLM responses
    """
    
    def __init__(self):
        self.ollama_client = OllamaClient()
        
        # Initialize all MCP tools
        self.tools = {
            'crypto_data': CryptoDataTool(),
            'crypto_news': CryptoNewsTool(),
            'sentiment_analysis': SentimentAnalysisTool(),
            'technical_analysis': TechnicalAnalysisTool(),
            'trading_strategy': TradingStrategyTool(),
            'backtest': BacktestTool(),
            'chart': ChartTool()
        }
        
        # Build tool definitions for LLM
        self.tool_definitions = self._build_tool_definitions()
        
        # Conversation history
        self.conversation_history = []
    
    def _build_tool_definitions(self) -> List[Dict[str, Any]]:
        """Build tool definitions for LLM context"""
        definitions = [
            {
                "name": "get_crypto_price",
                "description": "獲取加密貨幣當前價格、24小時交易量、漲跌幅等市場數據"
            },
            {
                "name": "get_crypto_ohlcv",
                "description": "獲取加密貨幣的K線數據（OHLCV），可指定時間週期"
            },
            {
                "name": "get_crypto_news",
                "description": "獲取最新的加密貨幣相關新聞文章"
            },
            {
                "name": "analyze_sentiment",
                "description": "使用FinBERT對加密貨幣新聞進行情感分析（正面/負面/中性）"
            },
            {
                "name": "technical_analysis",
                "description": "使用深度學習進行技術分析，包括價格預測和交易信號"
            },
            {
                "name": "create_strategy",
                "description": "創建一個新的量化交易策略"
            },
            {
                "name": "list_strategies",
                "description": "列出所有已創建的交易策略"
            },
            {
                "name": "run_backtest",
                "description": "運行量化交易策略的回測，評估策略表現"
            },
            {
                "name": "get_backtest_results",
                "description": "獲取最近的回測結果"
            },
            {
                "name": "combined_analysis",
                "description": "綜合分析：結合新聞情感、技術分析、市場數據給出完整的交易建議"
            },
            {
                "name": "create_chart",
                "description": "創建時間序列圖表，顯示價格走勢、K線圖或自定義數據的折線圖"
            }
        ]
        return definitions
    
    def process_user_message(self, user_message: str) -> Dict[str, Any]:
        """
        Process user message through MCP architecture
        
        Args:
            user_message: User's natural language input
            
        Returns:
            Response with tool execution results
        """
        try:
            # Get LLM response with tool selection
            llm_response = self.ollama_client.chat_with_tools(
                user_message,
                self.tool_definitions,
                self.conversation_history[-10:]  # Last 10 messages
            )
            
            # Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            tool_call = llm_response.get('tool_call')
            response_content = llm_response.get('content', '')
            
            # Execute tool if selected
            if tool_call and isinstance(tool_call, dict):
                tool_result = self._execute_tool(tool_call)
                
                # Format user-friendly response
                formatted_message = self._format_tool_response(
                    tool_call.get('tool'),
                    tool_result,
                    response_content
                )
                
                # Add assistant response with tool result
                self.conversation_history.append({
                    "role": "assistant",
                    "content": formatted_message,
                    "tool_call": tool_call,
                    "tool_result": tool_result
                })
                
                return {
                    "success": True,
                    "message": formatted_message,
                    "thinking": llm_response.get('thinking', ''),
                    "tool_used": tool_call.get('tool'),
                    "tool_result": tool_result
                }
            else:
                # No tool needed, just conversation
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_content
                })
                
                return {
                    "success": True,
                    "message": response_content,
                    "thinking": llm_response.get('thinking', ''),
                    "tool_used": None
                }
                
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the selected tool with parameters"""
        tool_name = tool_call.get('tool', '')
        params = tool_call.get('params', {})
        
        print(f"[EXECUTE] Tool: {tool_name}, Params: {params}", flush=True)
        
        try:
            # Map tool names to actual tool execution
            if tool_name == 'get_crypto_price':
                params['action'] = 'price'
                return self.tools['crypto_data'].execute(params)
            
            elif tool_name == 'get_crypto_ohlcv':
                params['action'] = 'ohlcv'
                return self.tools['crypto_data'].execute(params)
            
            elif tool_name == 'get_crypto_news':
                return self.tools['crypto_news'].execute(params)
            
            elif tool_name == 'analyze_sentiment':
                # Fetch news first if not provided
                if 'articles' not in params and 'texts' not in params:
                    symbol = params.get('symbol', 'BTC')
                    news_result = self.tools['crypto_news'].execute({'symbol': symbol})
                    if news_result.get('success'):
                        params['articles'] = news_result.get('articles', [])
                
                return self.tools['sentiment_analysis'].execute(params)
            
            elif tool_name == 'technical_analysis':
                return self.tools['technical_analysis'].execute(params)
            
            elif tool_name == 'create_strategy':
                params['action'] = 'create'
                return self.tools['trading_strategy'].execute(params)
            
            elif tool_name == 'list_strategies':
                params['action'] = 'list'
                return self.tools['trading_strategy'].execute(params)
            
            elif tool_name == 'run_backtest':
                return self.tools['backtest'].execute(params)
            
            elif tool_name == 'get_backtest_results':
                return self.tools['backtest'].get_results()
            
            elif tool_name == 'combined_analysis':
                return self._combined_analysis(params)
            
            elif tool_name == 'create_chart':
                return self.tools['chart'].execute(params)
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
                
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _combined_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform combined analysis using multiple tools"""
        symbol = params.get('symbol', 'BTC/USDT')
        
        results = {
            "success": True,
            "symbol": symbol,
            "timestamp": None
        }
        
        try:
            # 1. Get current price
            price_result = self.tools['crypto_data'].execute({
                'symbol': symbol,
                'action': 'price'
            })
            results['current_price'] = price_result
            
            # 2. Get news and analyze sentiment
            base_symbol = symbol.split('/')[0]
            news_result = self.tools['crypto_news'].execute({'symbol': base_symbol})
            
            if news_result.get('success'):
                sentiment_result = self.tools['sentiment_analysis'].execute({
                    'articles': news_result.get('articles', [])
                })
                results['sentiment'] = sentiment_result
            
            # 3. Technical analysis
            tech_result = self.tools['technical_analysis'].execute({
                'symbol': symbol,
                'timeframe': params.get('timeframe', '1h')
            })
            results['technical_analysis'] = tech_result
            
            # 4. Generate overall recommendation
            recommendation = self._generate_recommendation(results)
            results['recommendation'] = recommendation
            
            return results
            
        except Exception as e:
            import traceback
            results['success'] = False
            results['error'] = str(e)
            results['traceback'] = traceback.format_exc()
            return results
    
    def _generate_recommendation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading recommendation from combined analysis"""
        score = 0
        factors = []
        
        # Sentiment score
        sentiment = analysis.get('sentiment', {})
        if sentiment.get('success'):
            agg_sentiment = sentiment.get('aggregate_sentiment', {})
            sentiment_score = agg_sentiment.get('sentiment_score', 0)
            score += sentiment_score * 0.4  # 40% weight
            factors.append(f"Sentiment: {agg_sentiment.get('overall_sentiment', 'neutral')}")
        
        # Technical analysis score
        tech = analysis.get('technical_analysis', {})
        if tech.get('success'):
            signals = tech.get('signals', {})
            signal_strength = signals.get('signal_strength', 0)
            score += signal_strength * 0.6  # 60% weight
            factors.append(f"Technical: {signals.get('recommendation', 'HOLD')}")
        
        # Determine action
        if score > 0.3:
            action = 'STRONG BUY'
        elif score > 0.1:
            action = 'BUY'
        elif score > -0.1:
            action = 'HOLD'
        elif score > -0.3:
            action = 'SELL'
        else:
            action = 'STRONG SELL'
        
        return {
            'action': action,
            'confidence': abs(score),
            'score': score,
            'factors': factors
        }
    
    def _format_tool_response(self, tool_name: str, tool_result: Dict[str, Any], 
                              default_message: str) -> str:
        """Format tool execution result into user-friendly message"""
        
        if not tool_result.get('success'):
            return f"❌ 執行失敗: {tool_result.get('error', '未知錯誤')}"
        
        # Format based on tool type
        if tool_name == 'get_crypto_price':
            data = tool_result
            symbol = data.get('symbol', '')
            price = data.get('price', 0)
            change = data.get('change_24h', 0)
            volume = data.get('volume_24h', 0)
            
            change_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            
            return f"""💰 {symbol} 當前價格

價格: ${price:,.2f}
24小時變化: {change_emoji} {change:+.2f}%
24小時最高: ${data.get('high_24h', 0):,.2f}
24小時最低: ${data.get('low_24h', 0):,.2f}
24小時交易量: ${volume:,.0f}"""
        
        elif tool_name == 'analyze_sentiment':
            sentiment = tool_result.get('aggregate_sentiment', {})
            overall = sentiment.get('overall_sentiment', 'neutral')
            score = sentiment.get('sentiment_score', 0)
            
            emoji_map = {'positive': '😊', 'negative': '😟', 'neutral': '😐'}
            emoji = emoji_map.get(overall, '😐')
            
            return f"""{emoji} 新聞情感分析結果

整體情感: {overall.upper()}
情感分數: {score:.2f}
正面: {sentiment.get('positive', 0)}篇
中性: {sentiment.get('neutral', 0)}篇  
負面: {sentiment.get('negative', 0)}篇"""
        
        elif tool_name == 'technical_analysis':
            signals = tool_result.get('signals', {})
            recommendation = signals.get('recommendation', 'HOLD')
            confidence = signals.get('confidence', 0)
            
            return f"""📊 技術分析結果

建議: {recommendation}
信心度: {confidence:.1%}
預測方向: {signals.get('predicted_direction', 'NEUTRAL')}
信號強度: {signals.get('signal_strength', 0):.2f}"""
        
        elif tool_name == 'combined_analysis':
            rec = tool_result.get('recommendation', {})
            action = rec.get('action', 'HOLD')
            confidence = rec.get('confidence', 0)
            
            return f"""🎯 綜合分析結果

交易建議: {action}
信心度: {confidence:.1%}
綜合評分: {rec.get('score', 0):.2f}

分析因素:
{chr(10).join(['• ' + f for f in rec.get('factors', [])])}"""
        
        elif tool_name == 'run_backtest':
            metrics = tool_result.get('metrics', {})
            total_return = metrics.get('total_return', 0)
            
            return f"""📈 回測結果

總收益率: {total_return:+.2f}%
最大回撤: {metrics.get('max_drawdown', 0):.2f}%
夏普比率: {metrics.get('sharpe_ratio', 0):.2f}
勝率: {metrics.get('win_rate', 0):.1f}%
總交易次數: {metrics.get('total_trades', 0)}"""
        
        elif tool_name == 'create_chart':
            chart_data = tool_result.get('chart_data', {})
            data_points = tool_result.get('data_points', 0)
            
            return f"""📊 圖表已生成

標題: {chart_data.get('title', '未命名圖表')}
數據點數: {data_points}
類型: {chart_data.get('type', 'line')}

圖表已在下方顯示 ⬇️"""
        
        else:
            # Default formatting
            return default_message or "✅ 操作完成"
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
