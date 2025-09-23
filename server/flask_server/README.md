# Pump.fun Token Anomaly Detector

A comprehensive token analysis tool designed to detect suspicious patterns, anomalies, and risk factors in cryptocurrency tokens, specifically targeting tokens from the Pump.fun ecosystem. This project provides both a Python Flask backend and a Cloudflare Workers implementation with a modern web interface.

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

## 📊 Risk Assessment Methodology

The system evaluates tokens using multiple factors:

- **Score Normalization**: 0-100 scale where ≥62 indicates fraud risk
- **Market Analysis**: Market cap, liquidity, and trading volume ratios
- **Holder Distribution**: Creator holdings percentage and total holders
- **Temporal Factors**: Token age and creation patterns

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

## 🎨 Frontend Features

### User Interface

- **Dark Theme**: Modern, professional appearance
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Elements**: Hover effects, smooth animations
- **Loading States**: Visual feedback during API calls

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
- No financial advice - always do your own research
- Token analysis is based on available data and may not be 100% accurate
- Cryptocurrency investments carry significant risk

---

**Built with modern web technologies for the cryptocurrency community** 🚀