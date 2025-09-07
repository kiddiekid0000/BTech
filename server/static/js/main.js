// Mock token database for suggestions and analysis
const tokenDatabase = [
    { name: "Pepe", symbol: "PEPE", address: "0x6982508145454Ce325dDbE47a25d4ec3d2311933" },
    { name: "Shiba Inu", symbol: "SHIB", address: "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE" },
    { name: "Dogecoin", symbol: "DOGE", address: "0xbA2aE424d960c26247Dd6c32edC70B295c744C43" },
    { name: "SafeMoon", symbol: "SAFEMOON", address: "0x8076c74c5e3f5852037f31ff0093eeb8c8add8d3" },
    { name: "Floki Inu", symbol: "FLOKI", address: "0xcf0c122c6b73ff809c693db761e7baebe62b6a2e" },
];

// DOM elements
const tokenInput = document.getElementById('tokenInput');
const searchSuggestions = document.getElementById('searchSuggestions');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('resultsSection');
const tokenName = document.getElementById('tokenName');
const tokenSymbol = document.getElementById('tokenSymbol');
const riskScore = document.getElementById('riskScore');
const riskValue = document.getElementById('riskValue');
const marketCap = document.getElementById('marketCap');
const liquidity = document.getElementById('liquidity');
const holders = document.getElementById('holders');
const creationDate = document.getElementById('creationDate');
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navLinks = document.getElementById('navLinks');

// Mobile menu toggle
mobileMenuBtn.addEventListener('click', () => {
    navLinks.classList.toggle('active');
});

// Search suggestions
tokenInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    
    if (query.length < 2) {
        searchSuggestions.style.display = 'none';
        return;
    }

    const matches = tokenDatabase.filter(token => 
        token.name.toLowerCase().includes(query) || 
        token.symbol.toLowerCase().includes(query) ||
        token.address.toLowerCase().includes(query)
    );

    if (matches.length > 0) {
        searchSuggestions.innerHTML = matches.map(token => `
            <div class="suggestion-item" data-token='${JSON.stringify(token)}'>
                <div class="suggestion-name">${token.name}</div>
                <div class="suggestion-symbol">${token.symbol}</div>
            </div>
        `).join('');
        searchSuggestions.style.display = 'block';
    } else {
        searchSuggestions.style.display = 'none';
    }
});

// Handle suggestion clicks
searchSuggestions.addEventListener('click', (e) => {
    const suggestionItem = e.target.closest('.suggestion-item');
    if (suggestionItem) {
        const token = JSON.parse(suggestionItem.dataset.token);
        tokenInput.value = `${token.name} (${token.symbol})`;
        searchSuggestions.style.display = 'none';
    }
});

// Hide suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.token-search')) {
        searchSuggestions.style.display = 'none';
    }
});

