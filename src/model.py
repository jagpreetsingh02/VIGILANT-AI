import pandas as pd
from sklearn.ensemble import IsolationForest
import os
import pickle


def load_data(filepath):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)

    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df


def feature_engineering(df):
    print("Feature Engineering...")

    df = df.sort_values(by=['ShopID', 'Timestamp'])

    df['time_diff'] = df.groupby(
        'ShopID')['Timestamp'].diff().dt.total_seconds()

    # Fill NaN (first transaction for each shop) with 9999
    # Using 9999 to avoid false positives on the first transaction (effectively "infinite" time passed)
    df['time_diff'] = df['time_diff'].fillna(9999)

    # 2. hour_of_day
    df['hour_of_day'] = df['Timestamp'].dt.hour

    # 3. One-Hot Encode 'Item'
    # We use pd.get_dummies. We need to join this back or just use selected features later.
    # To keep it simple, we'll store the item dummies in the dataframe.
    item_dummies = pd.get_dummies(df['Item'], prefix='Item')
    df = pd.concat([df, item_dummies], axis=1)

    return df


def train_and_predict(df):
    print("Training Isolation Forest...")

    # Select features
    # Base features
    features = ['Quantity', 'time_diff', 'hour_of_day']
    # Add Item dummy columns
    item_cols = [col for col in df.columns if col.startswith('Item_')]
    features.extend(item_cols)

    print(f"Training features: {features}")

    X = df[features]

    # Initialize model
    model = IsolationForest(contamination=0.05, random_state=42)

    # Train
    model.fit(X)

    # Save model
    model_path = 'src/model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")

    # Predict
    # -1 for outliers, 1 for inliers
    df['anomaly_pred'] = model.predict(X)

    # Decision function (scores): lower is more abnormal.
    scores = model.decision_function(X)

    # Invert scores so higher = more anomalous
    df['risk_score'] = -scores

    # Normalize to [0, 1] range for Dashboard consistency
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    df['risk_score'] = scaler.fit_transform(df[['risk_score']])

    return df


def main():
    input_path = 'data/raw/transactions.csv'
    output_path = 'data/processed/scored_transactions.csv'

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    # Load
    df = load_data(input_path)

    # Features
    df = feature_engineering(df)

    # Train & Score
    df = train_and_predict(df)

    # Save
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Scored transactions saved to {output_path}")

    # Evaluation / Inspection
    print("\n--- Model Evaluation ---")

    # Check against ground truth if available
    if 'is_fraud' in df.columns:
        from sklearn.metrics import classification_report, confusion_matrix

        # Convert prediction to 0/1 (1=fraud, 0=normal)
        # model gives -1 for fraud, 1 for normal
        y_pred = df['anomaly_pred'].apply(lambda x: 1 if x == -1 else 0)
        y_true = df['is_fraud']

        print("\nConfusion Matrix:")
        print(confusion_matrix(y_true, y_pred))

        print("\nClassification Report:")
        print(classification_report(y_true, y_pred))

    # Top 5 riskiest
    print("\n--- Top 5 Riskiest Transactions ---")
    top_risky = df.sort_values(by='risk_score', ascending=False).head(5)
    print(top_risky[['TransactionID', 'ShopID', 'is_fraud',
          'risk_score', 'Quantity', 'time_diff', 'hour_of_day']])


if __name__ == "__main__":
    main()
