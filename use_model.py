import joblib
import pandas as pd
import numpy as np

def load_and_use_model():
    """
    Load the custom.model and demonstrate how to use it for predictions
    """
    try:
        # Load the trained model
        model = joblib.load('training_output/custom.model')
        print("Model loaded successfully!")
        
        # Example transaction data (replace with your actual data)
        sample_transactions = [
             {
                'fee': 500,  # ✅ Modest fee, standard for typical user TX
                'compute_units_consumed': 180000,  # ✅ Well within normal range
                'num_accounts': 4,  # ✅ Minimal account interaction
                'num_signers': 2,  # ✅ Two signers — likely user + system/program
                'num_writable': 2,  # ✅ Only modifying essential accounts
                'instruction_length': 5  # ✅ Short, readable, and simple instruction list
            },
            {
                'fee': 90000,  # 🚨 Extremely high fee, possibly to front-run
                'compute_units_consumed': 1400000,  # 🚨 Way above typical cap (heavy program logic)
                'num_accounts': 22,  # 🚨 Lots of accounts involved — possibly draining wallets/liquidity
                'num_signers': 1,  # Low signer count — centralized control
                'num_writable': 16,  # 🚨 Writing to many accounts — changing states or balances
                'instruction_length': 80  # 🚨 Complex logic — possibly obfuscated malicious code
            },
            {
                'fee': 500,
                'compute_units_consumed': 180000,
                'num_accounts': 4,
                'num_signers': 1,
                'num_writable': 2,
                'instruction_length': 5
            },
            {
                'fee': 800,
                'compute_units_consumed': 220000,
                'num_accounts': 5,
                'num_signers': 2,
                'num_writable': 3,
                'instruction_length': 8
            },
            {
                'fee': 400,
                'compute_units_consumed': 150000,
                'num_accounts': 3,
                'num_signers': 1,
                'num_writable': 2,
                'instruction_length': 4
            },
            {
                'fee': 600,
                'compute_units_consumed': 210000,
                'num_accounts': 6,
                'num_signers': 2,
                'num_writable': 3,
                'instruction_length': 7
            },
            {
                'fee': 700,
                'compute_units_consumed': 250000,
                'num_accounts': 5,
                'num_signers': 2,
                'num_writable': 3,
                'instruction_length': 6
            },
            {
                'fee': 300,
                'compute_units_consumed': 120000,
                'num_accounts': 4,
                'num_signers': 1,
                'num_writable': 2,
                'instruction_length': 3
            },
            {
                'fee': 1000,
                'compute_units_consumed': 270000,
                'num_accounts': 6,
                'num_signers': 2,
                'num_writable': 3,
                'instruction_length': 9
            },
            {
                'fee': 450,
                'compute_units_consumed': 160000,
                'num_accounts': 3,
                'num_signers': 1,
                'num_writable': 1,
                'instruction_length': 5
            },
            {
                'fee': 750,
                'compute_units_consumed': 230000,
                'num_accounts': 5,
                'num_signers': 2,
                'num_writable': 3,
                'instruction_length': 6
            },
            {
                'fee': 550,
                'compute_units_consumed': 190000,
                'num_accounts': 4,
                'num_signers': 1,
                'num_writable': 2,
                'instruction_length': 5
            }
        ]
        
        # Convert to DataFrame
        df = pd.DataFrame(sample_transactions)
        
        # Make predictions
        predictions = model.predict(df)
        probabilities = model.predict_proba(df)
        
        # Display results
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            print(f"\nTransaction {i+1}:")
            print(f"  Features: {dict(df.iloc[i])}")
            print(f"  Is Anomaly: {'Yes' if pred == 1 else 'No'}")
            print(f"  Normal Probability: {prob[0]:.3f}")
            print(f"  Anomaly Probability: {prob[1]:.3f}")
            
    except FileNotFoundError:
        print("Error: custom.model file not found. Please run custom_model.py first to generate the model.")
    except Exception as e:
        print(f"Error loading model: {e}")

def predict_single_transaction(fee, compute_units, num_accounts, num_signers, num_writable, instruction_length):
    """
    Predict if a single transaction is anomalous
    """
    try:
        model = joblib.load('training_output/custom.model')
        
        # Create DataFrame with the transaction
        transaction_data = pd.DataFrame([{
            'fee': fee,
            'compute_units_consumed': compute_units,
            'num_accounts': num_accounts,
            'num_signers': num_signers,
            'num_writable': num_writable,
            'instruction_length': instruction_length
        }])
        
        # Make prediction
        prediction = model.predict(transaction_data)[0]
        probability = model.predict_proba(transaction_data)[0]
        
        return {
            'is_anomaly': bool(prediction),
            'normal_probability': probability[0],
            'anomaly_probability': probability[1]
        }
        
    except Exception as e:
        print(f"Error making prediction: {e}")
        return None

if __name__ == "__main__":
    print("=== Custom Model Usage Demo ===")
    load_and_use_model()
    
    # print("\n=== Single Transaction Prediction ===")
    # # Example single prediction
    # result = predict_single_transaction(
    #     fee=25000,
    #     compute_units=500000,
    #     num_accounts=8,
    #     num_signers=3,
    #     num_writable=5,
    #     instruction_length=20
    # )
    
    # if result:
    #     print(f"Single transaction result: {result}")
