#!/usr/bin/env python3
"""
Generate sample MySQL Digital Banking data
Generates 100K digital customer profiles with activity data
"""

import mysql.connector
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from tqdm import tqdm
import os

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Configuration
NUM_CUSTOMERS = 100000
SESSIONS_PER_CUSTOMER = 10  # Average
EVENTS_PER_SESSION = 15  # Average

# MySQL connection
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'digital_banking')
MYSQL_USER = os.getenv('MYSQL_USER', 'digitaluser')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'DigitalPass!')

print("=" * 70)
print("MySQL Digital Banking Data Generator")
print("=" * 70)
print(f"Host: {MYSQL_HOST}:{MYSQL_PORT}")
print(f"Database: {MYSQL_DATABASE}")
print("=" * 70)
print()

def get_mysql_connection():
    """Connect to MySQL database"""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            database=MYSQL_DATABASE,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        print("✅ Connected to MySQL database")
        
        # Test query
        cursor = connection.cursor()
        cursor.execute("SELECT 'MySQL Connected!' AS status")
        result = cursor.fetchone()
        print(f"   {result[0]}")
        cursor.close()
        
        return connection
    except Exception as e:
        print(f"❌ Failed to connect to MySQL: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Docker container is running:")
        print("   cd infrastructure/docker && docker-compose up -d")
        print("2. Wait 30 seconds for MySQL to fully initialize")
        print("3. Check credentials in .env or docker-compose.yml")
        return None

def generate_digital_profiles(num_customers):
    """Generate digital customer profiles"""
    print(f"\n👥 Generating {num_customers:,} digital customer profiles...")
    
    profiles = []
    for i in tqdm(range(num_customers)):
        # Registration date (last 5 years)
        reg_date = datetime.now() - timedelta(days=random.randint(0, 1825))
        
        # Last login (within last 90 days for active users)
        is_active = random.random() > 0.15  # 85% active
        if is_active:
            last_login = datetime.now() - timedelta(days=random.randint(0, 90))
            login_count = random.randint(50, 500)
        else:
            last_login = datetime.now() - timedelta(days=random.randint(91, 365))
            login_count = random.randint(5, 50)
        
        # Ensure unique username by appending customer index
        base_username = fake.user_name()[:40]  # Leave room for suffix
        unique_username = f"{base_username}_{i:06d}"[:50]  # Max 50 chars
        
        profiles.append({
            'DIGITAL_ID': fake.uuid4(),
            'CUSTOMER_ID': f'CUS-{i:06d}',
            'EMAIL': fake.email(),
            'MOBILE_NUMBER': fake.phone_number()[:20],
            'USERNAME': unique_username,
            'REGISTRATION_DATE': reg_date,
            'LAST_LOGIN': last_login,
            'LOGIN_COUNT': login_count,
            'FAILED_LOGIN_COUNT': random.randint(0, 5),
            'MFA_ENABLED': random.choice([True, False]),
            'MFA_TYPE': random.choice(['SMS', 'APP', 'EMAIL', None]),
            'DEVICE_COUNT': random.randint(1, 4),
            'PRIMARY_DEVICE_TYPE': random.choice(['iOS', 'Android', 'Web', 'Desktop']),
            'BIOMETRIC_ENABLED': random.choice([True, False]),
            'PUSH_NOTIFICATIONS': random.choice([True, False]),
            'EMAIL_VERIFIED': random.choices([True, False], weights=[90, 10])[0],
            'MOBILE_VERIFIED': random.choices([True, False], weights=[85, 15])[0],
            'EKYC_STATUS': random.choices(['VERIFIED', 'PENDING', 'FAILED'], weights=[80, 15, 5])[0],
            'EKYC_DATE': (reg_date + timedelta(days=random.randint(0, 30))) if random.random() > 0.2 else None,
            'PREFERRED_LANGUAGE': random.choice(['EN', 'ZH', 'MS', 'TA']),
            'TIMEZONE': 'Asia/Singapore',
            'CREATED_DATE': reg_date,
            'MODIFIED_DATE': datetime.now()
        })
    
    return pd.DataFrame(profiles)

