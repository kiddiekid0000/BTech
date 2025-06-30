import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# Specify the JSON file name
json_file_name = 'training_files.json'  # Replace with your actual file name if different

# Initialize an empty list to store transactions
all_transactions = []

# Read the JSON file line by line
with open(json_file_name, 'r', encoding='utf-8') as f:
    for line in f:
        # Remove leading/trailing whitespace and skip empty lines
        line = line.strip()
        if line:
            try:
                # Parse each line as a JSON object
                transaction = json.loads(line)
                all_transactions.append(transaction)
            except json.JSONDecodeError as e:
                print(f"Error decoding line: {line[:50]}... Error: {e}")
                continue

# Extract features and create DataFrame
transactions_list = []
for tx in all_transactions:
    try:
        fee = tx.get('fee', 0)
        compute_units_consumed = tx.get('compute_units_consumed', 0)
        block_timestamp = pd.to_datetime(tx.get('block_timestamp', '1970-01-01 00:00:00 UTC')).timestamp()
        num_accounts = len(tx.get('txn_accounts', []))
        sol_value = float(tx.get('sol_value', fee))
        program_id = tx.get('program_id', 'Unknown')
        status = 1 if tx.get('status', 'Unknown') == 'Success' else 0

        transactions_list.append({
            'fee': fee,
            'compute_units_consumed': compute_units_consumed,
            'block_timestamp': block_timestamp,
            'num_accounts': num_accounts,
            'sol_value': sol_value,
            'program_id': program_id,
            'status': status
        })
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error processing transaction {tx.get('signature', 'Unknown')}: {e}")
        continue

# Create DataFrame
df = pd.DataFrame(transactions_list)

# Encode categorical variable (program_id)
le = LabelEncoder()
df['program_id_encoded'] = le.fit_transform(df['program_id'])

# Define features and target
X = df[['fee', 'compute_units_consumed', 'block_timestamp', 'num_accounts', 'sol_value', 'program_id_encoded']]
y = df['status']

# Train and predict only if enough data
if len(X) > 1:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))
else:
    print("Warning: Insufficient data (only 1 transaction). Training skipped. Add more data to improve model.")

# Optional: Feature importance (if trained)
if len(X) > 1:
    importances = rf.feature_importances_
    print("Feature Importances:", dict(zip(X.columns, importances)))