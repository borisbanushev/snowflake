#!/usr/bin/env python3
"""
Generate sample PostgreSQL Digital Banking data
Scaled down version: 10K customers, 100K sessions, 500K events, 8K KYC docs
"""

import psycopg2
from psycopg2.extras import execute_batch
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

# Configuration (Scaled down)
NUM_CUSTOMERS = 10000  # Reduced from 100,000
SESSIONS_PER_CUSTOMER = 10  # Average
EVENTS_PER_SESSION = 5  # Average (reduced from 15)
KYC_DOC_RATE = 0.8  # 80% of customers have KYC docs

# PostgreSQL RDS connection
POSTGRES_HOST = "snowflake-credit-demo-postgres.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com"
POSTGRES_PORT = 5432
POSTGRES_DATABASE = "digital_banking"
POSTGRES_USER = "digitaluser"
POSTGRES_PASSWORD = "DigitalPass123!"

print("=" * 70)
print("PostgreSQL Digital Banking Data Generator")
print("=" * 70)
print(f"Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
print(f"Database: {POSTGRES_DATABASE}")
print(f"Target Records:")
print(f"  - Customers: {NUM_CUSTOMERS:,}")
print(f"  - Sessions: ~{NUM_CUSTOMERS * SESSIONS_PER_CUSTOMER:,}")
print(f"  - Events: ~{NUM_CUSTOMERS * SESSIONS_PER_CUSTOMER * EVENTS_PER_SESSION:,}")
print(f"  - KYC Docs: ~{int(NUM_CUSTOMERS * KYC_DOC_RATE):,}")
print("=" * 70)
print()

def get_postgres_connection():
    """Connect to PostgreSQL database"""
    try:
        connection = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DATABASE,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            connect_timeout=10
        )
        print("✅ Connected to PostgreSQL RDS")
        
        # Test query
        cursor = connection.cursor()
        cursor.execute("SELECT version()")
        result = cursor.fetchone()
        print(f"   {result[0].split(',')[0]}")
        cursor.close()
        
        return connection
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        print("\nTroubleshooting:")
        print("1. Check if RDS instance is available")
        print("2. Verify security group allows your IP")
        print("3. Check credentials")
        return None

