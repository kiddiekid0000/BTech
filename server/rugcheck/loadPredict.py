import json
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# ------------------------------
# Reload trained model + scaler
# ------------------------------
model = joblib.load("randomforest_model.ckpt")
scaler = joblib.load("scaler.ckpt")

# ------------------------------
# Feature extraction (same as training)
# ------------------------------
def extract_features_from_json(data):
    features = {
        'token_supply': data.get('token', {}).get('supply', 0),
        'token_decimals': data.get('token', {}).get('decimals', 0),
        'is_initialized': data.get('token', {}).get('isInitialized', False),
        'is_mutable': data.get('tokenMeta', {}).get('mutable', False),
        'total_market_liquidity': data.get('totalMarketLiquidity', 0),
        'total_stable_liquidity': data.get('totalStableLiquidity', 0),
        'total_holders': data.get('totalHolders', 0),
        'price': data.get('price', 0),
        'normalized_score': data.get('score_normalised', 0)
    }

    # True label based on your rule
    score_norm = features['normalized_score']
    features['is_rugged'] = int(score_norm >= 63)

    if data.get('topHolders'):
        features['top_holder_pct'] = data['topHolders'][0].get('pct', 0)
    else:
        features['top_holder_pct'] = 0

    risk_names = [risk.get('name', '') for risk in data.get('risks', [])]
    features['low_liquidity_risk'] = 'Low Liquidity' in risk_names
    features['low_lp_providers_risk'] = 'Low amount of LP Providers' in risk_names

    if data.get('markets'):
        market_lp = data['markets'][0].get('lp', {})
        features['lp_quote_price'] = market_lp.get('quotePrice', 0)
        features['lp_base_price'] = market_lp.get('basePrice', 0)
        features['lp_locked_pct'] = market_lp.get('lpLockedPct', 0)
    else:
        features['lp_quote_price'] = 0
        features['lp_base_price'] = 0
        features['lp_locked_pct'] = 0

    return features

# ------------------------------
# Load rugcheck_reports.json
# ------------------------------
with open("rugcheck_reports.json", "r", encoding="utf-8") as f:
    reports = json.load(f)

all_features, mints = [], []
for entry in reports:
    mint = entry.get("mint", "")
    report_data = entry.get("report", {})
    features = extract_features_from_json(report_data)

    all_features.append(features)
    mints.append(mint)

# ------------------------------
# Prepare DataFrame
# ------------------------------
df = pd.DataFrame(all_features)
X = df.drop(["is_rugged", "normalized_score"], axis=1).astype(float)
y_true = df["is_rugged"]

# Scale features
X_scaled = scaler.transform(X)

# ------------------------------
# Predictions
# ------------------------------
y_pred = model.predict(X_scaled)

# ------------------------------
# Evaluate Accuracy
# ------------------------------
if len(set(y_true)) < 2:
    print("⚠️ All samples in rugcheck_reports.json belong to one class. Accuracy may be misleading.")
else:
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["Legit", "Fraud"]))

    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Legit','Fraud'], yticklabels=['Legit','Fraud'])
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix")
    plt.show()

print("\nAccuracy Score:", accuracy_score(y_true, y_pred))

# ------------------------------
# Show first few predictions
# ------------------------------
results_df = pd.DataFrame({
    "mint": mints,
    "score_normalised": df["normalized_score"],
    "true_label": ["Fraud" if x==1 else "Legit" for x in y_true],
    "predicted_label": ["Fraud" if x==1 else "Legit" for x in y_pred]
})
print("\nSample predictions:")
print(results_df.head())
