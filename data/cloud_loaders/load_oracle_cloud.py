#!/usr/bin/env python3
"""
Load T24 Core Banking Data to Oracle Cloud
Supports both Autonomous Database (with/without wallet) and DB System
"""

import oracledb
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from tqdm import tqdm
import os
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Using environment variables directly.")

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Configuration from environment
ORACLE_HOST = os.getenv('ORACLE_CLOUD_HOST', 'localhost')
ORACLE_PORT = int(os.getenv('ORACLE_CLOUD_PORT', '1522'))
ORACLE_SERVICE = os.getenv('ORACLE_CLOUD_SERVICE', 'XE')
ORACLE_USER = os.getenv('ORACLE_CLOUD_USERNAME', 'ADMIN')
ORACLE_PASSWORD = os.getenv('ORACLE_CLOUD_PASSWORD', '')
USE_WALLET = os.getenv('ORACLE_USE_WALLET', 'false').lower() == 'true'
WALLET_LOCATION = os.getenv('ORACLE_WALLET_LOCATION', '')
WALLET_PASSWORD = os.getenv('ORACLE_WALLET_PASSWORD', '')

# Data generation config
NUM_CUSTOMERS = int(os.getenv('NUM_CUSTOMERS', '100000'))
NUM_ACCOUNTS = int(NUM_CUSTOMERS * 1.8)
NUM_LOANS = int(NUM_CUSTOMERS * 0.35)

print("=" * 70)
print("Oracle Cloud T24 Data Loader")
print("=" * 70)

def get_oracle_connection():
    """Connect to Oracle Cloud Database"""
    try:
        if USE_WALLET and WALLET_LOCATION:
            # Autonomous Database with wallet
            print(f"📦 Connecting with wallet: {WALLET_LOCATION}")
            oracledb.init_oracle_client(config_dir=WALLET_LOCATION)
            
            connection = oracledb.connect(
                user=ORACLE_USER,
                password=ORACLE_PASSWORD,
                dsn=ORACLE_SERVICE,
                config_dir=WALLET_LOCATION,
                wallet_location=WALLET_LOCATION,
                wallet_password=WALLET_PASSWORD
            )
        else:
            # Standard connection (DB System or Autonomous with TLS)
            print(f"🔌 Connecting to {ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}")
            connection = oracledb.connect(
                user=ORACLE_USER,
                password=ORACLE_PASSWORD,
                host=ORACLE_HOST,
                port=ORACLE_PORT,
                service_name=ORACLE_SERVICE
            )
        
        print("✅ Connected to Oracle Cloud successfully!")
        
        # Test query
        cursor = connection.cursor()
        cursor.execute("SELECT 'Oracle Cloud Connected!' AS status FROM DUAL")
        result = cursor.fetchone()
        print(f"   {result[0]}")
        cursor.close()
        
        return connection
    except Exception as e:
        print(f"❌ Failed to connect to Oracle Cloud: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has correct credentials")
        print("2. Verify network connectivity to Oracle Cloud")
        print("3. For Autonomous DB, ensure wallet is downloaded and path is correct")
        print("4. Check if IP is whitelisted in Access Control List")
        return None