def create_tables(connection):
    """Create PostgreSQL tables"""
    print("\n🔨 Creating tables...")
    
    cursor = connection.cursor()
    
    # Drop existing tables (cascade to handle foreign keys)
    print("   Dropping existing tables...")
    cursor.execute("""
        DROP TABLE IF EXISTS digital_event CASCADE;
        DROP TABLE IF EXISTS digital_kyc_document CASCADE;
        DROP TABLE IF EXISTS digital_session CASCADE;
        DROP TABLE IF EXISTS digital_customer_profile CASCADE;
    """)
    
    # Create customer profile table
    print("   Creating digital_customer_profile...")
    cursor.execute("""
        CREATE TABLE digital_customer_profile (
            digital_id VARCHAR(36) PRIMARY KEY,
            customer_id VARCHAR(20) NOT NULL,
            email VARCHAR(100),
            mobile_number VARCHAR(20),
            username VARCHAR(50) UNIQUE,
            registration_date TIMESTAMP,
            last_login TIMESTAMP,
            login_count INTEGER DEFAULT 0,
            failed_login_count INTEGER DEFAULT 0,
            mfa_enabled BOOLEAN DEFAULT FALSE,
            mfa_type VARCHAR(20),
            device_count INTEGER DEFAULT 0,
            primary_device_type VARCHAR(20),
            biometric_enabled BOOLEAN DEFAULT FALSE,
            push_notifications BOOLEAN DEFAULT TRUE,
            email_verified BOOLEAN DEFAULT FALSE,
            mobile_verified BOOLEAN DEFAULT FALSE,
            ekyc_status VARCHAR(20) DEFAULT 'PENDING',
            ekyc_date TIMESTAMP NULL,
            preferred_language VARCHAR(10) DEFAULT 'EN',
            timezone VARCHAR(50) DEFAULT 'Asia/Singapore',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_customer_id ON digital_customer_profile(customer_id);
        CREATE INDEX idx_email ON digital_customer_profile(email);
    """)
    
    # Create session table
    print("   Creating digital_session...")
    cursor.execute("""
        CREATE TABLE digital_session (
            session_id VARCHAR(36) PRIMARY KEY,
            digital_id VARCHAR(36) REFERENCES digital_customer_profile(digital_id),
            customer_id VARCHAR(20),
            session_start TIMESTAMP,
            session_end TIMESTAMP NULL,
            duration_seconds INTEGER,
            device_id VARCHAR(100),
            device_type VARCHAR(20),
            device_model VARCHAR(50),
            os_version VARCHAR(20),
            app_version VARCHAR(20),
            ip_address VARCHAR(45),
            geolocation_lat DECIMAL(10,7),
            geolocation_lon DECIMAL(10,7),
            city VARCHAR(100),
            country VARCHAR(3),
            pages_viewed INTEGER DEFAULT 0,
            transactions_initiated INTEGER DEFAULT 0,
            transactions_completed INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            session_quality_score DECIMAL(5,2),
            exit_reason VARCHAR(30),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_session_digital_id ON digital_session(digital_id);
        CREATE INDEX idx_session_customer_id ON digital_session(customer_id);
        CREATE INDEX idx_session_start ON digital_session(session_start);
    """)
    
    # Create event table
    print("   Creating digital_event...")
    cursor.execute("""
        CREATE TABLE digital_event (
            event_id VARCHAR(36) PRIMARY KEY,
            session_id VARCHAR(36) REFERENCES digital_session(session_id),
            digital_id VARCHAR(36),
            customer_id VARCHAR(20),
            event_type VARCHAR(50),
            event_name VARCHAR(100),
            event_timestamp TIMESTAMP,
            page_name VARCHAR(100),
            element_id VARCHAR(100),
            event_data TEXT,
            response_time_ms INTEGER,
            success BOOLEAN DEFAULT TRUE,
            error_code VARCHAR(20),
            error_message VARCHAR(500),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_event_session_id ON digital_event(session_id);
        CREATE INDEX idx_event_type ON digital_event(event_type);
        CREATE INDEX idx_event_timestamp ON digital_event(event_timestamp);
    """)
    
    # Create KYC document table
    print("   Creating digital_kyc_document...")
    cursor.execute("""
        CREATE TABLE digital_kyc_document (
            document_id VARCHAR(36) PRIMARY KEY,
            digital_id VARCHAR(36) REFERENCES digital_customer_profile(digital_id),
            customer_id VARCHAR(20),
            document_type VARCHAR(30),
            document_number VARCHAR(50),
            issuing_country VARCHAR(3),
            issue_date DATE,
            expiry_date DATE,
            upload_date TIMESTAMP,
            verification_status VARCHAR(20) DEFAULT 'PENDING',
            verification_date TIMESTAMP NULL,
            verification_method VARCHAR(30),
            confidence_score DECIMAL(5,2),
            rejection_reason VARCHAR(200),
            face_match_score DECIMAL(5,2),
            liveness_check BOOLEAN,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_kyc_digital_id ON digital_kyc_document(digital_id);
        CREATE INDEX idx_kyc_customer_id ON digital_kyc_document(customer_id);
        CREATE INDEX idx_kyc_status ON digital_kyc_document(verification_status);
    """)
    
    connection.commit()
    cursor.close()
    print("✅ Tables created\n")

