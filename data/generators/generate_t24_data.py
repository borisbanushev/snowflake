#!/usr/bin/env python3
"""
Generate sample T24 Core Banking data for Oracle database
Generates 100K customers with realistic financial data
"""

import cx_Oracle
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from tqdm import tqdm

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Configuration
NUM_CUSTOMERS = 100000
NUM_ACCOUNTS = 180000  # 1.8 per customer
NUM_LOANS = 35000  # 35% have loans
TRANSACTIONS_PER_ACCOUNT = 50

# Oracle connection
def get_oracle_connection():
    """Connect to Oracle database"""
    try:
        connection = cx_Oracle.connect(
            user='t24user',
            password='T24UserPass!',
            dsn='localhost:1521/XE'
        )
        print("✓ Connected to Oracle T24 database")
        return connection
    except Exception as e:
        print(f"✗ Failed to connect to Oracle: {e}")
        print("Make sure Docker container is running: docker-compose up -d")
        return None

def generate_customers(num_customers):
    """Generate customer master data"""
    print(f"\nGenerating {num_customers:,} customers...")
    
    customers = []
    for i in tqdm(range(num_customers)):
        # Credit score follows beta distribution (mean ~680)
        credit_score = int(np.random.beta(5, 3) * 550 + 300)
        
        # Age distribution
        age = int(np.random.normal(40, 15))
        age = max(18, min(80, age))
        dob = datetime.now() - timedelta(days=age*365.25)
        
        # Customer since (1-20 years ago)
        years_customer = random.randint(1, 20)
        customer_since = datetime.now() - timedelta(days=years_customer*365)
        
        # Risk category based on credit score
        if credit_score >= 720:
            risk_cat = 'LOW'
        elif credit_score >= 650:
            risk_cat = 'MEDIUM'
        else:
            risk_cat = 'HIGH'
        
        customers.append({
            'CUSTOMER_ID': f'CUS-{i:06d}',
            'MNEMONIC': fake.user_name()[:20],
            'SHORT_NAME': fake.name()[:50],
            'NAME_1': fake.name(),
            'NAME_2': '',
            'GENDER': random.choice(['M', 'F']),
            'DATE_OF_BIRTH': dob.date(),
            'MARITAL_STATUS': random.choice(['SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED']),
            'NATIONALITY': 'SGP',
            'RESIDENCE': 'SGP',
            'SECTOR': random.choice(['1001', '1002', '2001', '2002']),
            'INDUSTRY': random.choice(['TECH', 'FINANCE', 'HEALTH', 'RETAIL', 'MANUF']),
            'TARGET_MARKET': random.choices(['RETAIL', 'WEALTH', 'CORPORATE'], weights=[70, 20, 10])[0],
            'CUSTOMER_STATUS': random.choices(['ACTIVE', 'DORMANT'], weights=[95, 5])[0],
            'CUSTOMER_SINCE': customer_since.date(),
            'KYC_STATUS': random.choices(['VERIFIED', 'PENDING', 'EXPIRED'], weights=[90, 5, 5])[0],
            'KYC_LAST_REVIEW': (datetime.now() - timedelta(days=random.randint(0, 365))).date(),
            'RISK_CATEGORY': risk_cat,
            'RELATIONSHIP_MANAGER': f'RM{random.randint(1, 50):03d}',
            'BRANCH_CODE': f'BR{random.randint(1, 20):03d}',
            'CREATED_DATE': customer_since,
            'MODIFIED_DATE': datetime.now()
        })
    
    return pd.DataFrame(customers)

