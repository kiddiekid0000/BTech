import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report
import joblib

# Load data
with open('block_000000000000.json') as f:
    data = [json.loads(line) for line in f]

records = []
for tx in data:
    records.append({
        'fee': tx['fee'],
        'compute_units_consumed': tx['compute_units_consumed'],
        'num_accounts': len(tx['txn_accounts']),
        'num_signers': sum(1 for acc in tx['txn_accounts'] if acc['signer']),
        'num_writable': sum(1 for acc in tx['txn_accounts'] if acc['writable']),
        'instruction_length': len(tx['instruction_data'])
    })

# Create dataframe
df = pd.DataFrame(records)

# Create heuristic anomaly label using multiple conditions
df['is_anomaly'] = ((df['fee'] > df['fee'].quantile(0.98)) | (df['compute_units_consumed'] > df['compute_units_consumed'].quantile(0.98))).astype(int)

# Features and target
X = df.drop(['is_anomaly'], axis=1)
y = df['is_anomaly']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# Train Random Forest
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
preds = clf.predict(X_test)
print(classification_report(y_test, preds))

# Cross-validation scores
scores = cross_val_score(clf, X, y, cv=5)
print("Cross-validation accuracy:", scores.mean())

# Export model
joblib.dump(clf, 'custom.model')
