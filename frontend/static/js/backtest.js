// Backtest page JavaScript

let backtestResults = [];
let performanceChart = null;
let comparisonChart = null;

// Load results on page load
document.addEventListener('DOMContentLoaded', function() {
    loadBacktestResults();
    
    // Set default date range (last 30 days)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);
    
    document.getElementById('end_date').valueAsDate = endDate;
    document.getElementById('start_date').valueAsDate = startDate;
    
    // Handle form submission
    document.getElementById('backtestForm').addEventListener('submit', function(e) {
        e.preventDefault();
        runBacktest();
    });
});

// Run backtest
async function runBacktest() {
    const symbol = document.getElementById('symbol').value;
    const timeframe = document.getElementById('timeframe').value;
    const strategy = document.getElementById('strategy').value;
    const initial_capital = parseFloat(document.getElementById('initial_capital').value);
    const start_date = document.getElementById('start_date').value;
    const end_date = document.getElementById('end_date').value;
    
    // Show loading
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('resultsContainer').innerHTML = '<p class="text-center">正在運行回測...</p>';
    
    try {
        const params = {
            symbol: symbol,
            timeframe: timeframe,
            strategy: strategy,
            initial_capital: initial_capital
        };
        
        // Add date range if specified
        if (start_date) {
            params.start_date = start_date;
        }
        if (end_date) {
            params.end_date = end_date;
        }
        
        const response = await fetch('/api/backtest/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        // Hide loading
        document.getElementById('loadingIndicator').style.display = 'none';
        
        if (data.success) {
            // Reload results
            await loadBacktestResults();
            alert('回測完成！');
        } else {
            alert('回測失敗: ' + data.error);
            console.error('Backtest error:', data);
        }
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loadingIndicator').style.display = 'none';
        alert('執行回測時發生錯誤');
    }
}

// Load backtest results
async function loadBacktestResults() {
    try {
        const response = await fetch('/api/backtest/results?limit=10');
        const data = await response.json();
        
        if (data.success && data.results.length > 0) {
            backtestResults = data.results;
            displayResults(backtestResults);
            updateCharts(backtestResults);
        } else {
            document.getElementById('resultsContainer').innerHTML = 
                '<p class="text-center">暫無回測結果，請運行一個回測。</p>';
        }
        
    } catch (error) {
        console.error('Error loading results:', error);
        document.getElementById('resultsContainer').innerHTML = 
            '<p class="text-center">載入結果時發生錯誤。</p>';
    }
}

// Display results
function displayResults(results) {
    const container = document.getElementById('resultsContainer');
    
    if (!results || results.length === 0) {
        container.innerHTML = '<p class="text-center">暫無回測結果。</p>';
        return;
    }
    
    let html = '';
    
    results.reverse().forEach((result, index) => {
        const isProfit = result.total_return_pct > 0;
        const badgeClass = isProfit ? 'badge-success' : 'badge-danger';
        
        // Format date range display
        let dateRangeStr = '';
        if (result.start_date || result.end_date) {
            const startStr = result.start_date || '開始';
            const endStr = result.end_date || '結束';
            dateRangeStr = ` | ${startStr} ~ ${endStr}`;
        }
        
        html += `
            <div class="result-card">
                <div class="result-header">
                    <div>
                        <div class="result-title">${result.symbol || 'N/A'} - ${getStrategyName(result.strategy)}</div>
                        <small style="color: #94a3b8;">${result.timeframe || '1h'}${dateRangeStr} | ${new Date(result.timestamp).toLocaleString('zh-TW')}</small>
                    </div>
                    <div class="result-badge ${badgeClass}">
                        ${isProfit ? '📈' : '📉'} ${result.total_return_pct.toFixed(2)}%
                    </div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-label">初始資金</div>
                        <div class="metric-value">$${result.initial_capital.toLocaleString()}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">最終價值</div>
                        <div class="metric-value">$${result.final_value.toFixed(2).toLocaleString()}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">總回報</div>
                        <div class="metric-value" style="color: ${isProfit ? 'var(--success-color)' : 'var(--danger-color)'};">
                            ${result.total_return_pct.toFixed(2)}%
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">夏普比率</div>
                        <div class="metric-value" style="color: ${result.sharpe_ratio > 1 ? 'var(--success-color)' : (result.sharpe_ratio > 0 ? '#f59e0b' : 'var(--danger-color)')};">
                            ${result.sharpe_ratio ? result.sharpe_ratio.toFixed(3) : '0.000'}
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">最大回撤</div>
                        <div class="metric-value" style="color: var(--danger-color);">
                            ${result.max_drawdown_pct.toFixed(2)}%
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">總交易次數</div>
                        <div class="metric-value">${result.total_trades || 0}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">獲利交易</div>
                        <div class="metric-value" style="color: var(--success-color);">
                            ${result.winning_trades || 0}
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">虧損交易</div>
                        <div class="metric-value" style="color: var(--danger-color);">
                            ${result.losing_trades || 0}
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">勝率</div>
                        <div class="metric-value" style="color: ${result.win_rate > 50 ? 'var(--success-color)' : '#f59e0b'};">
                            ${result.win_rate ? result.win_rate.toFixed(1) : '0.0'}%
                        </div>
                    </div>
                    ${result.profit_factor ? `
                    <div class="metric-item">
                        <div class="metric-label">獲利因子</div>
                        <div class="metric-value" style="color: ${result.profit_factor > 1 ? 'var(--success-color)' : 'var(--danger-color)'};">
                            ${result.profit_factor.toFixed(2)}
                        </div>
                    </div>` : ''}
                    ${result.avg_win ? `
                    <div class="metric-item">
                        <div class="metric-label">平均獲利</div>
                        <div class="metric-value" style="color: var(--success-color);">
                            $${result.avg_win.toFixed(2)}
                        </div>
                    </div>` : ''}
                    ${result.avg_loss ? `
                    <div class="metric-item">
                        <div class="metric-label">平均虧損</div>
                        <div class="metric-value" style="color: var(--danger-color);">
                            $${Math.abs(result.avg_loss).toFixed(2)}
                        </div>
                    </div>` : ''}
                </div>
            </div>`;
    });
    
    container.innerHTML = html;
}

// Update charts
function updateCharts(results) {
    if (!results || results.length === 0) return;
    
    document.getElementById('chartsContainer').style.display = 'grid';
    
    // Performance chart
    updatePerformanceChart(results);
    
    // Comparison chart
    updateComparisonChart(results);
}

// Update performance chart
function updatePerformanceChart(results) {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    
    if (performanceChart) {
        performanceChart.destroy();
    }
    
    const labels = results.map((r, i) => `測試 ${i + 1}`);
    const returns = results.map(r => r.total_return_pct);
    const sharpe = results.map(r => r.sharpe_ratio);
    
    performanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '總回報 (%)',
                    data: returns,
                    backgroundColor: returns.map(r => r > 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)'),
                    borderColor: returns.map(r => r > 0 ? 'rgb(16, 185, 129)' : 'rgb(239, 68, 68)'),
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: '夏普比率',
                    data: sharpe,
                    type: 'line',
                    borderColor: 'rgb(124, 58, 237)',
                    backgroundColor: 'rgba(124, 58, 237, 0.1)',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    ticks: { color: '#94a3b8' },
                    grid: { drawOnChartArea: false }
                },
                x: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9' }
                }
            }
        }
    });
}