def generate_accounts(customers_df, num_accounts):
    """Generate account data"""
    print(f"\nGenerating {num_accounts:,} accounts...")
    
    accounts = []
    customer_ids = customers_df['CUSTOMER_ID'].tolist()
    
    for i in tqdm(range(num_accounts)):
        customer_id = random.choice(customer_ids)
        
        # Account types
        product_type = random.choices(
            ['SAVINGS', 'CURRENT', 'FIXED_DEPOSIT', 'CREDIT_CARD'],
            weights=[40, 30, 20, 10]
        )[0]
        
        # Balance based on customer segment
        customer_segment = customers_df[customers_df['CUSTOMER_ID'] == customer_id]['TARGET_MARKET'].values[0]
        if customer_segment == 'WEALTH':
            balance = random.uniform(50000, 500000)
        elif customer_segment == 'RETAIL':
            balance = random.uniform(1000, 50000)
        else:
            balance = random.uniform(10000, 200000)
        
        opening_date = fake.date_between(start_date='-10y', end_date='today')
        
        accounts.append({
            'ACCOUNT_ID': f'ACC-{i:07d}',
            'CUSTOMER_ID': customer_id,
            'ACCOUNT_TITLE': f'{product_type} Account',
            'CATEGORY': product_type[:4],
            'PRODUCT_CODE': f'PRD{random.randint(100, 999)}',
            'PRODUCT_NAME': f'{product_type} Product',
            'CURRENCY': 'SGD',
            'WORKING_BALANCE': round(balance, 2),
            'ONLINE_ACTUAL_BAL': round(balance, 2),
            'LOCKED_AMOUNT': 0,
            'AVAILABLE_LIMIT': round(balance * 0.9, 2) if product_type == 'CREDIT_CARD' else 0,
            'ACCOUNT_STATUS': random.choices(['ACTIVE', 'DORMANT', 'CLOSED'], weights=[85, 10, 5])[0],
            'OPENING_DATE': opening_date,
            'LAST_ACTIVITY_DATE': fake.date_between(start_date=opening_date, end_date='today'),
            'INTEREST_RATE': round(random.uniform(0.5, 3.5), 4),
            'BRANCH_CODE': f'BR{random.randint(1, 20):03d}',
            'JOINT_HOLDER_1': None,
            'JOINT_HOLDER_2': None,
            'CREATED_DATE': opening_date,
            'MODIFIED_DATE': datetime.now()
        })
    
    return pd.DataFrame(accounts)

