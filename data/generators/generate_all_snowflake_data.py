#!/usr/bin/env python3
"""
Generate ALL datasets for Snowflake Credit Decisioning Platform
Outputs CSV files for direct upload to Snowflake
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os
from tqdm import tqdm
import uuid

# Initialize
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Configuration - REDUCED volumes for faster demo
NUM_CUSTOMERS = 3000
NUM_ACCOUNTS = 5400  # 1.8 per customer
NUM_LOANS = 1200  # 40% of customers
NUM_TRANSACTIONS = 30000
NUM_PAYMENT_SCHEDULES = 15000
NUM_DIGITAL_SESSIONS = 15000  # 5 per customer
NUM_DIGITAL_EVENTS = 60000  # 4 per session
NUM_CREDIT_INQUIRIES = 12000
NUM_TRADELINES = 18000  # 6 per customer

# Output directory
OUTPUT_DIR = 'data/generated_csv'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("🏦 SNOWFLAKE CREDIT DECISIONING - DATA GENERATOR")
print("=" * 80)
print(f"Generating {NUM_CUSTOMERS:,} customers with ALL related data")
print(f"Output directory: {OUTPUT_DIR}")
print("=" * 80)

# ============================================
# 1. DIGITAL BANKING DATA
# ============================================

def generate_digital_customer_profile(num_customers):
    """Generate digital banking customer profiles"""
    print("\n📱 Generating Digital Customer Profiles...")
    
    customers = []
    customer_ids = [f'CUS-{i:06d}' for i in range(num_customers)]
    
    for customer_id in tqdm(customer_ids):
        customers.append({
            'DIGITAL_ID': str(uuid.uuid4()),
            'CUSTOMER_ID': customer_id,
            'EMAIL': fake.email(),
            'MOBILE_NUMBER': fake.phone_number()[:20],
            'USERNAME': fake.user_name()[:30],
            'REGISTRATION_DATE': fake.date_time_between(start_date='-3y', end_date='now'),
            'LAST_LOGIN': fake.date_time_between(start_date='-30d', end_date='now'),
            'LOGIN_COUNT': random.randint(5, 500),
            'FAILED_LOGIN_COUNT': random.randint(0, 5),
            'MFA_ENABLED': random.choice([True, False]),
            'MFA_TYPE': random.choice(['SMS', 'APP', 'EMAIL', None]),
            'DEVICE_COUNT': random.randint(1, 3),
            'PRIMARY_DEVICE_TYPE': random.choice(['iOS', 'Android', 'Web']),
            'BIOMETRIC_ENABLED': random.choice([True, False]),
            'PUSH_NOTIFICATIONS': random.choice([True, False]),
            'EMAIL_VERIFIED': random.choice([True, False]),
            'MOBILE_VERIFIED': random.choice([True, False]),
            'EKYC_STATUS': random.choice(['VERIFIED', 'PENDING', 'REJECTED']),
            'EKYC_DATE': fake.date_time_between(start_date='-2y', end_date='now') if random.random() > 0.1 else None,
            'PREFERRED_LANGUAGE': random.choice(['EN', 'ZH', 'MS', 'TA']),
            'TIMEZONE': 'Asia/Singapore',
            'CREATED_DATE': fake.date_time_between(start_date='-3y', end_date='now'),
            'MODIFIED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(customers)
    df.to_csv(f'{OUTPUT_DIR}/digital_customer_profile.csv', index=False)
    print(f"✓ Created {len(df):,} digital customer profiles")
    return df

def generate_digital_sessions(digital_df):
    """Generate digital banking sessions"""
    print("\n📱 Generating Digital Sessions...")
    
    sessions = []
    customer_ids = digital_df['CUSTOMER_ID'].tolist()
    digital_ids = dict(zip(digital_df['CUSTOMER_ID'], digital_df['DIGITAL_ID']))
    
    for _ in tqdm(range(NUM_DIGITAL_SESSIONS)):
        customer_id = random.choice(customer_ids)
        session_start = fake.date_time_between(start_date='-90d', end_date='now')
        duration = random.randint(30, 3600)
        
        sessions.append({
            'SESSION_ID': str(uuid.uuid4()),
            'DIGITAL_ID': digital_ids[customer_id],
            'CUSTOMER_ID': customer_id,
            'SESSION_START': session_start,
            'SESSION_END': session_start + timedelta(seconds=duration),
            'DURATION_SECONDS': duration,
            'DEVICE_ID': fake.uuid4(),
            'DEVICE_TYPE': random.choice(['iOS', 'Android', 'Web', 'Tablet']),
            'DEVICE_MODEL': random.choice(['iPhone 14', 'Samsung S23', 'iPad', 'Pixel 7', 'Chrome']),
            'OS_VERSION': random.choice(['iOS 17', 'Android 14', 'Windows 11', 'macOS 14']),
            'APP_VERSION': f'4.{random.randint(0, 9)}.{random.randint(0, 20)}',
            'IP_ADDRESS': fake.ipv4(),
            'GEOLOCATION_LAT': round(random.uniform(1.2, 1.5), 7),
            'GEOLOCATION_LON': round(random.uniform(103.6, 104.0), 7),
            'CITY': random.choice(['Singapore', 'Jurong', 'Tampines', 'Woodlands']),
            'COUNTRY': 'SGP',
            'PAGES_VIEWED': random.randint(1, 20),
            'TRANSACTIONS_INITIATED': random.randint(0, 5),
            'TRANSACTIONS_COMPLETED': random.randint(0, 5),
            'ERROR_COUNT': random.randint(0, 3),
            'SESSION_QUALITY_SCORE': round(random.uniform(70, 100), 2),
            'EXIT_REASON': random.choice(['LOGOUT', 'TIMEOUT', 'COMPLETED', 'ERROR']),
            'CREATED_DATE': session_start
        })
    
    df = pd.DataFrame(sessions)
    df.to_csv(f'{OUTPUT_DIR}/digital_session.csv', index=False)
    print(f"✓ Created {len(df):,} digital sessions")
    return df

def generate_digital_events(sessions_df):
    """Generate digital banking events"""
    print("\n📱 Generating Digital Events...")
    
    events = []
    session_data = sessions_df[['SESSION_ID', 'DIGITAL_ID', 'CUSTOMER_ID', 'SESSION_START']].to_dict('records')
    
    for _ in tqdm(range(NUM_DIGITAL_EVENTS)):
        session = random.choice(session_data)
        event_types = ['PAGE_VIEW', 'BUTTON_CLICK', 'TRANSACTION', 'SEARCH', 'FORM_SUBMIT']
        
        events.append({
            'EVENT_ID': str(uuid.uuid4()),
            'SESSION_ID': session['SESSION_ID'],
            'DIGITAL_ID': session['DIGITAL_ID'],
            'CUSTOMER_ID': session['CUSTOMER_ID'],
            'EVENT_TYPE': random.choice(event_types),
            'EVENT_NAME': random.choice(['account_view', 'transfer', 'bill_payment', 'balance_check', 'statement_download']),
            'EVENT_TIMESTAMP': session['SESSION_START'] + timedelta(seconds=random.randint(0, 3600)),
            'PAGE_NAME': random.choice(['Dashboard', 'Accounts', 'Transfer', 'Bills', 'Profile']),
            'ELEMENT_ID': f'btn_{random.randint(1, 100)}',
            'EVENT_DATA': '{"amount": 1000, "currency": "SGD"}',
            'RESPONSE_TIME_MS': random.randint(50, 2000),
            'SUCCESS': random.choice([True, True, True, False]),
            'ERROR_CODE': None if random.random() > 0.1 else f'ERR_{random.randint(100, 999)}',
            'ERROR_MESSAGE': None if random.random() > 0.1 else 'Timeout error',
            'CREATED_DATE': session['SESSION_START']
        })
    
    df = pd.DataFrame(events)
    df.to_csv(f'{OUTPUT_DIR}/digital_event.csv', index=False)
    print(f"✓ Created {len(df):,} digital events")
    return df

def generate_digital_kyc(digital_df):
    """Generate KYC documents"""
    print("\n📱 Generating Digital KYC Documents...")
    
    kyc_docs = []
    for _, row in tqdm(digital_df.iterrows(), total=len(digital_df)):
        issue_date = fake.date_between(start_date='-10y', end_date='-1y')
        
        kyc_docs.append({
            'DOCUMENT_ID': str(uuid.uuid4()),
            'DIGITAL_ID': row['DIGITAL_ID'],
            'CUSTOMER_ID': row['CUSTOMER_ID'],
            'DOCUMENT_TYPE': random.choice(['PASSPORT', 'NRIC', 'DRIVERS_LICENSE']),
            'DOCUMENT_NUMBER': f'{fake.bothify(text="??######")}',
            'ISSUING_COUNTRY': 'SGP',
            'ISSUE_DATE': issue_date,
            'EXPIRY_DATE': issue_date + timedelta(days=3650),
            'UPLOAD_DATE': fake.date_time_between(start_date='-2y', end_date='now'),
            'VERIFICATION_STATUS': random.choice(['VERIFIED', 'PENDING', 'REJECTED']),
            'VERIFICATION_DATE': fake.date_time_between(start_date='-2y', end_date='now'),
            'VERIFICATION_METHOD': random.choice(['AI', 'MANUAL', 'THIRD_PARTY']),
            'CONFIDENCE_SCORE': round(random.uniform(85, 99.9), 2),
            'REJECTION_REASON': None if random.random() > 0.1 else 'Document unclear',
            'FACE_MATCH_SCORE': round(random.uniform(90, 99.9), 2),
            'LIVENESS_CHECK': random.choice([True, False]),
            'CREATED_DATE': fake.date_time_between(start_date='-2y', end_date='now'),
            'MODIFIED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(kyc_docs)
    df.to_csv(f'{OUTPUT_DIR}/digital_kyc_document.csv', index=False)
    print(f"✓ Created {len(df):,} KYC documents")
    return df

# ============================================
# 2. T24 CORE BANKING DATA
# ============================================

def generate_t24_customers(num_customers):
    """Generate T24 customer master data"""
    print("\n🏦 Generating T24 Customers...")
    
    customers = []
    for i in tqdm(range(num_customers)):
        age = int(np.random.normal(40, 15))
        age = max(18, min(80, age))
        dob = datetime.now() - timedelta(days=age*365.25)
        
        years_customer = random.randint(1, 20)
        customer_since = datetime.now() - timedelta(days=years_customer*365)
        
        # Credit score distribution
        credit_score = int(np.random.beta(5, 3) * 550 + 300)
        risk_cat = 'LOW' if credit_score >= 720 else ('MEDIUM' if credit_score >= 650 else 'HIGH')
        
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
    
    df = pd.DataFrame(customers)
    df.to_csv(f'{OUTPUT_DIR}/t24_customer.csv', index=False)
    print(f"✓ Created {len(df):,} T24 customers")
    return df

def generate_t24_accounts(customers_df):
    """Generate T24 accounts"""
    print("\n🏦 Generating T24 Accounts...")
    
    accounts = []
    customer_ids = customers_df['CUSTOMER_ID'].tolist()
    customer_segments = dict(zip(customers_df['CUSTOMER_ID'], customers_df['TARGET_MARKET']))
    
    for i in tqdm(range(NUM_ACCOUNTS)):
        customer_id = random.choice(customer_ids)
        segment = customer_segments[customer_id]
        
        product_type = random.choices(
            ['SAVINGS', 'CURRENT', 'FIXED_DEPOSIT', 'CREDIT_CARD'],
            weights=[40, 30, 20, 10]
        )[0]
        
        # Balance based on segment
        if segment == 'WEALTH':
            balance = random.uniform(50000, 500000)
        elif segment == 'RETAIL':
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
    
    df = pd.DataFrame(accounts)
    df.to_csv(f'{OUTPUT_DIR}/t24_account.csv', index=False)
    print(f"✓ Created {len(df):,} T24 accounts")
    return df

def generate_t24_loans(customers_df):
    """Generate T24 loans"""
    print("\n🏦 Generating T24 Loans...")
    
    loans = []
    customer_data = customers_df[['CUSTOMER_ID', 'RISK_CATEGORY']].to_dict('records')
    
    for i in tqdm(range(NUM_LOANS)):
        customer = random.choice(customer_data)
        risk_cat = customer['RISK_CATEGORY']
        
        loan_type = random.choices(
            ['PERSONAL', 'MORTGAGE', 'AUTO', 'BUSINESS'],
            weights=[40, 30, 20, 10]
        )[0]
        
        # Loan parameters
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
        if monthly_rate > 0:
            emi = (principal * monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
        else:
            emi = principal / term
        
        # Payments made
        months_elapsed = (datetime.now().date() - start_date).days // 30
        payments_made = min(months_elapsed, term)
        
        # Outstanding principal
        if monthly_rate > 0 and payments_made < term:
            outstanding = principal * ((1 + monthly_rate)**term - (1 + monthly_rate)**payments_made) / ((1 + monthly_rate)**term - 1)
        else:
            outstanding = 0
        outstanding = max(0, outstanding)
        
        # Delinquency
        delinquency_prob = 0.02 if risk_cat == 'LOW' else (0.05 if risk_cat == 'MEDIUM' else 0.12)
        dpd = random.choices([0, 15, 45, 75, 120], weights=[50, 25, 15, 7, 3])[0] if random.random() < delinquency_prob else 0
        
        loan_status = 'CURRENT' if dpd == 0 else ('DELINQUENT' if dpd < 90 else 'DEFAULT')
        if outstanding == 0:
            loan_status = 'CLOSED'
        
        loans.append({
            'LOAN_ID': f'LN-{i:08d}',
            'CUSTOMER_ID': customer['CUSTOMER_ID'],
            'ACCOUNT_ID': f'ACC-{random.randint(0, NUM_ACCOUNTS-1):07d}',
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
    
    df = pd.DataFrame(loans)
    df.to_csv(f'{OUTPUT_DIR}/t24_loan.csv', index=False)
    print(f"✓ Created {len(df):,} T24 loans")
    return df

def generate_t24_transactions(accounts_df):
    """Generate T24 transactions"""
    print("\n🏦 Generating T24 Transactions...")
    
    transactions = []
    account_ids = accounts_df['ACCOUNT_ID'].tolist()
    account_customers = dict(zip(accounts_df['ACCOUNT_ID'], accounts_df['CUSTOMER_ID']))
    
    for i in tqdm(range(NUM_TRANSACTIONS)):
        account_id = random.choice(account_ids)
        txn_type = random.choice(['DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'PAYMENT', 'FEE'])
        amount = random.uniform(10, 5000)
        value_date = fake.date_between(start_date='-1y', end_date='today')
        
        transactions.append({
            'TRANSACTION_ID': f'TXN-{i:010d}',
            'ACCOUNT_ID': account_id,
            'CUSTOMER_ID': account_customers[account_id],
            'TRANSACTION_TYPE': txn_type,
            'TRANSACTION_CODE': f'TC{random.randint(100, 999)}',
            'TRANSACTION_DESC': f'{txn_type} transaction',
            'AMOUNT': round(amount if txn_type in ['DEPOSIT', 'TRANSFER'] else -amount, 2),
            'CURRENCY': 'SGD',
            'AMOUNT_LCY': round(amount if txn_type in ['DEPOSIT', 'TRANSFER'] else -amount, 2),
            'EXCHANGE_RATE': 1.0,
            'VALUE_DATE': value_date,
            'BOOKING_DATE': value_date,
            'PROCESSING_TIME': datetime.combine(value_date, datetime.min.time()) + timedelta(hours=random.randint(9, 17)),
            'BALANCE_AFTER': round(random.uniform(1000, 50000), 2),
            'CHANNEL': random.choice(['MOBILE', 'ATM', 'BRANCH', 'INTERNET', 'POS']),
            'MERCHANT_NAME': fake.company() if txn_type == 'PAYMENT' else None,
            'MERCHANT_CATEGORY': random.choice(['RETAIL', 'FOOD', 'TRAVEL', 'UTILITIES']) if txn_type == 'PAYMENT' else None,
            'COUNTERPARTY_ACCT': f'ACC-{random.randint(0, NUM_ACCOUNTS-1):07d}' if txn_type == 'TRANSFER' else None,
            'COUNTERPARTY_NAME': fake.name() if txn_type == 'TRANSFER' else None,
            'COUNTERPARTY_BANK': random.choice(['DBS', 'OCBC', 'UOB', 'MAYBANK']) if txn_type == 'TRANSFER' else None,
            'REFERENCE': f'REF{random.randint(100000, 999999)}',
            'REVERSAL_FLAG': 0,
            'REVERSED_TXN_ID': None,
            'CREATED_DATE': datetime.combine(value_date, datetime.min.time())
        })
    
    df = pd.DataFrame(transactions)
    df.to_csv(f'{OUTPUT_DIR}/t24_transaction.csv', index=False)
    print(f"✓ Created {len(df):,} T24 transactions")
    return df

def generate_t24_payment_schedule(loans_df):
    """Generate payment schedules for loans"""
    print("\n🏦 Generating T24 Payment Schedules...")
    
    schedules = []
    for _ in tqdm(range(NUM_PAYMENT_SCHEDULES)):
        loan = loans_df.sample(1).iloc[0]
        installment_num = random.randint(1, loan['TERM_MONTHS'])
        due_date = loan['START_DATE'] + timedelta(days=installment_num*30)
        
        principal_due = loan['MONTHLY_PAYMENT'] * 0.7
        interest_due = loan['MONTHLY_PAYMENT'] * 0.3
        
        # Payment status
        if due_date < datetime.now().date():
            paid_prob = 0.85 if loan['LOAN_STATUS'] == 'CURRENT' else 0.3
            paid = random.random() < paid_prob
            status = 'PAID' if paid else 'OVERDUE'
        else:
            paid = False
            status = 'SCHEDULED'
        
        schedules.append({
            'SCHEDULE_ID': f'SCH-{len(schedules):010d}',
            'LOAN_ID': loan['LOAN_ID'],
            'CUSTOMER_ID': loan['CUSTOMER_ID'],
            'INSTALLMENT_NUMBER': installment_num,
            'DUE_DATE': due_date,
            'PRINCIPAL_DUE': round(principal_due, 2),
            'INTEREST_DUE': round(interest_due, 2),
            'TOTAL_DUE': round(loan['MONTHLY_PAYMENT'], 2),
            'PRINCIPAL_PAID': round(principal_due, 2) if paid else 0,
            'INTEREST_PAID': round(interest_due, 2) if paid else 0,
            'TOTAL_PAID': round(loan['MONTHLY_PAYMENT'], 2) if paid else 0,
            'PAYMENT_DATE': due_date if paid else None,
            'PAYMENT_STATUS': status,
            'DAYS_LATE': max(0, (datetime.now().date() - due_date).days) if status == 'OVERDUE' else 0,
            'PENALTY_AMOUNT': round(random.uniform(10, 100), 2) if status == 'OVERDUE' else 0,
            'CREATED_DATE': loan['START_DATE'],
            'MODIFIED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(schedules)
    df.to_csv(f'{OUTPUT_DIR}/t24_payment_schedule.csv', index=False)
    print(f"✓ Created {len(df):,} payment schedules")
    return df

def generate_t24_collateral(loans_df):
    """Generate collateral records"""
    print("\n🏦 Generating T24 Collateral...")
    
    collaterals = []
    secured_loans = loans_df[loans_df['COLLATERAL_TYPE'] != 'UNSECURED']
    
    for _, loan in tqdm(secured_loans.iterrows(), total=len(secured_loans)):
        valuation_date = fake.date_between(start_date=loan['START_DATE'], end_date='today')
        
        collaterals.append({
            'COLLATERAL_ID': f'COL-{len(collaterals):08d}',
            'LOAN_ID': loan['LOAN_ID'],
            'CUSTOMER_ID': loan['CUSTOMER_ID'],
            'COLLATERAL_TYPE': loan['COLLATERAL_TYPE'],
            'DESCRIPTION': f'{loan["COLLATERAL_TYPE"]} for {loan["LOAN_TYPE"]} loan',
            'ORIGINAL_VALUE': loan['COLLATERAL_VALUE'],
            'CURRENT_VALUE': round(loan['COLLATERAL_VALUE'] * random.uniform(0.9, 1.1), 2),
            'VALUATION_DATE': valuation_date,
            'VALUATION_SOURCE': random.choice(['INTERNAL', 'EXTERNAL', 'MARKET']),
            'CURRENCY': 'SGD',
            'LOCATION': fake.address() if loan['COLLATERAL_TYPE'] == 'PROPERTY' else None,
            'INSURANCE_POLICY': f'INS{random.randint(100000, 999999)}',
            'INSURANCE_EXPIRY': fake.date_between(start_date='today', end_date='+2y'),
            'LIEN_POSITION': 1,
            'REGISTRATION_REF': f'REG{random.randint(100000, 999999)}',
            'STATUS': loan['LOAN_STATUS'],
            'CREATED_DATE': loan['START_DATE'],
            'MODIFIED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(collaterals)
    df.to_csv(f'{OUTPUT_DIR}/t24_collateral.csv', index=False)
    print(f"✓ Created {len(df):,} collateral records")
    return df

# ============================================
# 3. CREDIT BUREAU DATA
# ============================================

def generate_credit_scores(customers_df):
    """Generate credit scores"""
    print("\n📊 Generating Credit Scores...")
    
    scores = []
    for _, customer in tqdm(customers_df.iterrows(), total=len(customers_df)):
        # Credit score aligned with risk category
        if customer['RISK_CATEGORY'] == 'LOW':
            score = int(np.random.normal(750, 30))
        elif customer['RISK_CATEGORY'] == 'MEDIUM':
            score = int(np.random.normal(680, 25))
        else:
            score = int(np.random.normal(600, 40))
        
        score = max(300, min(850, score))
        
        scores.append({
            'CREDIT_SCORE_ID': f'CS-{len(scores):08d}',
            'CUSTOMER_ID': customer['CUSTOMER_ID'],
            'BUREAU_NAME': random.choice(['EXPERIAN', 'EQUIFAX', 'TRANSUNION']),
            'SCORE': score,
            'SCORE_DATE': fake.date_between(start_date='-30d', end_date='today'),
            'SCORE_VERSION': '3.0',
            'DELINQUENCY_SCORE': random.randint(1, 100),
            'BANKRUPTCY_FLAG': random.choice([0, 0, 0, 1]),
            'FORECLOSURE_FLAG': 0,
            'TOTAL_ACCOUNTS': random.randint(3, 15),
            'OPEN_ACCOUNTS': random.randint(2, 10),
            'TOTAL_BALANCE': round(random.uniform(10000, 200000), 2),
            'AVAILABLE_CREDIT': round(random.uniform(5000, 100000), 2),
            'CREDIT_UTILIZATION': round(random.uniform(10, 80), 2),
            'OLDEST_ACCOUNT_MONTHS': random.randint(24, 240),
            'RECENT_INQUIRIES': random.randint(0, 5),
            'DEROGATORY_MARKS': random.randint(0, 3),
            'CREATED_DATE': datetime.now(),
            'MODIFIED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(scores)
    df.to_csv(f'{OUTPUT_DIR}/credit_score.csv', index=False)
    print(f"✓ Created {len(df):,} credit scores")
    return df

def generate_credit_inquiries(customers_df):
    """Generate credit inquiries"""
    print("\n📊 Generating Credit Inquiries...")
    
    inquiries = []
    customer_ids = customers_df['CUSTOMER_ID'].tolist()
    
    for _ in tqdm(range(NUM_CREDIT_INQUIRIES)):
        inquiries.append({
            'INQUIRY_ID': f'INQ-{len(inquiries):010d}',
            'CUSTOMER_ID': random.choice(customer_ids),
            'INQUIRY_DATE': fake.date_between(start_date='-2y', end_date='today'),
            'INQUIRY_TYPE': random.choice(['HARD', 'SOFT']),
            'CREDITOR_NAME': random.choice(['DBS Bank', 'OCBC Bank', 'UOB', 'Standard Chartered', 'Citibank']),
            'PRODUCT_TYPE': random.choice(['CREDIT_CARD', 'PERSONAL_LOAN', 'AUTO_LOAN', 'MORTGAGE']),
            'INQUIRY_AMOUNT': round(random.uniform(5000, 500000), 2) if random.random() > 0.3 else None,
            'INQUIRY_REASON': random.choice(['NEW_CREDIT', 'ACCOUNT_REVIEW', 'CREDIT_INCREASE']),
            'CREATED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(inquiries)
    df.to_csv(f'{OUTPUT_DIR}/credit_inquiry.csv', index=False)
    print(f"✓ Created {len(df):,} credit inquiries")
    return df

def generate_tradelines(customers_df):
    """Generate credit tradelines"""
    print("\n📊 Generating Tradelines...")
    
    tradelines = []
    customer_ids = customers_df['CUSTOMER_ID'].tolist()
    
    for _ in tqdm(range(NUM_TRADELINES)):
        open_date = fake.date_between(start_date='-15y', end_date='-1y')
        credit_limit = random.uniform(5000, 50000)
        balance = random.uniform(0, credit_limit * 0.8)
        
        tradelines.append({
            'TRADELINE_ID': f'TL-{len(tradelines):010d}',
            'CUSTOMER_ID': random.choice(customer_ids),
            'CREDITOR_NAME': random.choice(['DBS', 'OCBC', 'UOB', 'Citi', 'HSBC', 'Standard Chartered']),
            'ACCOUNT_TYPE': random.choice(['CREDIT_CARD', 'INSTALLMENT_LOAN', 'LINE_OF_CREDIT', 'MORTGAGE']),
            'ACCOUNT_NUMBER': f'****{random.randint(1000, 9999)}',
            'ACCOUNT_STATUS': random.choices(['OPEN', 'CLOSED', 'CHARGED_OFF'], weights=[85, 10, 5])[0],
            'OPEN_DATE': open_date,
            'CLOSE_DATE': fake.date_between(start_date=open_date, end_date='today') if random.random() < 0.2 else None,
            'CREDIT_LIMIT': round(credit_limit, 2),
            'CURRENT_BALANCE': round(balance, 2),
            'HIGHEST_BALANCE': round(credit_limit * random.uniform(0.3, 0.95), 2),
            'PAYMENT_STATUS': random.choices(['CURRENT', 'LATE_30', 'LATE_60', 'LATE_90'], weights=[90, 6, 3, 1])[0],
            'MONTHLY_PAYMENT': round(random.uniform(100, 2000), 2),
            'LAST_PAYMENT_DATE': fake.date_between(start_date='-60d', end_date='today'),
            'LAST_PAYMENT_AMOUNT': round(random.uniform(100, 2000), 2),
            'CREATED_DATE': open_date,
            'MODIFIED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(tradelines)
    df.to_csv(f'{OUTPUT_DIR}/tradeline.csv', index=False)
    print(f"✓ Created {len(df):,} tradelines")
    return df

def generate_public_records(customers_df):
    """Generate public records (bankruptcies, liens)"""
    print("\n📊 Generating Public Records...")
    
    records = []
    # Only 10% of customers have public records
    sample_customers = customers_df.sample(frac=0.1)
    
    for _, customer in tqdm(sample_customers.iterrows(), total=len(sample_customers)):
        record_date = fake.date_between(start_date='-10y', end_date='-1y')
        
        records.append({
            'RECORD_ID': f'PR-{len(records):08d}',
            'CUSTOMER_ID': customer['CUSTOMER_ID'],
            'RECORD_TYPE': random.choice(['BANKRUPTCY', 'TAX_LIEN', 'JUDGMENT', 'FORECLOSURE']),
            'FILING_DATE': record_date,
            'CLOSE_DATE': fake.date_between(start_date=record_date, end_date='today') if random.random() > 0.3 else None,
            'STATUS': random.choice(['DISCHARGED', 'WITHDRAWN', 'SATISFIED', 'ACTIVE']),
            'AMOUNT': round(random.uniform(5000, 100000), 2),
            'COURT': fake.city() + ' Court',
            'CASE_NUMBER': f'CASE{random.randint(100000, 999999)}',
            'CREATED_DATE': record_date,
            'MODIFIED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(records)
    df.to_csv(f'{OUTPUT_DIR}/public_record.csv', index=False)
    print(f"✓ Created {len(df):,} public records")
    return df

# ============================================
# 4. REFERENCE DATA
# ============================================

def generate_country_codes():
    """Generate country code reference data"""
    print("\n🌍 Generating Country Codes...")
    
    countries = [
        ('SGP', 'Singapore', 'SG', 'Asia', 'SGD'),
        ('USA', 'United States', 'US', 'North America', 'USD'),
        ('GBR', 'United Kingdom', 'GB', 'Europe', 'GBP'),
        ('AUS', 'Australia', 'AU', 'Oceania', 'AUD'),
        ('MYS', 'Malaysia', 'MY', 'Asia', 'MYR'),
        ('CHN', 'China', 'CN', 'Asia', 'CNY'),
        ('JPN', 'Japan', 'JP', 'Asia', 'JPY'),
        ('IND', 'India', 'IN', 'Asia', 'INR'),
        ('IDN', 'Indonesia', 'ID', 'Asia', 'IDR'),
        ('THA', 'Thailand', 'TH', 'Asia', 'THB'),
    ]
    
    # Add more countries
    all_countries = []
    for code, name, iso2, region, currency in countries:
        all_countries.append({
            'COUNTRY_CODE': code,
            'COUNTRY_NAME': name,
            'ISO2_CODE': iso2,
            'REGION': region,
            'CURRENCY': currency,
            'ACTIVE': True,
            'CREATED_DATE': datetime.now()
        })
    
    # Add 240 more random countries
    for i in range(240):
        all_countries.append({
            'COUNTRY_CODE': f'C{i:03d}',
            'COUNTRY_NAME': fake.country(),
            'ISO2_CODE': fake.country_code(),
            'REGION': random.choice(['Asia', 'Europe', 'Americas', 'Africa', 'Oceania']),
            'CURRENCY': random.choice(['USD', 'EUR', 'GBP', 'SGD']),
            'ACTIVE': True,
            'CREATED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(all_countries)
    df.to_csv(f'{OUTPUT_DIR}/country_code.csv', index=False)
    print(f"✓ Created {len(df):,} country codes")
    return df

def generate_currency_codes():
    """Generate currency code reference data"""
    print("\n💱 Generating Currency Codes...")
    
    currencies = []
    major_currencies = [
        ('SGD', 'Singapore Dollar', 'S$', 2),
        ('USD', 'US Dollar', '$', 2),
        ('EUR', 'Euro', '€', 2),
        ('GBP', 'British Pound', '£', 2),
        ('JPY', 'Japanese Yen', '¥', 0),
        ('CNY', 'Chinese Yuan', '¥', 2),
        ('AUD', 'Australian Dollar', 'A$', 2),
        ('MYR', 'Malaysian Ringgit', 'RM', 2),
    ]
    
    for code, name, symbol, decimals in major_currencies:
        currencies.append({
            'CURRENCY_CODE': code,
            'CURRENCY_NAME': name,
            'SYMBOL': symbol,
            'DECIMAL_PLACES': decimals,
            'ACTIVE': True,
            'CREATED_DATE': datetime.now()
        })
    
    # Add 142 more currencies
    for i in range(142):
        currencies.append({
            'CURRENCY_CODE': f'CUR{i:03d}',
            'CURRENCY_NAME': f'Currency {i}',
            'SYMBOL': fake.currency_code(),
            'DECIMAL_PLACES': 2,
            'ACTIVE': random.choice([True, False]),
            'CREATED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(currencies)
    df.to_csv(f'{OUTPUT_DIR}/currency_code.csv', index=False)
    print(f"✓ Created {len(df):,} currency codes")
    return df

def generate_product_catalog():
    """Generate product catalog"""
    print("\n📦 Generating Product Catalog...")
    
    products = []
    product_types = [
        ('SAVINGS', 'Basic Savings Account', 0.5, 500, 'DEPOSIT'),
        ('PREMIUM_SAVINGS', 'Premium Savings Account', 1.5, 10000, 'DEPOSIT'),
        ('CURRENT', 'Current Account', 0.0, 1000, 'DEPOSIT'),
        ('FIXED_1Y', '1-Year Fixed Deposit', 2.5, 5000, 'DEPOSIT'),
        ('FIXED_3Y', '3-Year Fixed Deposit', 3.0, 5000, 'DEPOSIT'),
        ('CREDIT_CLASSIC', 'Classic Credit Card', 18.0, 0, 'CREDIT'),
        ('CREDIT_GOLD', 'Gold Credit Card', 16.0, 50000, 'CREDIT'),
        ('CREDIT_PLATINUM', 'Platinum Credit Card', 14.0, 100000, 'CREDIT'),
        ('PERSONAL_LOAN', 'Personal Loan', 8.5, 5000, 'LOAN'),
        ('AUTO_LOAN', 'Auto Loan', 5.5, 20000, 'LOAN'),
        ('MORTGAGE', 'Home Mortgage', 3.5, 200000, 'LOAN'),
        ('BUSINESS_LOAN', 'Business Term Loan', 7.0, 50000, 'LOAN'),
    ]
    
    for i, (code, name, rate, min_amount, category) in enumerate(product_types):
        products.append({
            'PRODUCT_CODE': code,
            'PRODUCT_NAME': name,
            'PRODUCT_CATEGORY': category,
            'INTEREST_RATE': rate,
            'MIN_AMOUNT': min_amount,
            'MAX_AMOUNT': min_amount * 100 if category == 'LOAN' else 0,
            'ACTIVE': True,
            'DESCRIPTION': f'{name} - competitive rates and flexible terms',
            'CREATED_DATE': datetime.now()
        })
    
    # Add more products
    for i in range(38):
        products.append({
            'PRODUCT_CODE': f'PRD{i+100:03d}',
            'PRODUCT_NAME': f'Product {i+100}',
            'PRODUCT_CATEGORY': random.choice(['DEPOSIT', 'CREDIT', 'LOAN', 'INVESTMENT']),
            'INTEREST_RATE': round(random.uniform(0.5, 15.0), 2),
            'MIN_AMOUNT': random.choice([500, 1000, 5000, 10000]),
            'MAX_AMOUNT': random.choice([50000, 100000, 500000, 1000000]),
            'ACTIVE': True,
            'DESCRIPTION': fake.catch_phrase(),
            'CREATED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(products)
    df.to_csv(f'{OUTPUT_DIR}/product_catalog.csv', index=False)
    print(f"✓ Created {len(df):,} products")
    return df

def generate_branches():
    """Generate branch directory"""
    print("\n🏢 Generating Branch Directory...")
    
    branches = []
    for i in range(1, 21):
        branches.append({
            'BRANCH_CODE': f'BR{i:03d}',
            'BRANCH_NAME': f'{fake.city()} Branch',
            'ADDRESS': fake.address(),
            'CITY': random.choice(['Singapore', 'Jurong', 'Tampines', 'Woodlands', 'Orchard']),
            'POSTAL_CODE': f'{random.randint(100000, 999999)}',
            'COUNTRY': 'SGP',
            'PHONE': fake.phone_number(),
            'EMAIL': f'branch{i:03d}@bank.com',
            'MANAGER': fake.name(),
            'OPENED_DATE': fake.date_between(start_date='-20y', end_date='-1y'),
            'ACTIVE': True,
            'CREATED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(branches)
    df.to_csv(f'{OUTPUT_DIR}/branch_directory.csv', index=False)
    print(f"✓ Created {len(df):,} branches")
    return df

def generate_relationship_managers():
    """Generate relationship managers"""
    print("\n👔 Generating Relationship Managers...")
    
    rms = []
    for i in range(1, 51):
        rms.append({
            'RM_CODE': f'RM{i:03d}',
            'RM_NAME': fake.name(),
            'EMAIL': f'rm{i:03d}@bank.com',
            'PHONE': fake.phone_number(),
            'BRANCH_CODE': f'BR{random.randint(1, 20):03d}',
            'SPECIALIZATION': random.choice(['RETAIL', 'WEALTH', 'CORPORATE', 'SME']),
            'ACTIVE_CUSTOMERS': random.randint(50, 200),
            'PORTFOLIO_VALUE': round(random.uniform(5000000, 50000000), 2),
            'HIRE_DATE': fake.date_between(start_date='-15y', end_date='-1y'),
            'ACTIVE': True,
            'CREATED_DATE': datetime.now()
        })
    
    df = pd.DataFrame(rms)
    df.to_csv(f'{OUTPUT_DIR}/relationship_manager.csv', index=False)
    print(f"✓ Created {len(df):,} relationship managers")
    return df

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main execution flow"""
    
    # 1. Digital Banking Data
    digital_df = generate_digital_customer_profile(NUM_CUSTOMERS)
    sessions_df = generate_digital_sessions(digital_df)
    generate_digital_events(sessions_df)
    generate_digital_kyc(digital_df)
    
    # 2. T24 Core Banking Data
    t24_customers_df = generate_t24_customers(NUM_CUSTOMERS)
    accounts_df = generate_t24_accounts(t24_customers_df)
    loans_df = generate_t24_loans(t24_customers_df)
    generate_t24_transactions(accounts_df)
    generate_t24_payment_schedule(loans_df)
    generate_t24_collateral(loans_df)
    
    # 3. Credit Bureau Data
    generate_credit_scores(t24_customers_df)
    generate_credit_inquiries(t24_customers_df)
    generate_tradelines(t24_customers_df)
    generate_public_records(t24_customers_df)
    
    # 4. Reference Data
    generate_country_codes()
    generate_currency_codes()
    generate_product_catalog()
    generate_branches()
    generate_relationship_managers()
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ DATA GENERATION COMPLETE!")
    print("=" * 80)
    print(f"\n📁 All CSV files saved to: {OUTPUT_DIR}")
    print(f"\n📊 Generated Tables:")
    
    csv_files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')])
    total_rows = 0
    for csv_file in csv_files:
        df = pd.read_csv(f'{OUTPUT_DIR}/{csv_file}')
        rows = len(df)
        total_rows += rows
        print(f"   • {csv_file:<35} {rows:>10,} rows")
    
    print(f"\n🎯 Total Records: {total_rows:,}")
    print("\n✨ Ready to upload to Snowflake!")
    print("=" * 80)

if __name__ == "__main__":
    main()
