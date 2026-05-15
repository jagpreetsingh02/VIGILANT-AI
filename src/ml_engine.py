import pandas as pd
import numpy as np
import hashlib
import streamlit as st

def _assign_district(shop_id):
    """Deterministically assigns a district based on ShopID hash."""
    hash_val = int(hashlib.md5(shop_id.encode()).hexdigest(), 16)
    districts = ['North', 'South', 'East', 'West']
    return districts[hash_val % 4]

def _get_variance_multiplier(shop_id, txn_id):
    """
    Generates deterministic variance (0.85-1.15) based on transaction hash.
    Ensures same transaction always gets same variance.
    """
    hash_input = f"{shop_id}_{txn_id}".encode()
    hash_val = int(hashlib.md5(hash_input).hexdigest(), 16)
    # Map to 0.85-1.15 range
    variance = 0.85 + (hash_val % 1000) / 3333.0
    return variance

@st.cache_data(show_spinner=False)
def detect_fraud(df):
    """
    Granular Risk Scoring with Continuous 0-100 Scale.
    Uses weighted severity calculations with deterministic variance.
    """
    if df.empty:
        return df

    # --- STEP 1: ROBUST TYPE CONVERSION ---
    df = df.copy()
    
    # Force datetime conversion
    if not pd.api.types.is_datetime64_any_dtype(df['Timestamp']):
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    
    # Force numeric conversions
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    df['Quantity_kg'] = pd.to_numeric(df['Quantity_kg'], errors='coerce').fillna(0)
    
    # Extract hour
    df['Hour'] = df['Timestamp'].dt.hour
    df['Date'] = df['Timestamp'].dt.date
    
    # Assign District if missing
    if 'District' not in df.columns:
        df['District'] = df['ShopID'].apply(_assign_district)

    # Calculate deterministic variance for each transaction
    df['Variance'] = df.apply(
        lambda row: _get_variance_multiplier(row['ShopID'], row['TransactionID']), 
        axis=1
    )

    # Initialize scoring
    risk_score = np.zeros(len(df))
    flag_lists = [[] for _ in range(len(df))]

    # --- STEP 2: GRANULAR ANOMALY SCORING ---
    
    # 1. VELOCITY ANOMALY (Weight: 25, Max: 75)
    df['txn_marker'] = 1
    hourly_counts = df.groupby(['ShopID', 'Date', 'Hour'])['txn_marker'].transform('count')
    
    velocity_percentile_95 = hourly_counts.quantile(0.95)
    hard_floor_velocity = 20
    velocity_threshold = min(velocity_percentile_95, hard_floor_velocity)
    
    velocity_mask = (hourly_counts > velocity_threshold).values
    # Severity: how many times over threshold (capped at 3x)
    velocity_severity = np.where(
        velocity_mask,
        np.minimum((hourly_counts.values / velocity_threshold) - 1, 3.0),
        0
    )
    velocity_score = 25 * velocity_severity * df['Variance'].values
    risk_score += velocity_score
    
    for idx in np.where(velocity_mask)[0]:
        flag_lists[idx].append('High Velocity')

    # 2. PRICE INFLATION (Weight: 30, Max: 90)
    item_medians = df.groupby('Item_Type')['Amount'].transform('median')
    price_mask = (df['Amount'] > (item_medians * 1.5)).values
    # Severity: price deviation ratio (capped at 3x)
    price_severity = np.where(
        price_mask,
        np.minimum((df['Amount'].values / item_medians.values) - 1, 3.0),
        0
    )
    price_score = 30 * price_severity * df['Variance'].values
    risk_score += price_score
    
    for idx in np.where(price_mask)[0]:
        flag_lists[idx].append('Price Inflation')

    # 3. HOARDING - RICE (Weight: 28, Max: 84)
    rice_mask = ((df['Item_Type'] == 'Rice') & (df['Quantity_kg'] > 45)).values
    rice_severity = np.where(
        rice_mask,
        np.minimum((df['Quantity_kg'].values / 45) - 1, 3.0),
        0
    )
    rice_score = 28 * rice_severity * df['Variance'].values
    risk_score += rice_score
    
    for idx in np.where(rice_mask)[0]:
        flag_lists[idx].append('Bulk Hoarding (Rice)')
    
    # HOARDING - SALT (Weight: 28, Max: 84)
    salt_mask = ((df['Item_Type'] == 'Salt') & (df['Quantity_kg'] > 2)).values
    salt_severity = np.where(
        salt_mask,
        np.minimum((df['Quantity_kg'].values / 2) - 1, 3.0),
        0
    )
    salt_score = 28 * salt_severity * df['Variance'].values
    risk_score += salt_score
    
    for idx in np.where(salt_mask)[0]:
        flag_lists[idx].append('Hoarding (Salt)')

    # 4. TIME ANOMALY (Weight: 18, Max: 54)
    unique_hours = df['Hour'].nunique()
    
    if unique_hours > 6:
        time_mask = ((df['Hour'] < 7) | (df['Hour'] > 21)).values
        # Severity: distance from business hours (14:00 as midpoint)
        time_severity = np.where(
            time_mask,
            np.abs(df['Hour'].values - 14) / 14.0,
            0
        )
        time_score = 18 * time_severity * df['Variance'].values
        risk_score += time_score
        
        for idx in np.where(time_mask)[0]:
            flag_lists[idx].append('Non-Business Hours')

    # 5. CARD MISUSE (Weight: 22, Max: 66)
    daily_counts = df.groupby(['CustomerID', 'Date'])['txn_marker'].transform('count')
    
    id_percentile_98 = daily_counts.quantile(0.98)
    hard_floor_id = 3
    id_threshold = min(id_percentile_98, hard_floor_id)
    
    card_mask = (daily_counts > id_threshold).values
    card_severity = np.where(
        card_mask,
        np.minimum((daily_counts.values / id_threshold) - 1, 3.0),
        0
    )
    card_score = 22 * card_severity * df['Variance'].values
    risk_score += card_score
    
    for idx in np.where(card_mask)[0]:
        flag_lists[idx].append('Card Misuse')

    # --- STEP 3: FINAL SCORING ---
    # Normalize to 0-100 integer range
    df['Risk_Score'] = np.clip(risk_score, 0, 100).astype(int)

    # --- STEP 4: FINAL STATUS ---
    # Threshold: Risk_Score > 50
    df['Status'] = np.where(df['Risk_Score'] > 50, 'Fraud', 'Normal')
    
    # Convert flags list to proper format
    df['Flag_Reasons'] = [flags if flags else ['Normal'] for flags in flag_lists]

    # Drop helper columns
    df.drop(columns=['txn_marker', 'Hour', 'Date', 'Variance'], inplace=True, errors='ignore')
    
    return df
