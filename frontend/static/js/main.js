// Main chat interface JavaScript

let conversationHistory = [];

// Send message on Enter key
document.getElementById('chatInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Quick action function
function quickAction(message) {
    document.getElementById('chatInput').value = message;
    sendMessage();
}

// Disable buttons during processing
function setButtonsDisabled(disabled) {
    const buttons = document.querySelectorAll('.action-buttons button, .btn-primary, .btn-secondary');
    buttons.forEach(button => {
        button.disabled = disabled;
    });
}

// Send message to backend
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Disable buttons
    setButtonsDisabled(true);
    
    // Clear input
    input.value = '';
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Show loading indicator
    const loadingId = showLoadingMessage();
    
    // Update status
    updateStatus('🔄 AI 思考中...', 'warning');
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        // Remove loading indicator
        removeLoadingMessage(loadingId);
        
        const data = await response.json();
        
        if (data.success) {
            // Add bot response
            addBotResponse(data);
            updateStatus('✅ 就緒', 'success');
        } else {
            addMessage('❌ 抱歉，處理您的請求時發生錯誤: ' + data.error, 'bot');
            updateStatus('❌ 錯誤', 'danger');
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeLoadingMessage(loadingId);
        addMessage('❌ 連接伺服器時發生錯誤，請檢查網路連接。錯誤詳情: ' + error.message, 'bot');
        updateStatus('❌ 連接錯誤', 'danger');
    } finally {
        // Re-enable buttons
        setButtonsDisabled(false);
    }
}

