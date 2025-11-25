// BingX Local AI Trading Terminal - Frontend JavaScript

// Global variables
let terminal = null;
let chart = null;
let currentSymbol = 'BTC-USDT';
let currentTimeframe = '1m';
let isDemoMode = false;
let updateInterval = null;

// DOM Elements
const elements = {
    connectBtn: document.getElementById('connect-btn'),
    demoBtn: document.getElementById('demo-btn'),
    balanceDisplay: document.getElementById('balance-display'),
    symbolSelect: document.getElementById('symbol-select'),
    timeframeSelect: document.getElementById('timeframe-select'),
    chartContainer: document.getElementById('chart-container'),
    bidsList: document.getElementById('bids-list'),
    asksList: document.getElementById('asks-list'),
    spreadDisplay: document.getElementById('spread-display'),
    aiSignal: document.getElementById('signal-text'),
    confidenceText: document.getElementById('confidence-text'),
    rsiValue: document.getElementById('rsi-value'),
    macdValue: document.getElementById('macd-value'),
    volatilityValue: document.getElementById('volatility-value'),
    trendValue: document.getElementById('trend-value'),
    quantityInput: document.getElementById('quantity-input'),
    leverageInput: document.getElementById('leverage-input'),
    orderTypeSelect: document.getElementById('order-type-select'),
    executeTradeBtn: document.getElementById('execute-trade-btn'),
    positionsList: document.getElementById('positions-list'),
    historyBody: document.getElementById('history-body'),
    settingsModal: document.getElementById('settings-modal'),
    closeModal: document.querySelector('.close'),
    saveSettingsBtn: document.getElementById('save-settings-btn'),
    apiKeyInput: document.getElementById('api-key'),
    secretKeyInput: document.getElementById('secret-key'),
    demoCheckbox: document.getElementById('demo-checkbox'),
    refreshAiBtn: document.getElementById('refresh-ai-btn'),
    refreshPositionsBtn: document.getElementById('refresh-positions-btn'),
    refreshHistoryBtn: document.getElementById('refresh-history-btn')
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeChart();
    loadSettings();
});

// Initialize event listeners
function initializeEventListeners() {
    // Button events
    elements.connectBtn.addEventListener('click', showSettingsModal);
    elements.demoBtn.addEventListener('click', connectDemo);
    elements.saveSettingsBtn.addEventListener('click', saveSettings);
    elements.closeModal.addEventListener('click', hideSettingsModal);
    elements.refreshAiBtn.addEventListener('click', updateAIAnalysis);
    elements.refreshPositionsBtn.addEventListener('click', updatePositions);
    elements.refreshHistoryBtn.addEventListener('click', updateHistory);
    
    // Trading button
    elements.executeTradeBtn.addEventListener('click', executeTrade);
    
    // Dropdown events
    elements.symbolSelect.addEventListener('change', function() {
        currentSymbol = this.value;
        updateMarketData();
    });
    
    elements.timeframeSelect.addEventListener('change', function() {
        currentTimeframe = this.value;
        updateChartData();
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === elements.settingsModal) {
            hideSettingsModal();
        }
    });
}

// Initialize chart
function initializeChart() {
    const layout = {
        title: `${currentSymbol} Price Chart`,
        xaxis: { title: 'Time' },
        yaxis: { title: 'Price' },
        height: 400,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#ffffff' }
    };
    
    const config = { responsive: true };
    
    chart = Plotly.newPlot('chart-container', [], layout, config);
}

