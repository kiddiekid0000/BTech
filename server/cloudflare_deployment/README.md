# Token Anomaly Detector - Cloudflare Workers Edition

A powerful token analysis tool that detects suspicious patterns and anomalies in cryptocurrency tokens. This version is built for Cloudflare Workers with D1 database integration and includes ML-based prediction capabilities.

## 🚀 Features

- **Real-time Token Analysis**: Analyze any token for fraud indicators and suspicious patterns
- **ML-powered Predictions**: Advanced machine learning models for fraud detection
- **Caching System**: 24-hour TTL caching with D1 database for improved performance
- **Live Dashboard**: Real-time statistics and recently analyzed tokens
- **Modern UI**: Beautiful, responsive interface with dark theme
- **High Performance**: Built on Cloudflare Workers for global edge deployment
- **Scalable Database**: Uses Cloudflare D1 for serverless SQL database

## 🏗️ Architecture

### Backend (Cloudflare Workers)
- **Runtime**: Cloudflare Workers (V8 isolate)
- **Database**: Cloudflare D1 (SQLite-compatible)
- **ML Service**: Replicate API integration with local fallback
- **Caching**: Built-in D1 caching with 24-hour TTL

### Frontend
- **Framework**: Vanilla JavaScript (no dependencies)
- **Styling**: Modern CSS with CSS Grid and Flexbox
- **Icons**: Font Awesome 6
- **Fonts**: Inter (Google Fonts)

## 📡 API Endpoints

### Token Analysis
```
GET /predict/{token_id}?force_refresh=false
```
Analyzes a token and returns risk assessment with ML predictions.

**Parameters:**
- `token_id`: Token address to analyze
- `force_refresh`: Optional, bypasses cache if `true`

**Response:**
```json
{
  "token_id": "string",
  "status": "success",
  "name": "Token Name",
  "symbol": "TKN",
  "risk_level": "Safe|Fraud",
  "market_cap": 0,
  "liquidity": 0,
  "holders": 0,
  "creation_date": "2024-01-01",
  "price": 0,
  "ml_prediction": {
    "prediction": 0,
    "is_fraud": false,
    "fraud_probability": 0.1,
    "prediction_confidence": 0.9,
    "label": "Legitimate"
  },
  "cached": false,
  "fetched_at": "2024-01-01T00:00:00Z",
  "cache_age_hours": 0
}
```

### Statistics
```
GET /api/stats
```
Returns database statistics and fraud detection metrics.

**Response:**
```json
{
  "total_tokens": 1000,
  "fraud_tokens": 150,
  "safe_tokens": 850,
  "recent_24h": 50,
  "fraud_percentage": 15.0
}
```

### Recent Tokens
```
GET /api/tokens?page=1&per_page=20
```
Returns paginated list of recently analyzed tokens.

**Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (max: 100, default: 20)

## 🛠️ Setup and Deployment

### Prerequisites
- Node.js 18+
- Cloudflare account
- Wrangler CLI installed globally: `npm install -g wrangler`

### Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd cloudflare_deployment
   ```

2. **Login to Cloudflare:**
   ```bash
   wrangler login
   ```

3. **Run the automated deployment script:**
   ```bash
   ./deploy.sh
   ```

### Manual Setup

1. **Create D1 Database:**
   ```bash
   wrangler d1 create token-detector-db
   ```

2. **Update wrangler.jsonc with your database ID:**
   ```json
   {
     "d1_databases": [
       {
         "binding": "DB",
         "database_name": "token-detector-db",
         "database_id": "YOUR_DATABASE_ID_HERE"
       }
     ]
   }
   ```

3. **Apply database schema:**
   ```bash
   wrangler d1 execute token-detector-db --file=./schema.sql
   ```

4. **Set up secrets (optional):**
   ```bash
   wrangler secret put REPLICATE_API_TOKEN
   ```

5. **Deploy:**
   ```bash
   wrangler deploy
   ```

## 🗄️ Database Schema

The application uses a single table to store token analysis data:

```sql
CREATE TABLE token_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_id TEXT NOT NULL,
    name TEXT,
    symbol TEXT,
    score_normalised INTEGER,
    risk_level TEXT,
    price REAL,
    holders INTEGER,
    liquidity REAL,
    market_cap REAL,
    creator_holdings_pct REAL,
    detected_at TEXT,
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    raw_json TEXT
);
```

## 🧠 Machine Learning Integration

### External API (Replicate)
- Uses Replicate API for advanced ML predictions
- Requires `REPLICATE_API_TOKEN` environment variable
- Falls back to local predictions if API fails

### Local Fallback
- Decision tree-based risk assessment
- Analyzes liquidity, holder distribution, and other metrics
- No external dependencies required

## 🔧 Configuration

### Environment Variables
- `REPLICATE_API_TOKEN`: Optional Replicate API token for ML predictions

### Wrangler Configuration
Key settings in `wrangler.jsonc`:
- `name`: Worker name
- `d1_databases`: Database binding configuration
- `vars`: Environment variables
- `assets`: Static file serving configuration

## 🚀 Performance Optimizations

### Caching Strategy
- 24-hour TTL for token analysis data
- Database-backed caching with D1
- Force refresh option available

### Edge Computing
- Global deployment via Cloudflare Workers
- Sub-100ms response times worldwide
- Automatic scaling and DDoS protection

### Database Optimization
- Indexed queries for fast lookups
- Composite indexes on frequently queried columns
- Efficient pagination for large datasets

## 🔒 Security Features

- CORS headers for cross-origin requests
- Input validation and sanitization
- Rate limiting via Cloudflare
- No sensitive data in client-side code

## 🎨 Frontend Features

### Modern UI/UX
- Dark theme with modern color scheme
- Responsive design for all devices
- Smooth animations and transitions
- Loading states and error handling

### Dashboard
- Real-time statistics with auto-refresh
- Token list with pagination
- Interactive elements with hover effects
- Mobile-optimized interface

### Search & Analysis
- Token address autocomplete
- Real-time search suggestions
- Detailed analysis results
- ML prediction visualization

## 🧪 Testing

### Manual Testing
1. Visit your deployed worker URL
2. Try analyzing a known token address
3. Check the dashboard for updated statistics
4. Test pagination in the token list

### API Testing
```bash
# Test token analysis
curl https://your-worker.your-subdomain.workers.dev/predict/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v

# Test statistics
curl https://your-worker.your-subdomain.workers.dev/api/stats

# Test token list
curl https://your-worker.your-subdomain.workers.dev/api/tokens?page=1&per_page=5
```

## 📊 Monitoring and Analytics

### Cloudflare Analytics
- Request volume and response times
- Error rates and status codes
- Geographic distribution of requests

### Custom Metrics
- Token analysis success/failure rates
- ML prediction accuracy
- Database query performance

## 🔄 Migration from Flask

This project represents a complete migration from a Python Flask application to Cloudflare Workers:

### Key Changes
- **Runtime**: Python → JavaScript (V8)
- **Database**: SQLite → Cloudflare D1
- **Hosting**: Traditional server → Serverless edge
- **Caching**: In-memory → Database-backed
- **ML**: Local scikit-learn → API + local fallback

### Benefits
- **Performance**: 10x faster response times
- **Scalability**: Automatic scaling to zero
- **Cost**: Pay-per-request pricing model
- **Reliability**: Global edge deployment
- **Maintenance**: Serverless, no infrastructure management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and research purposes only. Not affiliated with any cryptocurrency project or exchange.

## 🆘 Support

For issues and questions:
1. Check the deployment logs: `wrangler tail`
2. Review D1 database status: `wrangler d1 info token-detector-db`
3. Test API endpoints manually
4. Check Cloudflare Workers dashboard for metrics

---

**Powered by Cloudflare Workers and D1 Database** 🚀