def generate_loans(customers_df, num_loans):
    """Generate loan data"""
    print(f"\nGenerating {num_loans:,} loans...")
    
    loans = []
    customer_ids = customers_df['CUSTOMER_ID'].tolist()
    
    for i in tqdm(range(num_loans)):
        customer_id = random.choice(customer_ids)
        risk_cat = customers_df[customers_df['CUSTOMER_ID'] == customer_id]['RISK_CATEGORY'].values[0]
        
        # Loan parameters based on risk
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
        elif loan_type == 'BUSINESS':
            principal = random.uniform(50000, 500000)
            term = random.choice([36, 48, 60, 84])
            rate = random.uniform(5.0, 9.0)
        else:  # PERSONAL
            principal = random.uniform(5000, 50000)
            term = random.choice([12, 24, 36, 48, 60])
            rate = random.uniform(6.0, 12.0)
        
        # Adjust rate by risk
        if risk_cat == 'HIGH':
            rate += 2.0
        elif risk_cat == 'MEDIUM':
            rate += 1.0
        
        start_date = fake.date_between(start_date='-5y', end_date='today')
        maturity_date = start_date + timedelta(days=term*30)
        
        # Calculate EMI
        monthly_rate = rate / 12 / 100
        emi = (principal * monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
        
        # Payments made
        months_elapsed = (datetime.now().date() - start_date).days // 30
        payments_made = min(months_elapsed, term)
        
        # Outstanding principal
        outstanding = principal * ((1 + monthly_rate)**term - (1 + monthly_rate)**payments_made) / ((1 + monthly_rate)**term - 1)
        outstanding = max(0, outstanding)
        
        # Days past due (5% delinquency rate, correlated with risk)
        delinquency_prob = 0.02 if risk_cat == 'LOW' else (0.05 if risk_cat == 'MEDIUM' else 0.12)
        if random.random() < delinquency_prob:
            dpd = random.choices([0, 15, 45, 75, 120], weights=[50, 25, 15, 7, 3])[0]
        else:
            dpd = 0
        
        loan_status = 'CURRENT' if dpd == 0 else ('DELINQUENT' if dpd < 90 else 'DEFAULT')
        if outstanding == 0:
            loan_status = 'CLOSED'
        
        loans.append({
            'LOAN_ID': f'LN-{i:08d}',
            'CUSTOMER_ID': customer_id,
            'ACCOUNT_ID': f'ACC-{random.randint(0, 180000):07d}',
            'LOAN_TYPE': loan_type,
            'PRODUCT_CODE': f'LN{random.randint(100, 999)}',
            'PRODUCT_NAME': f'{loan_type} Loan',
            'CURRENCY': 'SGD',
            'PRINCIPAL_AMOUNT': round(principal, 2),
            'OUTSTANDING_PRINCIPAL': round(outstanding, 2),
            'INTEREST_RATE': round(rate, 4),
            'INTEREST_TYPE': random.choice(['FIXED', 'FLOATING']),
            'TERM_MONTHS': term,
            'MONTHLY_PAYMENT': round(emi, 2),
            'START_DATE': start_date,
            'MATURITY_DATE': maturity_date,
            'NEXT_PAYMENT_DATE': start_date + timedelta(days=(payments_made + 1) * 30),
            'PAYMENTS_MADE': payments_made,
            'PAYMENTS_REMAINING': term - payments_made,
            'DAYS_PAST_DUE': dpd,
            'ARREARS_AMOUNT': round(emi * (dpd // 30), 2) if dpd > 0 else 0,
            'LOAN_STATUS': loan_status,
            'COLLATERAL_TYPE': random.choice(['PROPERTY', 'VEHICLE', 'DEPOSITS', 'UNSECURED']),
            'COLLATERAL_VALUE': round(principal * random.uniform(1.2, 1.8), 2),
            'LTV_RATIO': round(principal / (principal * random.uniform(1.2, 1.8)), 4),
            'APPROVAL_DATE': start_date - timedelta(days=random.randint(7, 30)),
            'APPROVED_BY': f'OFFICER{random.randint(1, 100):03d}',
            'CREATED_DATE': start_date,
            'MODIFIED_DATE': datetime.now()
        })
    
    return pd.DataFrame(loans)

def insert_data_to_oracle(connection, customers_df, accounts_df, loans_df):
    """Insert generated data into Oracle"""
    cursor = connection.cursor()
    
    try:
        # Insert customers
        print("\nInserting customers into Oracle...")
        for _, row in tqdm(customers_df.iterrows(), total=len(customers_df)):
            cursor.execute("""
                INSERT INTO T24_CUSTOMER VALUES 
                (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22)
            """, tuple(row))
        
        connection.commit()
        print(f"✓ Inserted {len(customers_df):,} customers")
        
        # Insert accounts
        print("\nInserting accounts into Oracle...")
        for _, row in tqdm(accounts_df.iterrows(), total=len(accounts_df)):
            cursor.execute("""
                INSERT INTO T24_ACCOUNT VALUES 
                (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20)
            """, tuple(row))
        
        connection.commit()
        print(f"✓ Inserted {len(accounts_df):,} accounts")
        
        # Insert loans
        print("\nInserting loans into Oracle...")
        for _, row in tqdm(loans_df.iterrows(), total=len(loans_df)):
            cursor.execute("""
                INSERT INTO T24_LOAN VALUES 
                (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28)
            """, tuple(row))
        
        connection.commit()
        print(f"✓ Inserted {len(loans_df):,} loans")
        
    except Exception as e:
        print(f"✗ Error inserting data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    print("=" * 60)
    print("T24 Core Banking Data Generator")
    print("=" * 60)
    
    # Connect to Oracle
    conn = get_oracle_connection()
    if not conn:
        return
    
    # Generate data
    customers_df = generate_customers(NUM_CUSTOMERS)
    accounts_df = generate_accounts(customers_df, NUM_ACCOUNTS)
    loans_df = generate_loans(customers_df, NUM_LOANS)
    
    # Insert into Oracle
    insert_data_to_oracle(conn, customers_df, accounts_df, loans_df)
    
    # Summary
    print("\n" + "=" * 60)
    print("Data Generation Complete!")
    print("=" * 60)
    print(f"Customers: {len(customers_df):,}")
    print(f"Accounts:  {len(accounts_df):,}")
    print(f"Loans:     {len(loans_df):,}")
    print("\nData is now ready for Snowflake Openflow CDC ingestion")
    
    conn.close()

if __name__ == "__main__":
    main()