// Update chart with new data
function updateChartData() {
    // In a real implementation, this would fetch data from the backend
    // For now, we'll create mock data
    const time = [];
    const open = [];
    const high = [];
    const low = [];
    const close = [];
    
    const now = new Date();
    for (let i = 100; i >= 0; i--) {
        const timePoint = new Date(now.getTime() - i * 60000); // 1-minute intervals
        time.push(timePoint);
        
        const basePrice = 40000 + Math.random() * 1000 - 500; // Base price around $40,000
        const variation = Math.random() * 100;
        
        open.push(basePrice);
        high.push(basePrice + variation);
        low.push(basePrice - variation);
        close.push(basePrice + (Math.random() - 0.5) * 200);
    }
    
    const trace = {
        x: time,
        open: open,
        high: high,
        low: low,
        close: close,
        type: 'candlestick',
        name: currentSymbol
    };
    
    const layout = {
        title: `${currentSymbol} Price Chart (${currentTimeframe})`,
        xaxis: { title: 'Time' },
        yaxis: { title: 'Price' },
        height: 400,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#ffffff' }
    };
    
    Plotly.newPlot('chart-container', [trace], layout);
}

// Update market data (order book, etc.)
function updateMarketData() {
    updateOrderBook();
    updateChartData();
    updateAIAnalysis();
}

// Update order book
function updateOrderBook() {
    // Clear existing lists
    elements.bidsList.innerHTML = '';
    elements.asksList.innerHTML = '';
    
    // Generate mock order book data
    let bidPrice = 40000;
    let askPrice = 40001;
    
    // Add bids (buy orders)
    for (let i = 0; i < 10; i++) {
        const li = document.createElement('li');
        const amount = (Math.random() * 10).toFixed(4);
        li.innerHTML = `<span>${bidPrice.toFixed(2)}</span> <span>${amount}</span>`;
        elements.bidsList.appendChild(li);
        bidPrice -= (Math.random() * 10);
    }
    
    // Add asks (sell orders)
    for (let i = 0; i < 10; i++) {
        const li = document.createElement('li');
        const amount = (Math.random() * 10).toFixed(4);
        li.innerHTML = `<span>${askPrice.toFixed(2)}</span> <span>${amount}</span>`;
        elements.asksList.appendChild(li);
        askPrice += (Math.random() * 10);
    }
    
    // Calculate and display spread
    const bestBid = 40000; // From our mock data
    const bestAsk = 40001; // From our mock data
    const spread = ((bestAsk - bestBid) / bestBid * 100).toFixed(4);
    elements.spreadDisplay.textContent = `Spread: ${spread}%`;
}

// Update AI analysis
function updateAIAnalysis() {
    // In a real implementation, this would call the backend AI model
    // For now, we'll generate random signals
    
    const signals = ['BUY', 'SELL', 'HOLD'];
    const randomSignal = signals[Math.floor(Math.random() * signals.length)];
    const confidence = Math.floor(Math.random() * 100);
    
    elements.aiSignal.textContent = randomSignal;
    elements.aiSignal.className = `signal-value signal-${randomSignal.toLowerCase()}`;
    elements.confidenceText.textContent = `(${confidence}%)`;
    
    // Update indicators with random values
    elements.rsiValue.textContent = (Math.random() * 100).toFixed(2);
    elements.macdValue.textContent = (Math.random() * 2 - 1).toFixed(4);
    elements.volatilityValue.textContent = (Math.random() * 5).toFixed(2);
    elements.trendValue.textContent = ['Up', 'Down', 'Neutral'][Math.floor(Math.random() * 3)];
}

// Update positions
function updatePositions() {
    // Clear existing positions
    elements.positionsList.innerHTML = '';
    
    // Add mock positions
    for (let i = 0; i < 3; i++) {
        const positionItem = document.createElement('div');
        positionItem.className = `position-item ${Math.random() > 0.5 ? 'buy' : 'sell'}`;
        
        const direction = Math.random() > 0.5 ? 'LONG' : 'SHORT';
        const symbol = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT'][i % 3];
        const size = (Math.random() * 10).toFixed(4);
        const entryPrice = (30000 + Math.random() * 20000).toFixed(2);
        const currentPrice = (30000 + Math.random() * 20000).toFixed(2);
        const pnl = ((Math.random() - 0.5) * 1000).toFixed(2);
        
        positionItem.innerHTML = `
            <div><strong>${symbol}</strong> | ${direction}</div>
            <div>Size: ${size}</div>
            <div>Entry: $${entryPrice}</div>
            <div>Current: $${currentPrice}</div>
            <div class="${pnl >= 0 ? 'positive' : 'negative'}">PnL: $${pnl}</div>
        `;
        
        elements.positionsList.appendChild(positionItem);
    }
}