def generate_digital_profiles(num_customers):
    """Generate digital customer profiles"""
    print(f"👥 Generating {num_customers:,} digital customer profiles...")
    
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
        
        # Ensure unique username
        base_username = fake.user_name()[:40]
        unique_username = f"{base_username}_{i:06d}"[:50]
        
        profiles.append({
            'digital_id': fake.uuid4(),
            'customer_id': f'CUS-{i:06d}',
            'email': fake.email(),
            'mobile_number': fake.phone_number()[:20],
            'username': unique_username,
            'registration_date': reg_date,
            'last_login': last_login,
            'login_count': login_count,
            'failed_login_count': random.randint(0, 5),
            'mfa_enabled': random.choice([True, False]),
            'mfa_type': random.choice(['SMS', 'APP', 'EMAIL', None]),
            'device_count': random.randint(1, 4),
            'primary_device_type': random.choice(['iOS', 'Android', 'Web', 'Desktop']),
            'biometric_enabled': random.choice([True, False]),
            'push_notifications': random.choice([True, False]),
            'email_verified': random.choices([True, False], weights=[90, 10])[0],
            'mobile_verified': random.choices([True, False], weights=[85, 15])[0],
            'ekyc_status': random.choices(['VERIFIED', 'PENDING', 'FAILED'], weights=[80, 15, 5])[0],
            'ekyc_date': (reg_date + timedelta(days=random.randint(0, 30))) if random.random() > 0.2 else None,
            'preferred_language': random.choice(['EN', 'ZH', 'MS', 'TA']),
            'timezone': 'Asia/Singapore',
            'created_date': reg_date,
            'modified_date': datetime.now()
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
        digital_id = profiles_df.iloc[customer_idx]['digital_id']
        
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
            'session_id': fake.uuid4(),
            'digital_id': digital_id,
            'customer_id': f'CUS-{customer_idx:06d}',
            'session_start': start_time,
            'session_end': end_time,
            'duration_seconds': duration_seconds,
            'device_id': fake.uuid4()[:100],
            'device_type': random.choice(device_types),
            'device_model': random.choice(['iPhone 15', 'Samsung S23', 'Pixel 8', 'MacBook Pro', 'iPad Pro', 'Desktop'])[:50],
            'os_version': f'{random.randint(10, 16)}.{random.randint(0, 9)}',
            'app_version': f'{random.randint(2, 5)}.{random.randint(0, 9)}.{random.randint(0, 20)}',
            'ip_address': fake.ipv4(),
            'geolocation_lat': round(lat, 7),
            'geolocation_lon': round(lon, 7),
            'city': city,
            'country': country,
            'pages_viewed': pages_viewed,
            'transactions_initiated': transactions_initiated,
            'transactions_completed': transactions_completed,
            'error_count': error_count,
            'session_quality_score': round(quality_score, 2),
            'exit_reason': random.choice(['NORMAL', 'TIMEOUT', 'ERROR', 'USER_CLOSE', None]),
            'created_date': start_time
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
    
    # Create list of session IDs to reference
    session_list = sessions_df[['session_id', 'digital_id', 'customer_id']].to_dict('records')
    
    for i in tqdm(range(total_events)):
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
        
        events.append({
            'event_id': fake.uuid4(),
            'session_id': session['session_id'],
            'digital_id': session['digital_id'],
            'customer_id': session['customer_id'],
            'event_type': event_type,
            'event_name': random.choice(event_names[event_type]),
            'event_timestamp': event_time,
            'page_name': random.choice(page_names),
            'element_id': f'element_{random.randint(1, 200)}',
            'event_data': f'{{"action": "{event_type}", "value": {random.randint(1, 1000)}}}',
            'response_time_ms': random.randint(50, 2000),
            'success': is_success,
            'error_code': None if is_success else f'ERR_{random.randint(100, 999)}',
            'error_message': None if is_success else random.choice(['Network timeout', 'Invalid input', 'Server error', 'Authentication failed']),
            'created_date': event_time
        })
    
    return pd.DataFrame(events)

def generate_kyc_documents(profiles_df, kyc_rate):
    """Generate KYC document data"""
    num_docs = int(len(profiles_df) * kyc_rate)
    print(f"\n📄 Generating {num_docs:,} KYC documents...")
    
    documents = []
    doc_types = ['PASSPORT', 'DRIVERS_LICENSE', 'NATIONAL_ID', 'RESIDENCE_PERMIT']
    countries = ['SG', 'MY', 'ID', 'TH', 'PH', 'VN', 'US', 'GB', 'AU']
    verification_methods = ['AUTO_OCR', 'MANUAL_REVIEW', 'VIDEO_KYC', 'BIOMETRIC']
    
    # Randomly select customers for KYC docs
    selected_indices = random.sample(range(len(profiles_df)), num_docs)
    
    for idx in tqdm(selected_indices):
        profile = profiles_df.iloc[idx]
        
        # Upload date (shortly after registration)
        upload_date = profile['registration_date'] + timedelta(days=random.randint(0, 7))
        
        # Verification status and date
        status = random.choices(['VERIFIED', 'PENDING', 'REJECTED'], weights=[85, 10, 5])[0]
        verification_date = upload_date + timedelta(days=random.randint(0, 3)) if status != 'PENDING' else None
        
        # Issue and expiry dates
        issue_date = datetime.now().date() - timedelta(days=random.randint(365, 3650))
        expiry_date = datetime.now().date() + timedelta(days=random.randint(30, 3650))
        
        documents.append({
            'document_id': fake.uuid4(),
            'digital_id': profile['digital_id'],
            'customer_id': profile['customer_id'],
            'document_type': random.choice(doc_types),
            'document_number': fake.bothify(text='??#######'),
            'issuing_country': random.choice(countries),
            'issue_date': issue_date,
            'expiry_date': expiry_date,
            'upload_date': upload_date,
            'verification_status': status,
            'verification_date': verification_date,
            'verification_method': random.choice(verification_methods) if status == 'VERIFIED' else None,
            'confidence_score': round(random.uniform(85, 99), 2) if status == 'VERIFIED' else None,
            'rejection_reason': random.choice(['Poor image quality', 'Expired document', 'Mismatch', 'Unclear text']) if status == 'REJECTED' else None,
            'face_match_score': round(random.uniform(80, 99), 2) if status == 'VERIFIED' else None,
            'liveness_check': random.choice([True, False]) if status == 'VERIFIED' else None,
            'created_date': upload_date,
            'modified_date': verification_date or upload_date
        })
    
    return pd.DataFrame(documents)

def bulk_insert_postgres(connection, table_name, df, batch_size=1000):
    """Bulk insert data into PostgreSQL"""
    cursor = connection.cursor()
    
    total_rows = len(df)
    print(f"📥 Inserting {total_rows:,} rows into {table_name}...")
    
    # Replace NaT and NaN with None
    df = df.replace({pd.NaT: None, np.nan: None})
    
    # Prepare SQL
    columns = df.columns.tolist()
    placeholders = ', '.join(['%s'] * len(columns))
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    # Convert DataFrame to list of tuples
    data = [tuple(None if pd.isna(x) else x for x in row) for row in df.to_numpy()]
    
    # Batch insert
    for i in tqdm(range(0, total_rows, batch_size)):
        batch = data[i:i+batch_size]
        execute_batch(cursor, sql, batch)
        connection.commit()
    
    cursor.close()
    print(f"✅ Inserted {total_rows:,} rows\n")

def main():
    # Connect
    conn = get_postgres_connection()
    if not conn:
        return
    
    # Create tables
    create_tables(conn)
    
    # Generate data
    print("🎲 Generating sample data...\n")
    
    profiles_df = generate_digital_profiles(NUM_CUSTOMERS)
    sessions_df = generate_sessions(NUM_CUSTOMERS, SESSIONS_PER_CUSTOMER, profiles_df)
    events_df = generate_events(sessions_df, EVENTS_PER_SESSION)
    kyc_df = generate_kyc_documents(profiles_df, KYC_DOC_RATE)
    
    # Load data
    print("\n📤 Loading data to PostgreSQL RDS...\n")
    bulk_insert_postgres(conn, 'digital_customer_profile', profiles_df)
    bulk_insert_postgres(conn, 'digital_session', sessions_df)
    bulk_insert_postgres(conn, 'digital_event', events_df)
    bulk_insert_postgres(conn, 'digital_kyc_document', kyc_df)
    
    # Verify
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM digital_customer_profile")
    profile_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM digital_session")
    session_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM digital_event")
    event_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM digital_kyc_document")
    kyc_count = cursor.fetchone()[0]
    cursor.close()
    
    print("=" * 70)
    print("🎉 PostgreSQL Data Load Complete!")
    print("=" * 70)
    print(f"Customer Profiles:  {profile_count:,}")
    print(f"Sessions:           {session_count:,}")
    print(f"Events:             {event_count:,}")
    print(f"KYC Documents:      {kyc_count:,}")
    print(f"Total Records:      {profile_count + session_count + event_count + kyc_count:,}")
    print()
    print("✅ PostgreSQL RDS is ready for Snowflake Openflow CDC ingestion!")
    print()
    print("Next Steps:")
    print("  1. Configure Snowflake Openflow PostgreSQL connector")
    print("  2. Use this JDBC URL:")
    print(f"     jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}")
    print(f"  3. Tables: public.digital_customer_profile,public.digital_session,")
    print(f"             public.digital_event,public.digital_kyc_document")
    
    conn.close()

if __name__ == "__main__":
    main()
