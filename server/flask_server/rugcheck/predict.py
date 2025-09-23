import joblib
import numpy as np

# Load the trained model and scaler
model = joblib.load("rugcheck/randomforest_model.ckpt")
scaler = joblib.load("rugcheck/scaler.ckpt")

def extract_features_from_token_data(data):
    """Extract features from token data for model prediction"""
    features = {
        'token_supply': data.get('token', {}).get('supply', 0),
        'token_decimals': data.get('token', {}).get('decimals', 0),
        'is_initialized': data.get('token', {}).get('isInitialized', False),
        'is_mutable': data.get('tokenMeta', {}).get('mutable', False),
        'total_market_liquidity': data.get('totalMarketLiquidity', 0),
        'total_stable_liquidity': data.get('totalStableLiquidity', 0),
        'total_holders': data.get('totalHolders', 0),
        'price': data.get('price', 0),
        'top_holder_pct': data.get('topHolders', [{}])[0].get('pct', 0) if data.get('topHolders') else 0,
        'low_liquidity_risk': 'Low Liquidity' in [risk.get('name', '') for risk in data.get('risks', [])],
        'low_lp_providers_risk': 'Low amount of LP Providers' in [risk.get('name', '') for risk in data.get('risks', [])],
        'lp_quote_price': data.get('markets', [{}])[0].get('lp', {}).get('quotePrice', 0) if data.get('markets') else 0,
        'lp_base_price': data.get('markets', [{}])[0].get('lp', {}).get('basePrice', 0) if data.get('markets') else 0,
        'lp_locked_pct': data.get('markets', [{}])[0].get('lp', {}).get('lpLockedPct', 0) if data.get('markets') else 0
    }
    return features

def predict_token_risk(token_data):
    """Predict if a token is a fraud using the RandomForest model"""
    # Extract features from token data
    features = extract_features_from_token_data(token_data)
    
    # Convert to DataFrame-like structure
    feature_values = np.array([list(features.values())])
    
    # Scale features
    scaled_features = scaler.transform(feature_values)
    
    # Make prediction
    prediction = model.predict(scaled_features)[0]
    probability = model.predict_proba(scaled_features)[0][1]  # Probability of fraud class
    
    return {
        'prediction': int(prediction),
        'is_fraud': bool(prediction == 1),
        'fraud_probability': float(probability),
        'prediction_confidence': float(max(probability, 1 - probability)),
        'label': 'Fraud' if prediction == 1 else 'Legitimate'
    }