// Token anomaly detection API call
async function analyzeToken(tokenQuery) {
    try {
        // For this demo, we'll use the token query as the token ID
        // In a real implementation, you might need to resolve token names to IDs first
        const tokenId = extractTokenId(tokenQuery);
        
        const response = await fetch(`/detect/${tokenId}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            // Transform API response to match frontend expectations
            return {
                name: data.name,
                symbol: data.symbol,
                marketCap: data.market_cap || 0,
                liquidity: data.liquidity || 0,
                holders: data.holders || 0,
                creationDate: data.creation_date ? new Date(data.creation_date) : new Date(),
                riskLevel: data.risk_level === 'Fraud' ? 'high' : 'low',
                apiStatus: 'success'
            };
        } else {
            // Return error information
            return {
                name: "Error",
                symbol: "ERR",
                marketCap: 0,
                liquidity: 0,
                holders: 0,
                creationDate: new Date(),
                riskLevel: 'medium',
                apiStatus: 'error',
                error: data.error
            };
        }
    } catch (error) {
        console.error('Error analyzing token:', error);
        return {
            name: "Network Error",
            symbol: "ERR",
            marketCap: 0,
            liquidity: 0,
            holders: 0,
            creationDate: new Date(),
            riskLevel: 'medium',
            apiStatus: 'error',
            error: error.message
        };
    }
}

// Extract token ID from user input
function extractTokenId(tokenQuery) {
    // Check if it's already a token address (starts with alphanumeric and has appropriate length)
    if (/^[a-zA-Z0-9]{32,}$/.test(tokenQuery.trim())) {
        return tokenQuery.trim();
    }
    
    // Check if it's in the known token database
    const knownToken = tokenDatabase.find(token => 
        tokenQuery.toLowerCase().includes(token.name.toLowerCase()) ||
        tokenQuery.toLowerCase().includes(token.symbol.toLowerCase())
    );
    
    if (knownToken) {
        return knownToken.address;
    }
    
    // If not found, return the query as-is (API will handle it)
    return tokenQuery.trim();
}

// Format currency
function formatCurrency(amount) {
    if (amount >= 1000000) {
        return `$${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
        return `$${(amount / 1000).toFixed(1)}K`;
    } else {
        return `$${amount.toLocaleString()}`;
    }
}

// Format date
function formatDate(date) {
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Analyze token
analyzeBtn.addEventListener('click', async () => {
    const query = tokenInput.value.trim();
    
    if (!query) {
        alert('Please enter a token name, symbol, or contract address.');
        return;
    }

    // Show loading state
    const originalText = analyzeBtn.innerHTML;
    analyzeBtn.innerHTML = '<div class="loading"></div> Analyzing...';
    analyzeBtn.disabled = true;

    try {
        const results = await analyzeToken(query);

        // Update token info
        tokenName.textContent = results.name;
        tokenSymbol.textContent = results.symbol;

        // Update risk display
        const riskClass = results.riskLevel === 'high' ? 'high' : 'low';
        const displayRisk = results.riskLevel === 'high' ? 'Fraud' : 'Legit';
        
        riskScore.className = `risk-score ${riskClass}`;
        riskValue.textContent = displayRisk;

        // Update metrics
        marketCap.textContent = formatCurrency(results.marketCap);
        liquidity.textContent = formatCurrency(results.liquidity);
        holders.textContent = results.holders.toLocaleString();
        creationDate.textContent = formatDate(results.creationDate);

        // Show results
        resultsSection.classList.remove('hidden');
    } catch (error) {
        console.error('Error during analysis:', error);
        alert('An error occurred while analyzing the token. Please try again.');
    } finally {
        // Reset button
        analyzeBtn.innerHTML = originalText;
        analyzeBtn.disabled = false;
    }
});

// Handle Enter key in input
tokenInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        analyzeBtn.click();
    }
});

// Dashboard functionality
let currentPage = 1;
let totalPages = 1;
let refreshInterval;

// DOM elements for dashboard
const totalTokensEl = document.getElementById('totalTokens');
const fraudTokensEl = document.getElementById('fraudTokens');
const safeTokensEl = document.getElementById('safeTokens');
const recentTokensEl = document.getElementById('recentTokens');
const fraudPercentageEl = document.getElementById('fraudPercentage');
const fraudBarFillEl = document.getElementById('fraudBarFill');
const lastUpdatedEl = document.getElementById('lastUpdated');
const refreshIconEl = document.getElementById('refreshIcon');
const tokenListEl = document.getElementById('tokenList');
const refreshTokensBtn = document.getElementById('refreshTokensBtn');
const paginationControls = document.getElementById('paginationControls');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');
const pageInfoEl = document.getElementById('pageInfo');

// Load dashboard data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadTokens();
    startAutoRefresh();
});

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        // Animate numbers
        animateNumber(totalTokensEl, stats.total_tokens);
        animateNumber(fraudTokensEl, stats.fraud_tokens);
        animateNumber(safeTokensEl, stats.safe_tokens);
        animateNumber(recentTokensEl, stats.recent_24h);
        
        // Update fraud percentage
        fraudPercentageEl.textContent = `${stats.fraud_percentage}%`;
        fraudBarFillEl.style.width = `${stats.fraud_percentage}%`;
        
        // Update last updated time
        lastUpdatedEl.textContent = `Updated ${new Date().toLocaleTimeString()}`;
        
    } catch (error) {
        console.error('Error loading stats:', error);
        lastUpdatedEl.textContent = 'Error loading data';
    }
}

