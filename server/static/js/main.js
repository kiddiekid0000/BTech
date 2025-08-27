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