def create_schema(connection):
    """Create T24 tables in Oracle Cloud"""
    cursor = connection.cursor()
    
    print("\n📋 Creating T24 schema...")
    
    # Drop existing tables
    tables = ['T24_COLLATERAL', 'T24_PAYMENT_SCHEDULE', 'T24_LOAN', 
              'T24_TRANSACTION', 'T24_ACCOUNT', 'T24_CUSTOMER']
    
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE {table} CASCADE CONSTRAINTS")
            print(f"   Dropped existing {table}")
        except:
            pass
    
    # Create T24_CUSTOMER
    cursor.execute("""
        CREATE TABLE T24_CUSTOMER (
            CUSTOMER_ID VARCHAR2(20) PRIMARY KEY,
            MNEMONIC VARCHAR2(50),
            SHORT_NAME VARCHAR2(100),
            NAME_1 VARCHAR2(100),
            NAME_2 VARCHAR2(100),
            GENDER VARCHAR2(10),
            DATE_OF_BIRTH DATE,
            MARITAL_STATUS VARCHAR2(20),
            NATIONALITY VARCHAR2(3),
            RESIDENCE VARCHAR2(3),
            SECTOR VARCHAR2(10),
            INDUSTRY VARCHAR2(10),
            TARGET_MARKET VARCHAR2(20),
            CUSTOMER_STATUS VARCHAR2(20),
            CUSTOMER_SINCE DATE,
            KYC_STATUS VARCHAR2(20),
            KYC_LAST_REVIEW DATE,
            RISK_CATEGORY VARCHAR2(20),
            RELATIONSHIP_MANAGER VARCHAR2(50),
            BRANCH_CODE VARCHAR2(10),
            CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            MODIFIED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created T24_CUSTOMER")
    
    # Create T24_ACCOUNT
    cursor.execute("""
        CREATE TABLE T24_ACCOUNT (
            ACCOUNT_ID VARCHAR2(20) PRIMARY KEY,
            CUSTOMER_ID VARCHAR2(20) REFERENCES T24_CUSTOMER(CUSTOMER_ID),
            ACCOUNT_TITLE VARCHAR2(200),
            CATEGORY VARCHAR2(10),
            PRODUCT_CODE VARCHAR2(20),
            PRODUCT_NAME VARCHAR2(100),
            CURRENCY VARCHAR2(3),
            WORKING_BALANCE NUMBER(18,2),
            ONLINE_ACTUAL_BAL NUMBER(18,2),
            LOCKED_AMOUNT NUMBER(18,2),
            AVAILABLE_LIMIT NUMBER(18,2),
            ACCOUNT_STATUS VARCHAR2(20),
            OPENING_DATE DATE,
            LAST_ACTIVITY_DATE DATE,
            INTEREST_RATE NUMBER(8,4),
            BRANCH_CODE VARCHAR2(10),
            JOINT_HOLDER_1 VARCHAR2(20),
            JOINT_HOLDER_2 VARCHAR2(20),
            CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            MODIFIED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created T24_ACCOUNT")
    
    # Create T24_LOAN
    cursor.execute("""
        CREATE TABLE T24_LOAN (
            LOAN_ID VARCHAR2(20) PRIMARY KEY,
            CUSTOMER_ID VARCHAR2(20) REFERENCES T24_CUSTOMER(CUSTOMER_ID),
            ACCOUNT_ID VARCHAR2(20) REFERENCES T24_ACCOUNT(ACCOUNT_ID),
            LOAN_TYPE VARCHAR2(30),
            PRODUCT_CODE VARCHAR2(20),
            PRODUCT_NAME VARCHAR2(100),
            CURRENCY VARCHAR2(3),
            PRINCIPAL_AMOUNT NUMBER(18,2),
            OUTSTANDING_PRINCIPAL NUMBER(18,2),
            INTEREST_RATE NUMBER(8,4),
            INTEREST_TYPE VARCHAR2(20),
            TERM_MONTHS NUMBER(5),
            MONTHLY_PAYMENT NUMBER(18,2),
            START_DATE DATE,
            MATURITY_DATE DATE,
            NEXT_PAYMENT_DATE DATE,
            PAYMENTS_MADE NUMBER(5),
            PAYMENTS_REMAINING NUMBER(5),
            DAYS_PAST_DUE NUMBER(5),
            ARREARS_AMOUNT NUMBER(18,2),
            LOAN_STATUS VARCHAR2(20),
            COLLATERAL_TYPE VARCHAR2(30),
            COLLATERAL_VALUE NUMBER(18,2),
            LTV_RATIO NUMBER(6,4),
            APPROVAL_DATE DATE,
            APPROVED_BY VARCHAR2(50),
            CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            MODIFIED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created T24_LOAN")
    
    connection.commit()
    cursor.close()
    print("✅ Schema creation complete!\n")

def generate_customers(num_customers):
    """Generate customer master data"""
    print(f"👥 Generating {num_customers:,} customers...")
    
    customers = []
    for i in tqdm(range(num_customers)):
        age = int(np.random.normal(40, 15))
        age = max(18, min(80, age))
        dob = datetime.now() - timedelta(days=age*365.25)
        
        years_customer = random.randint(1, 20)
        customer_since = datetime.now() - timedelta(days=years_customer*365)
        
        customers.append((
            f'CUS-{i:06d}',
            fake.user_name()[:20],
            fake.name()[:50],
            fake.name(),
            '',
            random.choice(['M', 'F']),
            dob.date(),
            random.choice(['SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED']),
            'SGP',
            'SGP',
            random.choice(['1001', '1002', '2001', '2002']),
            random.choice(['TECH', 'FINANCE', 'HEALTH', 'RETAIL', 'MANUF']),
            random.choices(['RETAIL', 'WEALTH', 'CORPORATE'], weights=[70, 20, 10])[0],
            random.choices(['ACTIVE', 'DORMANT'], weights=[95, 5])[0],
            customer_since.date(),
            random.choices(['VERIFIED', 'PENDING', 'EXPIRED'], weights=[90, 5, 5])[0],
            (datetime.now() - timedelta(days=random.randint(0, 365))).date(),
            random.choice(['LOW', 'MEDIUM', 'HIGH']),
            f'RM{random.randint(1, 50):03d}',
            f'BR{random.randint(1, 20):03d}',
            customer_since,
            datetime.now()
        ))
    
    return customers

def generate_accounts(num_accounts, customer_ids):
    """Generate account data"""
    print(f"💳 Generating {num_accounts:,} accounts...")
    
    accounts = []
    for i in tqdm(range(num_accounts)):
        customer_id = random.choice(customer_ids)
        product_type = random.choices(
            ['SAVINGS', 'CURRENT', 'FIXED_DEPOSIT', 'CREDIT_CARD'],
            weights=[40, 30, 20, 10]
        )[0]
        
        balance = random.uniform(1000, 100000)
        opening_date = fake.date_between(start_date='-10y', end_date='today')
        
        accounts.append((
            f'ACC-{i:07d}',
            customer_id,
            f'{product_type} Account',
            product_type[:4],
            f'PRD{random.randint(100, 999)}',
            f'{product_type} Product',
            'SGD',
            round(balance, 2),
            round(balance, 2),
            0,
            round(balance * 0.9, 2) if product_type == 'CREDIT_CARD' else 0,
            random.choices(['ACTIVE', 'DORMANT', 'CLOSED'], weights=[85, 10, 5])[0],
            opening_date,
            fake.date_between(start_date=opening_date, end_date='today'),
            round(random.uniform(0.5, 3.5), 4),
            f'BR{random.randint(1, 20):03d}',
            None,
            None,
            opening_date,
            datetime.now()
        ))
    
    return accounts

def generate_loans(num_loans, customer_ids):
    """Generate loan data"""
    print(f"🏦 Generating {num_loans:,} loans...")
    
    loans = []
    for i in tqdm(range(num_loans)):
        customer_id = random.choice(customer_ids)
        loan_type = random.choices(
            ['PERSONAL', 'MORTGAGE', 'AUTO', 'BUSINESS'],
            weights=[40, 30, 20, 10]
        )[0]
        
        if loan_type == 'MORTGAGE':
            principal = random.uniform(200000, 1000000)
            term = random.choice([120, 180, 240, 300])
            rate = random.uniform(2.5, 4.5)
        elif loan_type == 'AUTO':
            principal = random.uniform(30000, 150000)
            term = random.choice([36, 48, 60, 72])
            rate = random.uniform(3.5, 6.5)
        else:
            principal = random.uniform(5000, 50000)
            term = random.choice([12, 24, 36, 48, 60])
            rate = random.uniform(6.0, 12.0)
        
        start_date = fake.date_between(start_date='-5y', end_date='today')
        maturity_date = start_date + timedelta(days=term*30)
        
        monthly_rate = rate / 12 / 100
        emi = (principal * monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
        
        months_elapsed = (datetime.now().date() - start_date).days // 30
        payments_made = min(months_elapsed, term)
        outstanding = principal * ((1 + monthly_rate)**term - (1 + monthly_rate)**payments_made) / ((1 + monthly_rate)**term - 1)
        outstanding = max(0, outstanding)
        
        dpd = 0
        if random.random() < 0.05:
            dpd = random.choices([0, 15, 45, 75], weights=[50, 25, 15, 10])[0]
        
        loan_status = 'CURRENT' if dpd == 0 else 'DELINQUENT'
        if outstanding == 0:
            loan_status = 'CLOSED'
        
        loans.append((
            f'LN-{i:08d}',
            customer_id,
            f'ACC-{random.randint(0, num_loans):07d}',
            loan_type,
            f'LN{random.randint(100, 999)}',
            f'{loan_type} Loan',
            'SGD',
            round(principal, 2),
            round(outstanding, 2),
            round(rate, 4),
            random.choice(['FIXED', 'FLOATING']),
            term,
            round(emi, 2),
            start_date,
            maturity_date,
            start_date + timedelta(days=(payments_made + 1) * 30),
            payments_made,
            term - payments_made,
            dpd,
            round(emi * (dpd // 30), 2) if dpd > 0 else 0,
            loan_status,
            random.choice(['PROPERTY', 'VEHICLE', 'DEPOSITS', 'UNSECURED']),
            round(principal * random.uniform(1.2, 1.8), 2),
            round(random.uniform(0.5, 0.9), 4),
            start_date - timedelta(days=random.randint(7, 30)),
            f'OFFICER{random.randint(1, 100):03d}',
            start_date,
            datetime.now()
        ))
    
    return loans

def bulk_insert(connection, table_name, data, batch_size=1000):
    """Bulk insert data into Oracle"""
    cursor = connection.cursor()
    
    total_rows = len(data)
    print(f"📥 Inserting {total_rows:,} rows into {table_name}...")
    
    # Get column count
    col_count = len(data[0])
    placeholders = ', '.join([f':{i+1}' for i in range(col_count)])
    sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
    
    # Batch insert
    for i in tqdm(range(0, total_rows, batch_size)):
        batch = data[i:i+batch_size]
        cursor.executemany(sql, batch)
        connection.commit()
    
    cursor.close()
    print(f"✅ Inserted {total_rows:,} rows\n")

def main():
    # Connect
    conn = get_oracle_connection()
    if not conn:
        return
    
    # Create schema
    create_schema(conn)
    
    # Generate data
    print("🎲 Generating sample data...\n")
    customers = generate_customers(NUM_CUSTOMERS)
    customer_ids = [c[0] for c in customers]
    
    accounts = generate_accounts(NUM_ACCOUNTS, customer_ids)
    loans = generate_loans(NUM_LOANS, customer_ids)
    
    # Load data
    print("📤 Loading data to Oracle Cloud...\n")
    bulk_insert(conn, 'T24_CUSTOMER', customers)
    bulk_insert(conn, 'T24_ACCOUNT', accounts)
    bulk_insert(conn, 'T24_LOAN', loans)
    
    # Verify
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM T24_CUSTOMER")
    cust_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM T24_ACCOUNT")
    acc_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM T24_LOAN")
    loan_count = cursor.fetchone()[0]
    cursor.close()
    
    print("=" * 70)
    print("🎉 Data Load Complete!")
    print("=" * 70)
    print(f"Customers: {cust_count:,}")
    print(f"Accounts:  {acc_count:,}")
    print(f"Loans:     {loan_count:,}")
    print("\n✅ Oracle Cloud is ready for Snowflake Openflow CDC ingestion!")
    
    conn.close()

if __name__ == "__main__":
    main()