// Load tokens list
async function loadTokens(page = 1) {
    try {
        // Show loading
        tokenListEl.innerHTML = `
            <div class="loading-placeholder">
                <div class="loading-spinner"></div>
                <p>Loading tokens...</p>
            </div>
        `;
        
        const response = await fetch(`/api/tokens?page=${page}&per_page=10`);
        const data = await response.json();
        
        if (data.tokens && data.tokens.length > 0) {
            // Display tokens
            tokenListEl.innerHTML = data.tokens.map(token => createTokenItem(token)).join('');
            
            // Update pagination
            currentPage = data.pagination.page;
            totalPages = data.pagination.pages;
            updatePagination();
            
            // Add click handlers to token items
            document.querySelectorAll('.token-item').forEach(item => {
                item.addEventListener('click', () => {
                    const tokenId = item.dataset.tokenId;
                    if (tokenId) {
                        // Fill the search input and analyze
                        tokenInput.value = tokenId;
                        analyzeBtn.click();
                        
                        // Scroll to results
                        document.querySelector('#resultsSection').scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
            
        } else {
            tokenListEl.innerHTML = `
                <div class="loading-placeholder">
                    <i class="fas fa-coins" style="font-size: 2rem; margin-bottom: 1rem; color: var(--text-muted);"></i>
                    <p>No tokens found in database</p>
                    <small>Analyze some tokens to see them here</small>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error loading tokens:', error);
        tokenListEl.innerHTML = `
            <div class="loading-placeholder">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem; color: var(--danger-color);"></i>
                <p>Error loading tokens</p>
                <small>Please try again</small>
            </div>
        `;
    }
}

// Create token item HTML
function createTokenItem(token) {
    const riskClass = token.risk_level === 'Fraud' ? 'fraud' : 'safe';
    const riskText = token.risk_level === 'Fraud' ? 'Fraud' : 'Safe';
    const avatarText = token.symbol ? token.symbol.substring(0, 2).toUpperCase() : 'UN';
    const timeAgo = getTimeAgo(new Date(token.fetched_at));
    
    return `
        <div class="token-item" data-token-id="${token.token_id}">
            <div class="token-main-info">
                <div class="token-avatar">${avatarText}</div>
                <div class="token-details">
                    <h4>${token.name}</h4>
                    <div class="token-symbol">${token.symbol}</div>
                </div>
            </div>
            
            <div class="token-metrics">
                <div class="token-metric">
                    <div class="token-metric-label">Market Cap</div>
                    <div class="token-metric-value">${formatCurrency(token.market_cap)}</div>
                </div>
                <div class="token-metric">
                    <div class="token-metric-label">Holders</div>
                    <div class="token-metric-value">${token.holders.toLocaleString()}</div>
                </div>
                <div class="token-metric">
                    <div class="token-metric-label">Analyzed</div>
                    <div class="token-metric-value">${timeAgo}</div>
                </div>
            </div>
            
            <div class="token-risk ${riskClass}">${riskText}</div>
        </div>
    `;
}

// Update pagination controls
function updatePagination() {
    if (totalPages <= 1) {
        paginationControls.style.display = 'none';
        return;
    }
    
    paginationControls.style.display = 'flex';
    pageInfoEl.textContent = `Page ${currentPage} of ${totalPages}`;
    prevPageBtn.disabled = currentPage <= 1;
    nextPageBtn.disabled = currentPage >= totalPages;
}

// Pagination event handlers
prevPageBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        loadTokens(currentPage - 1);
    }
});

nextPageBtn.addEventListener('click', () => {
    if (currentPage < totalPages) {
        loadTokens(currentPage + 1);
    }
});

// Refresh tokens button
refreshTokensBtn.addEventListener('click', () => {
    loadTokens(currentPage);
    loadStats();
    
    // Add pulse effect
    refreshTokensBtn.classList.add('pulse');
    setTimeout(() => refreshTokensBtn.classList.remove('pulse'), 1000);
});

// Auto refresh functionality
function startAutoRefresh() {
    // Refresh stats every 30 seconds
    refreshInterval = setInterval(() => {
        loadStats();
    }, 30000);
    
    // Refresh tokens every 2 minutes
    setInterval(() => {
        loadTokens(currentPage);
    }, 120000);
}

// Stop auto refresh (if needed)
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// Animate number counting
function animateNumber(element, targetValue) {
    const startValue = 0;
    const duration = 1000;
    const startTime = Date.now();
    
    function updateNumber() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOut);
        
        element.textContent = currentValue.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        } else {
            element.textContent = targetValue.toLocaleString();
        }
    }
    
    updateNumber();
}

// Get time ago string
function getTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
