import pandas as pd
import random
import datetime
import os
import uuid

# Initialize constants
ITEMS = {
    'Rice': {'price': 3.0, 'normal_qty_range': (5, 20)},
    'Wheat': {'price': 2.0, 'normal_qty_range': (5, 20)},
    'Sugar': {'price': 20.0, 'normal_qty_range': (1, 3)},
    'Oil': {'price': 50.0, 'normal_qty_range': (1, 2)},
    'Kerosene': {'price': 25.0, 'normal_qty_range': (1, 3)}
}
TOTAL_TXNS = 5000
SHOP_IDS = [f'SHOP_{i:03d}' for i in range(1, 51)]
BENEFICIARY_POOL_SIZE = 3000
BENEFICIARY_IDS = [f'BEN_{i:05d}' for i in range(1, BENEFICIARY_POOL_SIZE + 1)]

# Date range
END_DATE = datetime.datetime.now()
START_DATE = END_DATE - datetime.timedelta(days=30)

# Load Valid Locations and District Map
try:
    loc_df = pd.read_csv('data/processed/delhi_shop_locations.csv')
    # Create Dict: ShopID -> {Lat, Lon, District}
    SHOP_META = loc_df.set_index('ShopID').to_dict(orient='index')
    print(f"Loaded metadata for {len(SHOP_META)} shops.")
except Exception as e:
    print(f"Error loading locations: {e}. Fallback to random.")
    SHOP_META = {}

def get_shop_meta(shop_id):
    if shop_id in SHOP_META:
        return SHOP_META[shop_id]
    else:
        # Fallback Delhi center
        return {'Latitude': 28.61, 'Longitude': 77.20, 'District': 'Unknown'}

def random_date(start, end, start_hour=8, end_hour=20):
    while True:
        delta = end - start
        random_second = random.randrange(int(delta.total_seconds()))
        dt = start + datetime.timedelta(seconds=random_second)
        if start_hour <= dt.hour < end_hour:
            return dt

def generate_normal_transactions():
    transactions = []
    beneficiary_usage = {b_id: 0 for b_id in BENEFICIARY_IDS}
    target_normal = TOTAL_TXNS - 60
    
    count = 0
    while count < target_normal:
        b_id = random.choice(BENEFICIARY_IDS)
        if beneficiary_usage[b_id] >= 2:
            continue
            
        beneficiary_usage[b_id] += 1
        
        item_name = random.choice(list(ITEMS.keys()))
        qty_range = ITEMS[item_name]['normal_qty_range']
        qty = random.randint(*qty_range)
        price = ITEMS[item_name]['price']
        
        shop_id = random.choice(SHOP_IDS)
        meta = get_shop_meta(shop_id)
        
        tx = {
            'TransactionID': str(uuid.uuid4()),
            'ShopID': shop_id,
            'BeneficiaryID': b_id,
            'Timestamp': random_date(START_DATE, END_DATE),
            'Item': item_name,
            'Quantity': qty,
            'Price': price * qty,
            'Latitude': meta['Latitude'],
            'Longitude': meta['Longitude'],
            'District': meta['District'],
            'is_fraud': 0
        }
        transactions.append(tx)
        count += 1
        
    return transactions

def inject_velocity_fraud(transactions):
    shop_id = random.choice(SHOP_IDS)
    base_time = random_date(START_DATE, END_DATE)
    meta = get_shop_meta(shop_id)
    
    print(f"Injecting Velocity Fraud at {shop_id}")
    
    for i in range(20):
        item_name = 'Rice'
        qty = 5
        tx = {
            'TransactionID': str(uuid.uuid4()),
            'ShopID': shop_id,
            'BeneficiaryID': random.choice(BENEFICIARY_IDS),
            'Timestamp': base_time + datetime.timedelta(seconds=i*2),
            'Item': item_name,
            'Quantity': qty,
            'Price': ITEMS[item_name]['price'] * qty,
            'Latitude': meta['Latitude'],
            'Longitude': meta['Longitude'],
            'District': meta['District'],
            'is_fraud': 1
        }
        transactions.append(tx)

def inject_volume_fraud(transactions):
    b_id = random.choice(BENEFICIARY_IDS)
    item_name = 'Sugar'
    normal_qty = ITEMS[item_name]['normal_qty_range'][1]
    fraud_qty = normal_qty * 10
    
    print(f"Injecting Volume Fraud for {b_id}")
    
    shop_id = random.choice(SHOP_IDS)
    meta = get_shop_meta(shop_id)
    
    tx = {
        'TransactionID': str(uuid.uuid4()),
        'ShopID': shop_id,
        'BeneficiaryID': b_id,
        'Timestamp': random_date(START_DATE, END_DATE),
        'Item': item_name,
        'Quantity': fraud_qty,
        'Price': ITEMS[item_name]['price'] * fraud_qty,
        'Latitude': meta['Latitude'],
        'Longitude': meta['Longitude'],
        'District': meta['District'],
        'is_fraud': 1
    }
    transactions.append(tx)

def inject_time_fraud(transactions):
    print("Injecting Time Fraud")
    for _ in range(20):
        day_offset = random.randint(0, 30)
        day_date = START_DATE + datetime.timedelta(days=day_offset)
        hour = random.randint(2, 3)
        minute = random.randint(0, 59)
        fraud_time = day_date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
        
        item_name = random.choice(list(ITEMS.keys()))
        qty = random.randint(*ITEMS[item_name]['normal_qty_range'])
        
        shop_id = random.choice(SHOP_IDS)
        meta = get_shop_meta(shop_id)
        
        tx = {
            'TransactionID': str(uuid.uuid4()),
            'ShopID': shop_id,
            'BeneficiaryID': random.choice(BENEFICIARY_IDS),
            'Timestamp': fraud_time,
            'Item': item_name,
            'Quantity': qty,
            'Price': ITEMS[item_name]['price'] * qty,
            'Latitude': meta['Latitude'],
            'Longitude': meta['Longitude'],
            'District': meta['District'],
            'is_fraud': 1
        }
        transactions.append(tx)

def main():
    print("Generating normal transactions...")
    transactions = generate_normal_transactions()
    
    print("Injecting fraud patterns...")
    inject_velocity_fraud(transactions)
    inject_volume_fraud(transactions)
    inject_time_fraud(transactions)
    
    df = pd.DataFrame(transactions)
    df = df.sort_values(by='Timestamp')
    
    os.makedirs('data/raw', exist_ok=True)
    output_path = 'data/raw/transactions.csv'
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} transactions. Saved to {output_path}")

if __name__ == "__main__":
    main()
