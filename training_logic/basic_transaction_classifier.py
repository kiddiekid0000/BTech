import json
import pandas as pd
import glob
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# List all JSON files in the "transactions" folder
json_files = glob.glob('transactions/*.json')

# Initialize an empty list to store all transactions
all_transactions = []

# Read each JSON file and extract transactions
for json_file in json_files:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_transactions.extend(data['data']['transactions'])

# ... rest of the code for feature extraction, model training, etc.

# Extract features from each transaction
transactions_list = []
for tx in all_transactions:
    try:
        fee = tx['fee']
        sol_value = float(tx['sol_value'])
        num_instructions = len(tx['parsedInstruction'])
        status = 1 if tx['status'] == 'Success' else 0
        transactions_list.append({
            'fee': fee,
            'sol_value': sol_value,
            'num_instructions': num_instructions,
            'status': status
        })
    except KeyError as e:
        print(f"Missing key {e} in transaction {tx.get('txHash', 'Unknown')}")
        continue
    except ValueError as e:
        print(f"Error converting sol_value in transaction {tx.get('txHash', 'Unknown')}: {e}")
        continue

# Create a DataFrame from the extracted features
df = pd.DataFrame(transactions_list)

# Split into features (X) and target (y)
X = df[['fee', 'sol_value', 'num_instructions']]
y = df['status']

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest classifier
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Predict on the test set
y_pred = rf.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))