// Update trade history
function updateHistory() {
    // Clear existing history
    elements.historyBody.innerHTML = '';
    
    // Add mock history
    for (let i = 0; i < 5; i++) {
        const row = document.createElement('tr');
        
        const time = new Date(Date.now() - i * 300000).toLocaleTimeString(); // 5 min intervals
        const symbol = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT'][i % 3];
        const side = Math.random() > 0.5 ? 'BUY' : 'SELL';
        const qty = (Math.random() * 5).toFixed(4);
        const price = (30000 + Math.random() * 20000).toFixed(2);
        const pnl = ((Math.random() - 0.5) * 500).toFixed(2);
        
        row.innerHTML = `
            <td>${time}</td>
            <td>${symbol}</td>
            <td>${side}</td>
            <td>${qty}</td>
            <td>$${price}</td>
            <td class="${pnl >= 0 ? 'positive' : 'negative'}">$${pnl}</td>
        `;
        
        elements.historyBody.appendChild(row);
    }
}

// Connect in demo mode
function connectDemo() {
    isDemoMode = true;
    alert('Connected to Demo Mode! All trading will be simulated.');
    updateBalance();
    startMarketUpdates();
}

// Show settings modal
function showSettingsModal() {
    elements.settingsModal.style.display = 'block';
}

// Hide settings modal
function hideSettingsModal() {
    elements.settingsModal.style.display = 'none';
}

// Save settings
function saveSettings() {
    const apiKey = elements.apiKeyInput.value;
    const secretKey = elements.secretKeyInput.value;
    isDemoMode = elements.demoCheckbox.checked;
    
    if (!apiKey || !secretKey) {
        alert('Please enter both API key and secret key');
        return;
    }
    
    // In a real implementation, this would connect to the backend
    // For now, we'll just show a success message
    alert(`Settings saved! ${isDemoMode ? 'Demo' : 'Live'} mode activated.`);
    hideSettingsModal();
    
    // Update UI
    updateBalance();
    startMarketUpdates();
}

// Load settings from local storage or backend
function loadSettings() {
    // For now, just initialize with default values
    updateBalance();
    updateMarketData();
}

// Update balance display
function updateBalance() {
    // In a real implementation, this would fetch from the backend
    // For now, we'll show a mock balance
    const balance = (30000 + Math.random() * 20000).toFixed(2);
    elements.balanceDisplay.textContent = `Balance: $${balance}`;
}

// Execute a trade
function executeTrade() {
    const direction = document.querySelector('input[name="direction"]:checked').value;
    const position = document.querySelector('input[name="position"]:checked').value;
    const quantity = elements.quantityInput.value;
    const leverage = elements.leverageInput.value;
    const orderType = elements.orderTypeSelect.value;
    
    if (!quantity || parseFloat(quantity) <= 0) {
        alert('Please enter a valid quantity');
        return;
    }
    
    // In a real implementation, this would call the backend to execute the trade
    alert(`Trade executed: ${direction} ${position} ${quantity} ${currentSymbol} at ${orderType} price with ${leverage}x leverage`);
    
    // Update UI after trade
    updatePositions();
    updateHistory();
}

// Start market data updates
function startMarketUpdates() {
    // Clear any existing interval
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    
    // Update every 5 seconds
    updateInterval = setInterval(() => {
        updateMarketData();
        updateBalance();
    }, 5000);
}

// Initialize the first update
setTimeout(() => {
    updateMarketData();
    updateBalance();
}, 1000);