// Update comparison chart
function updateComparisonChart(results) {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    
    if (comparisonChart) {
        comparisonChart.destroy();
    }
    
    // Group by strategy
    const strategies = {};
    results.forEach(r => {
        const strategy = r.strategy || 'unknown';
        if (!strategies[strategy]) {
            strategies[strategy] = { returns: [], wins: [] };
        }
        strategies[strategy].returns.push(r.total_return_pct);
        strategies[strategy].wins.push(r.win_rate || 0);
    });
    
    const labels = Object.keys(strategies).map(s => getStrategyName(s));
    const avgReturns = Object.values(strategies).map(s => 
        s.returns.reduce((a, b) => a + b, 0) / s.returns.length
    );
    const avgWinRates = Object.values(strategies).map(s => 
        s.wins.reduce((a, b) => a + b, 0) / s.wins.length
    );
    
    comparisonChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['平均回報', '平均勝率', '穩定性'],
            datasets: labels.map((label, i) => ({
                label: label,
                data: [
                    avgReturns[i],
                    avgWinRates[i],
                    avgReturns[i] > 0 ? 80 : 40  // Simple stability metric
                ],
                borderColor: getStrategyColor(i),
                backgroundColor: getStrategyColor(i, 0.2),
                pointBackgroundColor: getStrategyColor(i)
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    ticks: { color: '#94a3b8', backdropColor: 'transparent' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' },
                    pointLabels: { color: '#f1f5f9' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9' }
                }
            }
        }
    });
}

// Helper functions
function getStrategyName(strategy) {
    const names = {
        'sentiment': '情感分析策略',
        'technical': '技術分析策略',
        'combined': '綜合策略',
        'macd': 'MACD 策略',
        'ml': '機器學習策略'
    };
    return names[strategy] || strategy;
}

function getStrategyColor(index, alpha = 1) {
    const colors = [
        `rgba(37, 99, 235, ${alpha})`,
        `rgba(124, 58, 237, ${alpha})`,
        `rgba(16, 185, 129, ${alpha})`,
        `rgba(245, 158, 11, ${alpha})`
    ];
    return colors[index % colors.length];
}
