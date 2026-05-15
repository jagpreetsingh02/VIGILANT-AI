import pandas as pd
import numpy as np
import random
import streamlit as st
from datetime import datetime, timedelta

def get_csv_template():
    """Returns a DataFrame with the EXACT columns the user must upload."""
    columns = ['TransactionID', 'Timestamp', 'CustomerID', 'ShopID', 'Item_Type', 'Quantity_kg', 'Amount']
    return pd.DataFrame(columns=columns)

def _generate_delhi_coords(n_shops=100):
    """Generates fixed coordinates for shops spread across Delhi."""
    shop_coords = {}
    for i in range(1, n_shops + 1):
        shop_id = f"SHOP_{i:03d}"
        lat = 28.61 + random.uniform(-0.1, 0.1)
        lon = 77.20 + random.uniform(-0.1, 0.1)
        shop_coords[shop_id] = (lat, lon)
    return shop_coords

@st.cache_data(ttl=3600, show_spinner=False)
def load_data(uploaded_file=None):
    """
    Generates 97% clean data + 3% surgical fraud with balanced crime profiles.
    OPTIMIZED: Cached for 1 hour. Auto-invalidates when uploaded_file changes.
    """
    
    shop_coords = _generate_delhi_coords(n_shops=100)
    
    if uploaded_file is None:
        # --- PHASE 1: GENERATE 97% NORMAL BACKGROUND DATA ---
        n_total = 50000
        n_normal = int(n_total * 0.97)  # 48,500 normal
        n_fraud = n_total - n_normal     # 1,500 fraud
        
        # Normal data constraints
        shop_ids_pool = list(shop_coords.keys())
        customer_ids_pool = [f"RATION_CARD_{i:04d}" for i in range(1, 5001)]
        items = ['Rice', 'Wheat', 'Sugar', 'Salt']
        probs = [0.4, 0.4, 0.1, 0.1]
        prices = {'Rice': 3, 'Wheat': 2, 'Sugar': 20, 'Salt': 10}
        
        # Generate normal transactions
        normal_data = []
        
        # Track usage to prevent same customer on same day
        daily_customers = {}  # {date: set of customer IDs}
        
        for i in range(n_normal):
            # Time: Strictly 08:00 to 20:00
            base_date = datetime.now() - timedelta(days=random.randint(0, 29))
            hour = random.randint(8, 20)
            minute = random.randint(0, 59)
            timestamp = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Customer ID - ensure no repeats on same day
            date_key = timestamp.date()
            if date_key not in daily_customers:
                daily_customers[date_key] = set()
            
            # Pick a customer that hasn't been used today
            available_customers = [c for c in customer_ids_pool if c not in daily_customers[date_key]]
            if not available_customers:
                # If all used (unlikely), just pick random
                customer_id = random.choice(customer_ids_pool)
            else:
                customer_id = random.choice(available_customers)
                daily_customers[date_key].add(customer_id)
            
            # Item type
            item_type = np.random.choice(items, p=probs)
            
            # Quantity: Conservative amounts
            if item_type in ['Rice', 'Wheat']:
                quantity = random.randint(10, 30) if item_type == 'Rice' else random.randint(10, 20)
            elif item_type == 'Sugar':
                quantity = random.randint(1, 3)
            else:  # Salt
                quantity = 1
            
            # Amount: Normal pricing
            amount = quantity * prices[item_type]
            
            normal_data.append({
                'TransactionID': f"TXN_{i:07d}",
                'Timestamp': timestamp,
                'CustomerID': customer_id,
                'ShopID': random.choice(shop_ids_pool),
                'Item_Type': item_type,
                'Quantity_kg': quantity,
                'Amount': amount
            })
        
        df_normal = pd.DataFrame(normal_data)
        
        # --- PHASE 2: INJECT 3% EXTREME FRAUD (BALANCED PROFILES) ---
        # Split 1500 fraud transactions into 5 equal groups of 300 each
        n_per_profile = n_fraud // 5
        
        fraud_data = []
        txn_id_offset = n_normal
        
        # PROFILE A: VELOCITY FRAUD (300 transactions)
        # Create bursts of 80+ transactions in single hour for specific shops
        velocity_shops = random.sample(shop_ids_pool, 3)  # 3 ghost shops
        for shop in velocity_shops:
            burst_time = (datetime.now() - timedelta(days=random.randint(0, 29))).replace(
                hour=random.randint(9, 18), minute=0, second=0, microsecond=0
            )
            # Inject 100 transactions in this hour
            for j in range(100):
                fraud_data.append({
                    'TransactionID': f"TXN_{txn_id_offset + len(fraud_data):07d}",
                    'Timestamp': burst_time + timedelta(minutes=random.randint(0, 59)),
                    'CustomerID': random.choice(customer_ids_pool),
                    'ShopID': shop,
                    'Item_Type': random.choice(items),
                    'Quantity_kg': random.randint(10, 25),
                    'Amount': random.uniform(30, 100)
                })
        
        # PROFILE B: HOARDING FRAUD (300 transactions)
        for _ in range(n_per_profile):
            # Extreme quantities
            if random.random() > 0.5:
                # Rice hoarding: 100kg
                item = 'Rice'
                qty = random.randint(80, 150)
            else:
                # Salt hoarding: 50kg
                item = 'Salt'
                qty = random.randint(30, 80)
            
            fraud_data.append({
                'TransactionID': f"TXN_{txn_id_offset + len(fraud_data):07d}",
                'Timestamp': (datetime.now() - timedelta(days=random.randint(0, 29))).replace(
                    hour=random.randint(9, 18), minute=random.randint(0, 59), second=0, microsecond=0
                ),
                'CustomerID': random.choice(customer_ids_pool),
                'ShopID': random.choice(shop_ids_pool),
                'Item_Type': item,
                'Quantity_kg': qty,
                'Amount': qty * prices[item]
            })
        
        # PROFILE C: TIME FRAUD (300 transactions)
        for _ in range(n_per_profile):
            night_hour = random.choice([0, 1, 2, 3, 4, 5, 23])
            fraud_data.append({
                'TransactionID': f"TXN_{txn_id_offset + len(fraud_data):07d}",
                'Timestamp': (datetime.now() - timedelta(days=random.randint(0, 29))).replace(
                    hour=night_hour, minute=random.randint(0, 59), second=0, microsecond=0
                ),
                'CustomerID': random.choice(customer_ids_pool),
                'ShopID': random.choice(shop_ids_pool),
                'Item_Type': random.choice(items),
                'Quantity_kg': random.randint(10, 25),
                'Amount': random.uniform(30, 80)
            })
        
        # PROFILE D: DISTRICT DEVIATION (300 transactions)
        # Force amount to be 5x normal (selling at inflated prices)
        for _ in range(n_per_profile):
            item = random.choice(items)
            qty = random.randint(10, 30)
            normal_amount = qty * prices[item]
            inflated_amount = normal_amount * 5  # 5x markup
            
            fraud_data.append({
                'TransactionID': f"TXN_{txn_id_offset + len(fraud_data):07d}",
                'Timestamp': (datetime.now() - timedelta(days=random.randint(0, 29))).replace(
                    hour=random.randint(9, 18), minute=random.randint(0, 59), second=0, microsecond=0
                ),
                'CustomerID': random.choice(customer_ids_pool),
                'ShopID': random.choice(shop_ids_pool),
                'Item_Type': item,
                'Quantity_kg': qty,
                'Amount': inflated_amount
            })
        
        # PROFILE E: CARD MISUSE (300 transactions)
        # Pick specific "criminal" IDs and make them buy 20 times per day
        criminal_ids = [f"RC_CRIMINAL_{i:03d}" for i in range(15)]  # 15 criminals
        for criminal_id in criminal_ids:
            fraud_date = (datetime.now() - timedelta(days=random.randint(0, 29))).replace(
                hour=9, minute=0, second=0, microsecond=0
            )
            # Each criminal does 20 transactions in one day
            for j in range(20):
                fraud_data.append({
                    'TransactionID': f"TXN_{txn_id_offset + len(fraud_data):07d}",
                    'Timestamp': fraud_date + timedelta(hours=random.randint(0, 10), minutes=random.randint(0, 59)),
                    'CustomerID': criminal_id,
                    'ShopID': random.choice(shop_ids_pool),
                    'Item_Type': random.choice(items),
                    'Quantity_kg': random.randint(10, 25),
                    'Amount': random.uniform(30, 80)
                })
        
        df_fraud = pd.DataFrame(fraud_data)
        
        # Combine normal + fraud
        df = pd.concat([df_normal, df_fraud], ignore_index=True)
        
        # Shuffle to mix fraud throughout dataset
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # --- PHASE 3: ML COMPATIBILITY ---
        # Add coordinates
        coords_df = pd.DataFrame.from_dict(shop_coords, orient='index', columns=['Lat', 'Lon'])
        df = df.join(coords_df, on='ShopID')
        
        # Apply ML Engine
        from src import ml_engine
        df = ml_engine.detect_fraud(df)
        
        return df

    else:
        # --- USER UPLOAD SCENARIO ---
        try:
            df = pd.read_csv(uploaded_file)
            
            required = ['TransactionID', 'Timestamp', 'CustomerID', 'ShopID', 'Item_Type', 'Amount', 'Quantity_kg']
            for col in required:
                if col not in df.columns:
                    if col == 'Amount' or col == 'Quantity_kg':
                        df[col] = 0
                    elif col == 'Item_Type':
                        df[col] = "Unknown"
                    else:
                        df[col] = "UNKNOWN"
            
            # Add location if missing
            if 'Lat' not in df.columns or 'Lon' not in df.columns:
                coords_df = pd.DataFrame.from_dict(shop_coords, orient='index', columns=['Lat', 'Lon'])
                df = df.join(coords_df, on='ShopID')
                missing_mask = df['Lat'].isna()
                n_missing = missing_mask.sum()
                if n_missing > 0:
                    df.loc[missing_mask, 'Lat'] = 28.61 + np.random.uniform(-0.1, 0.1, n_missing)
                    df.loc[missing_mask, 'Lon'] = 77.20 + np.random.uniform(-0.1, 0.1, n_missing)
            
            # Apply ML Engine
            from src import ml_engine
            df = ml_engine.detect_fraud(df)
            
            return df
            
        except Exception as e:
            return pd.DataFrame()