// Show loading message
function showLoadingMessage() {
    const messagesDiv = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    const loadingId = 'loading-' + Date.now();
    loadingDiv.id = loadingId;
    loadingDiv.className = 'message bot-message loading-message';
    
    loadingDiv.innerHTML = `
        <div class="message-content">
            <strong>🤖 AI 助手：</strong>
            <div class="loading-dots">
                <span class="dot">●</span>
                <span class="dot">●</span>
                <span class="dot">●</span>
                <span style="margin-left: 10px;">正在分析您的請求...</span>
            </div>
        </div>`;
    
    messagesDiv.appendChild(loadingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    return loadingId;
}

// Remove loading message
function removeLoadingMessage(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// Add message to chat
function addMessage(content, type) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (type === 'user') {
        contentDiv.innerHTML = `<strong>👤 您：</strong><p>${escapeHtml(content)}</p>`;
    } else {
        contentDiv.innerHTML = `<strong>🤖 AI 助手：</strong><p>${escapeHtml(content)}</p>`;
    }
    
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Add bot response with tool results
function addBotResponse(data) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    let html = `<strong>🤖 AI 助手：</strong>`;
    
    // Add thinking process if available
    if (data.thinking) {
        html += `<p style="color: #94a3b8; font-style: italic; font-size: 0.9rem;">💭 ${escapeHtml(data.thinking)}</p>`;
    }
    
    // Add main message
    html += `<p>${escapeHtml(data.message)}</p>`;
    
    // Add tool result if available
    if (data.tool_result && data.tool_used) {
        html += formatToolResult(data.tool_used, data.tool_result);
    }
    
    contentDiv.innerHTML = html;
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Format tool result display
function formatToolResult(toolName, result) {
    if (!result || !result.success) {
        return `<div class="tool-result">
            <div class="result-title">❌ 工具執行失敗</div>
            <p>${result.error || '未知錯誤'}</p>
        </div>`;
    }
    
    // Handle chart display
    if (toolName === 'create_chart' && result.chart_data) {
        displayChart(result);
        return `<div class="tool-result">
            <div class="result-title">✅ 圖表已生成</div>
            <p>圖表已在上方顯示區域展示</p>
        </div>`;
    }
    
    let html = `<div class="tool-result">
        <div class="result-title">✅ 工具執行結果：${toolName}</div>
        <div class="result-data">`;
    
    // Format based on tool type
    if (result.symbol && result.price) {
        // Price data
        html += `
            <div class="result-item">
                <span class="result-label">交易對</span>
                <span class="result-value">${result.symbol}</span>
            </div>
            <div class="result-item">
                <span class="result-label">當前價格</span>
                <span class="result-value">$${result.price.toFixed(2)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">24小時漲跌</span>
                <span class="result-value ${result.change_24h > 0 ? 'positive' : 'negative'}">
                    ${result.change_24h > 0 ? '+' : ''}${result.change_24h.toFixed(2)}%
                </span>
            </div>
            <div class="result-item">
                <span class="result-label">24小時交易量</span>
                <span class="result-value">$${formatNumber(result.volume_24h)}</span>
            </div>`;
    } else if (result.aggregate_sentiment) {
        // Sentiment analysis
        const agg = result.aggregate_sentiment;
        html += `
            <div class="result-item">
                <span class="result-label">整體情感</span>
                <span class="result-value ${getSentimentClass(agg.overall_sentiment)}">
                    ${getSentimentEmoji(agg.overall_sentiment)} ${agg.overall_sentiment.toUpperCase()}
                </span>
            </div>
            <div class="result-item">
                <span class="result-label">情感分數</span>
                <span class="result-value">${agg.sentiment_score.toFixed(3)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">分析文章數</span>
                <span class="result-value">${agg.counts.total}</span>
            </div>
            <div class="result-item">
                <span class="result-label">正面/中性/負面</span>
                <span class="result-value">${agg.counts.positive}/${agg.counts.neutral}/${agg.counts.negative}</span>
            </div>`;
    } else if (result.predicted_price) {
        // Technical analysis
        html += `
            <div class="result-item">
                <span class="result-label">當前價格</span>
                <span class="result-value">$${result.current_price.toFixed(2)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">預測價格</span>
                <span class="result-value">$${result.predicted_price.toFixed(2)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">預測漲跌</span>
                <span class="result-value ${result.predicted_change_pct > 0 ? 'positive' : 'negative'}">
                    ${result.predicted_change_pct > 0 ? '+' : ''}${result.predicted_change_pct.toFixed(2)}%
                </span>
            </div>`;
        
        if (result.signals && result.signals.recommendation) {
            html += `
                <div class="result-item">
                    <span class="result-label">建議操作</span>
                    <span class="result-value ${getRecommendationClass(result.signals.recommendation)}">
                        ${result.signals.recommendation}
                    </span>
                </div>`;
        }
    } else if (result.recommendation) {
        // Combined analysis
        const rec = result.recommendation;
        html += `
            <div class="result-item">
                <span class="result-label">綜合建議</span>
                <span class="result-value ${getRecommendationClass(rec.action)}">
                    ${rec.action}
                </span>
            </div>
            <div class="result-item">
                <span class="result-label">信心水平</span>
                <span class="result-value">${(rec.confidence * 100).toFixed(1)}%</span>
            </div>`;
    } else if (result.final_value !== undefined) {
        // Backtest result
        html += `
            <div class="result-item">
                <span class="result-label">策略</span>
                <span class="result-value">${result.strategy}</span>
            </div>
            <div class="result-item">
                <span class="result-label">總回報</span>
                <span class="result-value ${result.total_return_pct > 0 ? 'positive' : 'negative'}">
                    ${result.total_return_pct > 0 ? '+' : ''}${result.total_return_pct.toFixed(2)}%
                </span>
            </div>
            <div class="result-item">
                <span class="result-label">夏普比率</span>
                <span class="result-value">${result.sharpe_ratio.toFixed(2)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">最大回撤</span>
                <span class="result-value negative">-${result.max_drawdown_pct.toFixed(2)}%</span>
            </div>
            <div class="result-item">
                <span class="result-label">勝率</span>
                <span class="result-value">${result.win_rate.toFixed(1)}%</span>
            </div>`;
    }
    
    html += `</div></div>`;
    return html;
}

// Helper functions
function getSentimentClass(sentiment) {
    if (sentiment === 'positive') return 'positive';
    if (sentiment === 'negative') return 'negative';
    return '';
}

function getSentimentEmoji(sentiment) {
    if (sentiment === 'positive') return '😊';
    if (sentiment === 'negative') return '😟';
    return '😐';
}

function getRecommendationClass(rec) {
    if (rec && (rec.includes('BUY') || rec === 'BUY')) return 'positive';
    if (rec && (rec.includes('SELL') || rec === 'SELL')) return 'negative';
    return '';
}

function formatNumber(num) {
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(2);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function updateStatus(text, type) {
    const statusText = document.getElementById('statusText');
    
    // Add processing indicator for warning state
    if (type === 'warning') {
        statusText.innerHTML = `<span class="processing-indicator"></span>${text}`;
    } else {
        statusText.textContent = text;
    }
    
    statusText.className = type === 'success' ? 'positive' : type === 'danger' ? 'negative' : '';
}

// Reset conversation
async function resetChat() {
    if (confirm('確定要重置對話嗎？')) {
        try {
            await fetch('/api/reset', { method: 'POST' });
            conversationHistory = [];
            
            const messagesDiv = document.getElementById('chatMessages');
            messagesDiv.innerHTML = `
                <div class="message bot-message">
                    <div class="message-content">
                        <strong>🤖 AI 助手：</strong>
                        <p>對話已重置。請告訴我您想做什麼！</p>
                    </div>
                </div>`;
            
            updateStatus('就緒', 'success');
        } catch (error) {
            console.error('Error:', error);
            alert('重置對話時發生錯誤');
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateStatus('就緒', 'success');
});

// Display chart using Plotly
function displayChart(chartResult) {
    const chartContainer = document.getElementById('chartContainer');
    const chartDisplay = document.getElementById('chartDisplay');
    
    // Show chart container
    chartContainer.style.display = 'block';
    
    // Clear previous chart
    chartDisplay.innerHTML = '';
    
    const chartData = chartResult.chart_data;
    
    if (chartData.type === 'candlestick' && chartResult.chart_html) {
        // Use the HTML from backend for candlestick
        chartDisplay.innerHTML = chartResult.chart_html;
    } else if (chartData.timestamps && chartData.values) {
        // Create line chart
        const trace = {
            x: chartData.timestamps,
            y: chartData.values,
            type: 'scatter',
            mode: 'lines',
            name: chartData.title || '價格',
            line: {
                color: '#00D9FF',
                width: 2
            }
        };
        
        const layout = {
            title: chartData.title || '價格走勢圖',
            xaxis: {
                title: '時間',
                type: 'date'
            },
            yaxis: {
                title: '價格 (USDT)'
            },
            template: 'plotly_dark',
            paper_bgcolor: '#1a1a2e',
            plot_bgcolor: '#16213e',
            hovermode: 'x unified',
            height: 500
        };
        
        Plotly.newPlot('chartDisplay', [trace], layout, {responsive: true});
    } else if (chartResult.chart_html) {
        // Fallback: use HTML from backend
        chartDisplay.innerHTML = chartResult.chart_html;
    }
    
    // Scroll to chart
    chartContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
