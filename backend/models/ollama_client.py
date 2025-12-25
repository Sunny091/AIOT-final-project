import requests
import json
from typing import List, Dict, Any, Optional
from config import Config

class OllamaClient:
    """Wrapper for Ollama API based on the example notebook"""
    
    def __init__(self, api_key: Optional[str] = None, uri: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or Config.OLLAMA_API_KEY
        self.uri = uri or Config.OLLAMA_URI
        self.model = model or Config.OLLAMA_MODEL
        self.chat_api_url = f"{self.uri}/api/chat"
        
    def generate(self, 
                 messages: List[Dict[str, str]], 
                 stream: bool = False, 
                 options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate response from Ollama API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response
            options: Additional options like temperature, max_tokens
            
        Returns:
            Response dict containing 'message' with 'thinking' and 'content'
        """
        if options is None:
            options = {"temperature": 0.7}
            
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": options
        })
        
        headers = {
            "X-API-Key": self.api_key,
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        
        try:
            response = requests.post(self.chat_api_url, headers=headers, data=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "message": {
                    "thinking": "",
                    "content": f"Error calling Ollama API: {str(e)}"
                }
            }
    
    def chat(self, user_message: str, system_prompt: Optional[str] = None, 
             temperature: float = 0.7) -> str:
        """
        Simple chat interface
        
        Args:
            user_message: User's message
            system_prompt: Optional system prompt
            temperature: Temperature for generation
            
        Returns:
            Assistant's response content
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        options = {"temperature": temperature}
        response = self.generate(messages, stream=False, options=options)
        
        if "error" in response:
            return response["message"]["content"]
            
        return response.get("message", {}).get("content", "No response generated")
    
    def chat_with_tools(self, user_message: str, available_tools: List[Dict[str, Any]], 
                        conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Chat with MCP tool selection capability
        
        Args:
            user_message: User's message
            available_tools: List of available MCP tools with descriptions
            conversation_history: Previous conversation messages
            
        Returns:
            Dict with 'content', 'selected_tool', 'tool_params', 'thinking'
        """
        tools_description = "\n".join([
            f"- {tool['name']}: {tool['description']}" 
            for tool in available_tools
        ])
        
        system_prompt = f"""You are a cryptocurrency trading assistant with access to the following tools via MCP (Model Context Protocol):

{tools_description}

When the user asks to perform an action, you MUST:
1. Analyze the user's intent
2. Select the most appropriate tool
3. Extract necessary parameters
4. Return ONLY valid JSON in this exact format:

{{"tool": "tool_name", "params": {{"param1": "value1"}}, "explanation": "what I'm doing"}}

Examples:
- User: "查詢BTC價格" -> {{"tool": "get_crypto_price", "params": {{"symbol": "BTC/USDT"}}, "explanation": "查詢BTC當前價格"}}
- User: "分析ETH" -> {{"tool": "combined_analysis", "params": {{"symbol": "ETH/USDT"}}, "explanation": "對ETH進行綜合分析"}}
- User: "BTC的新聞情感" -> {{"tool": "analyze_sentiment", "params": {{"symbol": "BTC"}}, "explanation": "分析BTC新聞情感"}}

IMPORTANT: Return ONLY the JSON object, nothing else. No extra text, no thinking process, just pure JSON."""

        messages = []
        messages.append({"role": "system", "content": system_prompt})
        
        if conversation_history:
            messages.extend(conversation_history)
            
        messages.append({"role": "user", "content": user_message})
        
        response = self.generate(messages, stream=False, options={"temperature": 0.3})
        
        message = response.get("message", {})
        content = message.get("content", "")
        thinking = message.get("thinking", "")
        tool_calls_native = message.get("tool_calls", [])
        
        # Try to extract tool call - check native tool_calls first (OpenAI format)
        tool_call = None
        explanation = ""
        
        if tool_calls_native and len(tool_calls_native) > 0:
            # Handle native tool calling format (OpenAI-style)
            first_call = tool_calls_native[0]
            function_info = first_call.get("function", {})
            raw_tool_name = function_info.get("name", "")
            
            # Clean tool name - remove various prefixes
            tool_name = raw_tool_name
            for prefix in ["tool.", "tool_", "tools."]:
                if tool_name.startswith(prefix):
                    tool_name = tool_name[len(prefix):]
            
            # Handle "tool_use" - this is a generic tool use indicator, need to infer actual tool
            if tool_name == "use" or tool_name == "tool_use" or tool_name == "tool_call" or not tool_name:
                print(f"[OLLAMA] Generic tool_use detected, inferring from message", flush=True)
                # Check if arguments contain the actual tool info
                if isinstance(tool_params, dict) and "tool" in tool_params:
                    tool_call = {
                        "tool": tool_params.get("tool"),
                        "params": tool_params.get("params", {}),
                        "explanation": tool_params.get("explanation", thinking or "正在為您查詢...")
                    }
                    explanation = tool_call.get("explanation", "正在為您查詢...")
                else:
                    tool_call = self._infer_tool_from_message(user_message)
                    if tool_call:
                        explanation = tool_call.get("explanation", "正在為您查詢...")
            else:
                tool_params = function_info.get("arguments", {})
                
                # Ensure params is a dict
                if isinstance(tool_params, str):
                    try:
                        tool_params = json.loads(tool_params)
                    except:
                        tool_params = {}
                
                # Check if tool_params contains a nested tool call structure
                if isinstance(tool_params, dict) and "tool" in tool_params and "params" in tool_params:
                    # The arguments contain the actual tool call
                    print(f"[OLLAMA] Found nested tool call in arguments", flush=True)
                    tool_call = {
                        "tool": tool_params.get("tool"),
                        "params": tool_params.get("params", {}),
                        "explanation": tool_params.get("explanation", thinking or f"調用工具")
                    }
                    explanation = tool_call.get("explanation", "正在為您查詢...")
                else:
                    tool_call = {
                        "tool": tool_name,
                        "params": tool_params,
                        "explanation": thinking or f"調用工具: {tool_name}"
                    }
                    explanation = thinking or "正在為您查詢..."
        else:
            # Fallback: try to parse JSON from content
            try:
                import re
                # Look for JSON in the response
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    json_str = json_match.group()
                    parsed_json = json.loads(json_str)
                    
                    # Check if this is a tool call (has "tool" and "params" keys)
                    if "tool" in parsed_json and "params" in parsed_json:
                        tool_call = parsed_json
                        explanation = tool_call.get("explanation", "")
                    else:
                        # LLM returned data instead of tool call, use fallback
                        print(f"[OLLAMA] LLM returned data instead of tool call", flush=True)
                        tool_call = self._infer_tool_from_message(user_message)
                        explanation = "正在為您查詢..."
            except Exception as e:
                # If JSON parsing fails, try to infer the tool from the message
                print(f"[OLLAMA] Failed to parse tool call: {e}", flush=True)
                print(f"[OLLAMA] Content: {content}", flush=True)
                
                # Fallback: parse user message directly
                tool_call = self._infer_tool_from_message(user_message)
                explanation = "正在為您查詢..."
        
        return {
            "content": explanation if tool_call else content,
            "thinking": thinking,
            "tool_call": tool_call
        }
    
    def _infer_tool_from_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Fallback method to infer tool from user message"""
        message_lower = message.lower()

        # Extract symbol first (used by multiple tool types)
        symbol = 'BTC/USDT'
        base_symbol = 'BTC'
        for s in ['btc', 'eth', 'bnb', 'sol', 'ada', 'xrp', 'doge']:
            if s in message_lower:
                symbol = s.upper() + '/USDT'
                base_symbol = s.upper()
                break

        # Chart/Trend queries - check BEFORE general analysis
        if any(word in message_lower for word in ['走勢', '圖表', 'chart', 'trend', 'k線', 'kline', '曲線', '歷史價格']):
            return {
                "tool": "create_chart",
                "params": {"symbol": symbol, "chart_type": "line", "timeframe": "1d", "limit": 30},
                "explanation": f"生成{symbol}價格走勢圖"
            }

        # OHLCV/Candlestick queries
        if any(word in message_lower for word in ['ohlcv', '蠟燭圖', 'candlestick', 'k棒']):
            return {
                "tool": "get_crypto_ohlcv",
                "params": {"symbol": symbol, "timeframe": "1d", "limit": 30},
                "explanation": f"獲取{symbol}的K線數據"
            }

        # Price queries (current price only)
        if any(word in message_lower for word in ['價格', 'price', '多少錢', '查詢']):
            return {
                "tool": "get_crypto_price",
                "params": {"symbol": symbol},
                "explanation": f"查詢{symbol}當前價格"
            }

        # News queries (only news, no sentiment)
        if any(word in message_lower for word in ['新聞', 'news', '消息', '報導']):
            return {
                "tool": "get_crypto_news",
                "params": {"symbol": base_symbol},
                "explanation": f"獲取{base_symbol}相關新聞"
            }

        # Sentiment analysis
        if any(word in message_lower for word in ['情感', 'sentiment', '情緒']):
            return {
                "tool": "analyze_sentiment",
                "params": {"symbol": base_symbol},
                "explanation": f"分析{base_symbol}新聞情感"
            }

        # Technical analysis
        if any(word in message_lower for word in ['技術分析', 'technical', '預測', '指標']):
            return {
                "tool": "technical_analysis",
                "params": {"symbol": symbol},
                "explanation": f"對{symbol}進行技術分析"
            }

        # Combined analysis - use more specific keywords
        if any(word in message_lower for word in ['綜合分析', '完整分析', '全面分析', '交易建議']):
            return {
                "tool": "combined_analysis",
                "params": {"symbol": symbol},
                "explanation": f"對{symbol}進行綜合分析"
            }

        return None
