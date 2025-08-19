# Pump.fun Token Anomaly Detector

A comprehensive token analysis tool designed to detect suspicious patterns, anomalies, and risk factors in cryptocurrency tokens, specifically targeting tokens from the Pump.fun ecosystem. This project provides both a Python Flask backend and a Cloudflare Workers implementation with a modern web interface.

## Test Website
```bash
https://token-detector-2.myworkspace.workers.dev/
```

## 🚀 Features

- **Real-time Token Analysis**: Analyze tokens by name, symbol, or contract address
- **Risk Assessment**: Comprehensive scoring system that classifies tokens as "Safe" or "Fraud"
- **Market Metrics**: Track market cap, liquidity, trading volume, and holder distribution
- **Anomaly Detection**: Identify suspicious patterns including:
  - High creator holdings (potential rug pull risk)
  - Low liquidity relative to market cap
  - Unusual holder concentration
  - Recent token creation with high valuations
- **Modern Web Interface**: Responsive, dark-themed UI with real-time search suggestions
- **Multiple Deployment Options**: Flask development server and Cloudflare Workers production deployment

## 🏗️ Architecture

### Backend Components

1. **Flask Application** (`app.py`)
   - RESTful API for token analysis
   - CORS-enabled for cross-origin requests
   - Comprehensive error handling

2. **Cloudflare Workers** (`token-detector-2/src/index.js`)
   - Serverless deployment option
   - Edge computing for global performance
   - Built-in static asset serving

### Frontend

- **Modern Web Interface**: Responsive single-page application
- **Real-time Search**: Auto-complete suggestions for popular tokens
- **Interactive Results**: Color-coded risk assessments and detailed metrics
- **Mobile-Friendly**: Fully responsive design

## 📊 Risk Assessment Methodology

The system evaluates tokens using multiple factors:

- **Score Normalization**: 0-100 scale where ≥62 indicates fraud risk
- **Market Analysis**: Market cap, liquidity, and trading volume ratios
- **Holder Distribution**: Creator holdings percentage and total holders
- **Temporal Factors**: Token age and creation patterns

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.7+ (for Flask backend)
- Node.js 16+ (for Cloudflare Workers)
- Modern web browser

### Flask Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask flask-cors requests
   ```

3. **Run the Flask application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser to `http://localhost:5000`
   - The web interface will be served from `templates/index.html`

### Cloudflare Workers Deployment

1. **Navigate to the Workers directory**
   ```bash
   cd token-detector-2
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Local development**
   ```bash
   npm run dev
   ```

4. **Deploy to Cloudflare**
   ```bash
   npm run deploy
   ```

## 🔧 Configuration

### Customization Options

- **Token Database**: Modify the `tokenDatabase` array in the frontend JavaScript to add more token suggestions
- **Risk Thresholds**: Adjust the fraud detection threshold (currently 62) in both backend implementations
- **API Endpoints**: The system can be adapted to use different token analysis APIs

## 📡 API Reference

### Analyze Token

**Endpoint:** `GET /detect/{token_id}`

**Description:** Analyzes a token for potential fraud indicators and returns comprehensive risk assessment.

**Parameters:**
- `token_id` (string): Token contract address, name, or symbol

**Response Format:**
```json
{
  "token_id": "string",
  "status": "success|error",
  "name": "Token Name",
  "symbol": "TKN",
  "score_normalized": 0-100,
  "risk_level": "Safe|Fraud",
  "market_cap": 0,
  "liquidity": 0,
  "volume_24h": 0,
  "holders": 0,
  "creation_date": "ISO date string",
  "creator_holdings": 0-100,
  "anomalies": ["list of detected issues"],
  "price": 0,
  "raw_data": "object"
}
```

**Example Request:**
```bash
curl https://your-domain.com/detect/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```

## 🧪 Testing

### Cloudflare Workers Tests

The project includes test suites for the Cloudflare Workers implementation:

```bash
cd token-detector-2
npm test
```

**Test Configuration:**
- Framework: Vitest with Cloudflare Workers pool
- Coverage: Unit and integration tests
- Configuration: `vitest.config.js`

## 🎨 Frontend Features

### User Interface

- **Dark Theme**: Modern, professional appearance
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Elements**: Hover effects, smooth animations
- **Loading States**: Visual feedback during API calls

### Search Functionality

- **Auto-complete**: Real-time suggestions for popular tokens
- **Multiple Input Types**: Support for names, symbols, and addresses
- **Token Resolution**: Automatic conversion of names/symbols to addresses

### Results Display

- **Risk Visualization**: Color-coded risk levels (green/yellow/red)
- **Comprehensive Metrics**: Market data, holder information, and timestamps
- **Anomaly Listing**: Clear presentation of detected risks
- **Responsive Layout**: Adapts to different screen sizes

## 🔒 Security Considerations

- **API Rate Limiting**: Inherent protection through third-party API limits
- **Input Validation**: Basic validation of token inputs
- **CORS Configuration**: Properly configured for web security
- **No Sensitive Data**: No API keys or sensitive information stored

## 🚨 Disclaimer

**Important Notice:**
- This tool is for educational and research purposes only
- Not affiliated with Pump.fun or any cryptocurrency platform
- No financial advice - always do your own research (DYOR)
- Token analysis is based on available data and may not be 100% accurate
- Cryptocurrency investments carry significant risk

## 🛣️ Roadmap

### Planned Features

- [ ] Real-time token monitoring and alerts
- [ ] Historical risk trend analysis
- [ ] Integration with additional data sources
- [ ] Advanced anomaly detection algorithms
- [ ] Portfolio risk assessment tools
- [ ] API rate limiting and authentication
- [ ] Database storage for historical analysis

### Potential Improvements

- [ ] Enhanced mobile experience
- [ ] Social sentiment analysis integration
- [ ] Automated reporting features
- [ ] Machine learning risk models
- [ ] Multi-chain support

## 📄 License

This project is available for educational and research purposes. Please ensure compliance with all applicable laws and regulations when using cryptocurrency analysis tools.

## 🤝 Contributing

Contributions are welcome! Please consider:

1. **Bug Reports**: Report issues with detailed reproduction steps
2. **Feature Requests**: Suggest new functionality with use cases
3. **Code Contributions**: Follow the existing code style and patterns
4. **Documentation**: Help improve documentation and examples

## 📞 Support

For questions, issues, or suggestions:

1. **GitHub Issues**: Use the repository issue tracker
2. **Documentation**: Refer to this README and code comments
3. **Community**: Engage with the cryptocurrency development community

---

**Built with modern web technologies for the cryptocurrency community** 🚀