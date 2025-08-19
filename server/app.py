from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/detect/<string:token_id>')
def detect_token(token_id):
    url = f'https://api.rugcheck.xyz/v1/tokens/{token_id}/report'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant data and process it from the actual API structure
            token_meta = data.get('tokenMeta', {})
            score_normalised = data.get('score_normalised', 0)  # Note: 'normalised' not 'normalized'
            risks = data.get('risks', [])
            creator_balance = data.get('creatorBalance', 0)
            total_supply = data.get('token', {}).get('supply', 1000000000000)  # Default to avoid division by zero
            total_holders = data.get('totalHolders', 0)
            total_liquidity = data.get('totalMarketLiquidity', 0)
            price = data.get('price', 0)
            
            # Calculate market cap: price * total supply
            market_cap = price * (total_supply / (10 ** data.get('token', {}).get('decimals', 6)))
            
            # Calculate creator holdings percentage
            creator_holdings_pct = (creator_balance / total_supply) * 100 if total_supply > 0 else 0
            
            # Extract anomalies from risks
            anomalies = []
            for risk in risks:
                risk_desc = risk.get('description', risk.get('name', 'Unknown risk'))
                if risk.get('value'):
                    risk_desc += f" ({risk.get('value')})"
                anomalies.append(risk_desc)
            
            if not anomalies:
                anomalies = ['No specific risks detected in API response']
            
            processed_data = {
                'token_id': token_id,
                'status': 'success',
                'name': token_meta.get('name', 'Unknown Token'),
                'symbol': token_meta.get('symbol', 'UNK'),
                'score_normalized': score_normalised,
                'risk_level': 'Fraud' if score_normalised >= 62 else 'Safe',
                'market_cap': market_cap,
                'liquidity': total_liquidity,
                'volume_24h': 0,  # Not available in this API
                'holders': total_holders,
                'creation_date': data.get('detectedAt', ''),
                'creator_holdings': creator_holdings_pct,
                'anomalies': anomalies,
                'price': price,
                'raw_data': data  # Include full raw data for debugging
            }
            
            return jsonify(processed_data)
        else:
            return jsonify({
                'token_id': token_id,
                'status': 'error',
                'error': f'API returned status code: {response.status_code}',
                'message': 'Failed to fetch token data'
            }), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({
            'token_id': token_id,
            'status': 'error',
            'error': str(e),
            'message': 'Network error occurred while fetching token data'
        }), 500
    except Exception as e:
        return jsonify({
            'token_id': token_id,
            'status': 'error',
            'error': str(e),
            'message': 'An unexpected error occurred'
        }), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )