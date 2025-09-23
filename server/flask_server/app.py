from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
from sqlalchemy import select, desc
from typing import cast
from rugcheck.predict import predict_token_risk
from db import SessionLocal, TokenReport, init_db

app = Flask(__name__)
CORS(app)
init_db()

@app.route('/detect/<string:token_id>')
def detect_token(token_id):
    # Check cache: return latest record within TTL
    TTL_HOURS = 24
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=TTL_HOURS)

    with SessionLocal() as session:
        stmt = (
            select(TokenReport)
            .where(TokenReport.token_id == token_id)
            .order_by(desc(TokenReport.fetched_at))
            .limit(1)
        )
    row = session.execute(stmt).scalars().first()
    report = None
    if TokenReport is not None:
        report = cast(TokenReport, row)
    else:
        report = cast(None, row)
    if report is not None and report.fetched_at is not None and report.fetched_at >= cutoff:
            return jsonify({
                'token_id': token_id,
                'status': 'success',
        'name': report.name or 'Unknown Token',
        'symbol': report.symbol or 'UNK',
        'risk_level': report.risk_level or 'Safe',
        'market_cap': report.market_cap or 0,
        'liquidity': report.liquidity or 0,
        'holders': report.holders or 0,
        'creation_date': report.detected_at or '',
        'price': report.price or 0,
        'raw_data': json.loads(report.raw_json) if (report.raw_json is not None and len(report.raw_json) > 0) else {}
            })

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
            
            # Removed anomalies extraction
            
            processed_data = {
                'token_id': token_id,
                'status': 'success',
                'name': token_meta.get('name', 'Unknown Token'),
                'symbol': token_meta.get('symbol', 'UNK'),
                'risk_level': 'Fraud' if score_normalised >= 62 else 'Safe',
                'market_cap': market_cap,
                'liquidity': total_liquidity,

                'holders': total_holders,
                'creation_date': data.get('detectedAt', ''),

                'price': price,
                'raw_data': data  # Include full raw data for debugging
            }
            
            # Persist for history and future cache hits
            try:
                with SessionLocal() as session:
                    record = TokenReport(
                        token_id=token_id,
                        name=processed_data['name'],
                        symbol=processed_data['symbol'],
                        score_normalised=score_normalised,
                        risk_level=processed_data['risk_level'],
                        price=price,
                        holders=total_holders,
                        liquidity=total_liquidity,
                        market_cap=market_cap,
                        creator_holdings_pct=creator_holdings_pct,
                        detected_at=data.get('detectedAt', ''),
                        raw_json=json.dumps(data)
                    )
                    session.add(record)
                    session.commit()
            except Exception:
                # Don't fail the request if DB write fails
                pass

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

@app.route('/predict/<string:token_id>')
def predict_token(token_id):
    url = f'https://api.rugcheck.xyz/v1/tokens/{token_id}/report'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Use our ML model to predict risk
            prediction_result = predict_token_risk(data)
            
            # Combine API data with our prediction
            processed_data = {
                'token_id': token_id,
                'status': 'success',
                'name': data.get('tokenMeta', {}).get('name', 'Unknown Token'),
                'symbol': data.get('tokenMeta', {}).get('symbol', 'UNK'),
                'ml_prediction': prediction_result,
                'price': data.get('price', 0),
            }
            
            return jsonify(processed_data)
        else:
            return jsonify({
                'token_id': token_id,
                'status': 'error',
                'error': f'API returned status code: {response.status_code}',
                'message': 'Failed to fetch token data'
            }), response.status_code

    except Exception as e:
        return jsonify({
            'token_id': token_id,
            'status': 'error',
            'error': str(e),
            'message': 'An error occurred during prediction'
        }), 500

@app.route('/api/tokens')
def get_tokens():
    """Get recent tokens from database with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Limit per_page to prevent abuse
    per_page = min(per_page, 100)
    
    with SessionLocal() as session:
        # Get total count
        total = session.query(TokenReport).count()
        
        # Get paginated results, ordered by most recent
        tokens = (
            session.query(TokenReport)
            .order_by(desc(TokenReport.fetched_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        
        # Format tokens for JSON response
        token_list = []
        for token in tokens:
            token_data = {
                'id': token.id,
                'token_id': token.token_id,
                'name': token.name or 'Unknown',
                'symbol': token.symbol or 'UNK',
                'risk_level': token.risk_level or 'Safe',
                'score_normalised': token.score_normalised or 0,
                'price': token.price or 0,
                'market_cap': token.market_cap or 0,
                'liquidity': token.liquidity or 0,
                'holders': token.holders or 0,
                'creator_holdings_pct': token.creator_holdings_pct or 0,
                'detected_at': token.detected_at,
                'fetched_at': token.fetched_at.isoformat() if token.fetched_at else None,
            }
            token_list.append(token_data)
        
        return jsonify({
            'tokens': token_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    with SessionLocal() as session:
        total_tokens = session.query(TokenReport).count()
        
        # Count by risk level
        fraud_count = session.query(TokenReport).filter(TokenReport.risk_level == 'Fraud').count()
        safe_count = session.query(TokenReport).filter(TokenReport.risk_level == 'Safe').count()
        
        # Get recent activity (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_count = session.query(TokenReport).filter(TokenReport.fetched_at >= cutoff).count()
        
        return jsonify({
            'total_tokens': total_tokens,
            'fraud_tokens': fraud_count,
            'safe_tokens': safe_count,
            'recent_24h': recent_count,
            'fraud_percentage': round((fraud_count / total_tokens * 100) if total_tokens > 0 else 0, 1)
        })

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )