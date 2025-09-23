import json
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
import seaborn as sns
import matplotlib.pyplot as plt

# Step 1: Feature Extraction
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

    # Dynamically set the 'is_rugged' label based on the new rule
    score_norm = features['normalized_score']
    # 'is_rugged' is True (1) if score is 63 or higher, otherwise False (0)
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

# Step 2: Load and Process All JSON files from a folder
data_folder = 'data'
all_extracted_features = []
processed_files_count = 0

if not os.path.exists(data_folder):
    print(f"Error: The folder '{data_folder}' was not found.")
else:
    for filename in os.listdir(data_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(data_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    features = extract_features_from_json(json_data)
                    all_extracted_features.append(features)
                    processed_files_count += 1
            except json.JSONDecodeError:
                print(f"Skipping '{filename}' due to JSON decoding error.")
            except Exception as e:
                print(f"Skipping '{filename}' due to an unexpected error: {e}")

    if not all_extracted_features:
        print("No valid JSON files were found or processed. Please check your data folder.")
    else:
        print(f"Successfully processed {processed_files_count} JSON files.")

        df = pd.DataFrame(all_extracted_features)

        # Step 3: Separate features (X) and target (y)
        # Separate features (X) and target (y)
        # The 'is_rugged' column is created from 'normalized_score'
        # The 'normalized_score' column itself must be dropped from the features
        X = df.drop(['is_rugged', 'normalized_score'], axis=1)
        y = df['is_rugged']

        X = X.astype(float)
        y = y.astype(int)

        # Step 4: Handle Imbalance with SMOTE
        if y.nunique() > 1 and len(y[y == 1]) != len(y[y == 0]):
            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X, y)
        else:
            X_resampled, y_resampled = X, y

        print("\nOriginal dataset shape:", y.value_counts())
        print("Resampled dataset shape:", y_resampled.value_counts())
        print("-" * 50)

        # Step 5: Split data and apply Feature Scaling
        X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Step 6: Train and Evaluate the model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)

        print("\nNew Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Legit', 'Fraud']))

        conf_matrix = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Legit', 'Fraud'], yticklabels=['Legit', 'Fraud'])
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.title('Confusion Matrix')
        plt.show()

import joblib

# Save model and scaler to files
joblib.dump(model, "randomforest_model.ckpt")
joblib.dump(scaler, "scaler.ckpt")

print("✅ Model and Scaler saved as randomforest_model.ckpt and scaler.ckpt")