def generate_sessions(num_customers, avg_sessions_per_customer, profiles_df):
    """Generate session data"""
    total_sessions = num_customers * avg_sessions_per_customer
    print(f"\n🔐 Generating {total_sessions:,} sessions...")
    
    sessions = []
    device_types = ['iOS', 'Android', 'Web', 'Desktop']
    cities = ['Singapore', 'Kuala Lumpur', 'Jakarta', 'Bangkok', 'Manila']
    countries = ['SG', 'MY', 'ID', 'TH', 'PH']
    
    for i in tqdm(range(total_sessions)):
        customer_idx = random.randint(0, num_customers - 1)
        digital_id = profiles_df.iloc[customer_idx]['DIGITAL_ID']
        
        # Session timing (last 180 days)
        start_time = datetime.now() - timedelta(
            days=random.randint(0, 180),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Session duration (1-30 minutes)
        is_completed = random.random() > 0.05  # 95% completed
        duration_seconds = random.randint(60, 1800) if is_completed else None
        end_time = start_time + timedelta(seconds=duration_seconds) if duration_seconds else None
        
        # City and location
        location_idx = random.randint(0, len(cities) - 1)
        city = cities[location_idx]
        country = countries[location_idx]
        
        # Singapore coordinates (with random offset)
        base_lat = 1.3521
        base_lon = 103.8198
        lat = base_lat + random.uniform(-0.2, 0.2)
        lon = base_lon + random.uniform(-0.2, 0.2)
        
        # Session activity
        pages_viewed = random.randint(1, 20)
        transactions_initiated = random.randint(0, 5)
        transactions_completed = random.randint(0, transactions_initiated)
        error_count = random.randint(0, 3)
        
        # Quality score (0-100)
        quality_score = max(0, 100 - (error_count * 10) - ((transactions_initiated - transactions_completed) * 5))
        
        sessions.append({
            'SESSION_ID': fake.uuid4(),
            'DIGITAL_ID': digital_id,
            'CUSTOMER_ID': f'CUS-{customer_idx:06d}',
            'SESSION_START': start_time,
            'SESSION_END': end_time,
            'DURATION_SECONDS': duration_seconds,
            'DEVICE_ID': fake.uuid4()[:100],
            'DEVICE_TYPE': random.choice(device_types),
            'DEVICE_MODEL': random.choice(['iPhone 15', 'Samsung S23', 'Pixel 8', 'MacBook Pro', 'iPad Pro', 'Desktop'])[:50],
            'OS_VERSION': f'{random.randint(10, 16)}.{random.randint(0, 9)}',
            'APP_VERSION': f'{random.randint(2, 5)}.{random.randint(0, 9)}.{random.randint(0, 20)}',
            'IP_ADDRESS': fake.ipv4(),
            'GEOLOCATION_LAT': round(lat, 7),
            'GEOLOCATION_LON': round(lon, 7),
            'CITY': city,
            'COUNTRY': country,
            'PAGES_VIEWED': pages_viewed,
            'TRANSACTIONS_INITIATED': transactions_initiated,
            'TRANSACTIONS_COMPLETED': transactions_completed,
            'ERROR_COUNT': error_count,
            'SESSION_QUALITY_SCORE': round(quality_score, 2),
            'EXIT_REASON': random.choice(['NORMAL', 'TIMEOUT', 'ERROR', 'USER_CLOSE', None]),
            'CREATED_DATE': start_time
        })
    
    return pd.DataFrame(sessions)

def generate_events(sessions_df, avg_events_per_session):
    """Generate event data"""
    total_events = int(len(sessions_df) * avg_events_per_session)
    print(f"\n📱 Generating {total_events:,} digital events...")
    
    events = []
    event_types = [
        'PAGE_VIEW', 'BUTTON_CLICK', 'FORM_SUBMIT', 'SEARCH', 
        'BALANCE_CHECK', 'TRANSACTION_INIT', 'TRANSACTION_CONFIRM',
        'PAYMENT', 'TRANSFER', 'DOWNLOAD', 'SETTINGS_CHANGE'
    ]
    
    event_names = {
        'PAGE_VIEW': ['Dashboard View', 'Account View', 'Transfer View', 'Profile View'],
        'BUTTON_CLICK': ['Submit Button', 'Cancel Button', 'Confirm Button', 'Next Button'],
        'FORM_SUBMIT': ['Login Form', 'Transfer Form', 'Profile Update', 'Payment Form'],
        'SEARCH': ['Account Search', 'Transaction Search', 'Beneficiary Search'],
        'BALANCE_CHECK': ['Account Balance', 'Available Balance', 'Credit Limit'],
        'TRANSACTION_INIT': ['Transfer Init', 'Payment Init', 'Bill Payment Init'],
        'TRANSACTION_CONFIRM': ['Transfer Confirm', 'Payment Confirm', 'Bill Payment Confirm'],
        'PAYMENT': ['Bill Payment', 'Merchant Payment', 'P2P Payment'],
        'TRANSFER': ['Internal Transfer', 'External Transfer', 'International Transfer'],
        'DOWNLOAD': ['Statement Download', 'Receipt Download', 'Report Download'],
        'SETTINGS_CHANGE': ['Language Change', 'Notification Change', 'Security Setting']
    }
    
    page_names = ['Dashboard', 'Accounts', 'Transfers', 'Payments', 'Profile', 'Settings', 'Help', 'Reports']
    
    print("   This may take a few minutes...")
    
    # Create list of session IDs to reference
    session_list = sessions_df[['SESSION_ID', 'DIGITAL_ID', 'CUSTOMER_ID']].to_dict('records')
    
    # Generate in batches for better performance
    batch_size = 100000
    for batch_start in tqdm(range(0, total_events, batch_size)):
        batch_end = min(batch_start + batch_size, total_events)
        batch_events = []
        
        for i in range(batch_start, batch_end):
            # Pick random session
            session = random.choice(session_list)
            
            event_time = datetime.now() - timedelta(
                days=random.randint(0, 180),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            event_type = random.choice(event_types)
            is_success = random.random() > 0.05  # 95% success rate
            
            batch_events.append({
                'EVENT_ID': fake.uuid4(),
                'SESSION_ID': session['SESSION_ID'],
                'DIGITAL_ID': session['DIGITAL_ID'],
                'CUSTOMER_ID': session['CUSTOMER_ID'],
                'EVENT_TYPE': event_type,
                'EVENT_NAME': random.choice(event_names[event_type]),
                'EVENT_TIMESTAMP': event_time,
                'PAGE_NAME': random.choice(page_names),
                'ELEMENT_ID': f'element_{random.randint(1, 200)}',
                'EVENT_DATA': f'{{"action": "{event_type}", "value": {random.randint(1, 1000)}}}',
                'RESPONSE_TIME_MS': random.randint(50, 2000),
                'SUCCESS': is_success,
                'ERROR_CODE': None if is_success else f'ERR_{random.randint(100, 999)}',
                'ERROR_MESSAGE': None if is_success else random.choice(['Network timeout', 'Invalid input', 'Server error', 'Authentication failed']),
                'CREATED_DATE': event_time
            })
        
        events.extend(batch_events)
    
    return pd.DataFrame(events)

def bulk_insert(connection, table_name, df, batch_size=1000):
    """Bulk insert data into MySQL"""
    cursor = connection.cursor()
    
    total_rows = len(df)
    print(f"📥 Inserting {total_rows:,} rows into {table_name}...")
    
    # Replace NaT and NaN with None for proper NULL handling
    df = df.replace({pd.NaT: None, np.nan: None})
    
    # Prepare SQL
    columns = df.columns.tolist()
    placeholders = ', '.join(['%s'] * len(columns))
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    # Convert DataFrame to list of tuples, ensuring None values are preserved
    data = [tuple(None if pd.isna(x) else x for x in row) for row in df.to_numpy()]
    
    # Batch insert
    for i in tqdm(range(0, total_rows, batch_size)):
        batch = data[i:i+batch_size]
        cursor.executemany(sql, batch)
        connection.commit()
    
    cursor.close()
    print(f"✅ Inserted {total_rows:,} rows\n")

def main():
    # Connect
    conn = get_mysql_connection()
    if not conn:
        return
    
    # Generate data
    print("\n🎲 Generating sample data...\n")
    
    profiles_df = generate_digital_profiles(NUM_CUSTOMERS)
    sessions_df = generate_sessions(NUM_CUSTOMERS, SESSIONS_PER_CUSTOMER, profiles_df)
    
    # For events, generate fewer to keep it manageable
    events_df = generate_events(sessions_df, 5)  # 5 events per session
    
    # Load data
    print("\n📤 Loading data to MySQL...\n")
    bulk_insert(conn, 'DIGITAL_CUSTOMER_PROFILE', profiles_df)
    bulk_insert(conn, 'DIGITAL_SESSION', sessions_df)
    bulk_insert(conn, 'DIGITAL_EVENT', events_df)
    
    # Verify
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM DIGITAL_CUSTOMER_PROFILE")
    profile_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM DIGITAL_SESSION")
    session_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM DIGITAL_EVENT")
    event_count = cursor.fetchone()[0]
    cursor.close()
    
    print("=" * 70)
    print("🎉 MySQL Data Load Complete!")
    print("=" * 70)
    print(f"Customer Profiles: {profile_count:,}")
    print(f"Sessions:          {session_count:,}")
    print(f"Events:            {event_count:,}")
    print("\n✅ MySQL is ready for Snowflake Openflow CDC ingestion!")
    
    conn.close()

if __name__ == "__main__":
    main()
