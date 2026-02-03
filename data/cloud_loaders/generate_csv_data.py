#!/usr/bin/env python3
"""
Generate CSV files for Databricks upload
Creates 100K credit bureau and income verification records
"""

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

NUM_CUSTOMERS = 100000
OUTPUT_DIR = "../../databricks_csv_data"

print("=" * 70)
print("CSV Data Generator for Databricks")
print("=" * 70)
print(f"Records: {NUM_CUSTOMERS:,}")
print(f"Output: {OUTPUT_DIR}/")
print("=" * 70)
print()

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_credit_bureau_report(num_records):
    """Generate credit bureau reports"""
    print(f"📊 Generating {num_records:,} credit bureau reports...")
    
    data = []
    for i in tqdm(range(num_records)):
        # Credit score with realistic distribution
        score = int(np.random.beta(5, 3) * 550 + 300)
        score = max(300, min(850, score))
        
        total_accounts = random.randint(2, 20)
        open_accounts = random.randint(1, total_accounts)
        
        report_date = (datetime.now() - timedelta(days=random.randint(0, 90))).date()
        oldest_account_date = (datetime.now() - timedelta(days=random.randint(730, 7300))).date()
        newest_account_date = (datetime.now() - timedelta(days=random.randint(0, 730))).date()
        
        total_balance = round(random.uniform(5000, 150000), 2)
        total_credit_limit = round(random.uniform(20000, 300000), 2)
        utilization = round(total_balance / total_credit_limit, 4)
        
        data.append({
            'REPORT_ID': f'RPT-{i:08d}',
            'CUSTOMER_ID': f'CUS-{i:06d}',
            'BUREAU_NAME': random.choice(['EXPERIAN', 'EQUIFAX', 'TRANSUNION']),
            'REPORT_DATE': report_date,
            'CREDIT_SCORE': score,
            'CREDIT_SCORE_VERSION': 'FICO-8',
            'SCORE_FACTORS': 'Payment History;Credit Utilization;Length of History',
            'CREDIT_LIMIT_UTILIZATION': utilization,
            'TOTAL_ACCOUNTS': total_accounts,
            'OPEN_ACCOUNTS': open_accounts,
            'CLOSED_ACCOUNTS': total_accounts - open_accounts,
            'DELINQUENT_ACCOUNTS': random.randint(0, 2),
            'PUBLIC_RECORDS': random.randint(0, 1),
            'BANKRUPTCIES': 0 if random.random() > 0.05 else 1,
            'TAX_LIENS': 0,
            'JUDGMENTS': 0 if random.random() > 0.03 else 1,
            'COLLECTIONS': random.randint(0, 1),
            'INQUIRIES_LAST_6M': random.randint(0, 5),
            'INQUIRIES_LAST_12M': random.randint(0, 10),
            'OLDEST_ACCOUNT_DATE': oldest_account_date,
            'NEWEST_ACCOUNT_DATE': newest_account_date,
            'AVERAGE_ACCOUNT_AGE_MONTHS': random.randint(12, 120),
            'TOTAL_BALANCE': total_balance,
            'TOTAL_CREDIT_LIMIT': total_credit_limit,
            'TOTAL_MONTHLY_PAYMENT': round(random.uniform(500, 5000), 2),
            'DELINQUENCY_30_DAYS': random.randint(0, 3),
            'DELINQUENCY_60_DAYS': random.randint(0, 1),
            'DELINQUENCY_90_DAYS': random.randint(0, 1),
            'CREATED_TIMESTAMP': datetime.now(),
            'MODIFIED_TIMESTAMP': datetime.now()
        })
    
    return pd.DataFrame(data)

def generate_income_verification(num_records):
    """Generate income verification records"""
    print(f"💰 Generating {num_records:,} income verification records...")
    
    data = []
    for i in tqdm(range(num_records)):
        annual_income = round(random.uniform(30000, 500000), 2)
        verification_date = (datetime.now() - timedelta(days=random.randint(0, 180))).date()
        employment_start = (datetime.now() - timedelta(days=random.randint(365, 3650))).date()
        
        data.append({
            'VERIFICATION_ID': f'INC-{i:08d}',
            'CUSTOMER_ID': f'CUS-{i:06d}',
            'VERIFICATION_TYPE': random.choice(['EMPLOYMENT', 'SELF_EMPLOYED', 'INVESTMENT']),
            'VERIFICATION_DATE': verification_date,
            'EMPLOYER_NAME': fake.company(),
            'EMPLOYMENT_STATUS': random.choice(['FULL_TIME', 'PART_TIME', 'CONTRACT', 'SELF_EMPLOYED']),
            'JOB_TITLE': fake.job(),
            'EMPLOYMENT_START_DATE': employment_start,
            'EMPLOYMENT_SECTOR': random.choice(['TECH', 'FINANCE', 'HEALTHCARE', 'RETAIL', 'MANUFACTURING']),
            'ANNUAL_INCOME': annual_income,
            'MONTHLY_INCOME': round(annual_income / 12, 2),
            'INCOME_SOURCE': random.choice(['SALARY', 'BUSINESS', 'INVESTMENT', 'RENTAL']),
            'INCOME_STABILITY_SCORE': random.randint(60, 100),
            'VERIFICATION_METHOD': random.choice(['PAY_STUB', 'TAX_RETURN', 'BANK_STATEMENT', 'EMPLOYER_CALL']),
            'VERIFIED_BY': f'VERIFIER-{random.randint(1, 50):03d}',
            'VERIFICATION_STATUS': random.choices(['VERIFIED', 'PENDING', 'FAILED'], weights=[85, 10, 5])[0],
            'DOCUMENTS_PROVIDED': 'Pay Stub;Tax Return',
            'CONFIDENCE_LEVEL': random.choice(['HIGH', 'MEDIUM', 'LOW']),
            'NOTES': 'Verified successfully',
            'CREATED_TIMESTAMP': datetime.now()
        })
    
    return pd.DataFrame(data)

# Generate data
print("🎲 Generating data...\n")
credit_bureau_df = generate_credit_bureau_report(NUM_CUSTOMERS)
income_verification_df = generate_income_verification(NUM_CUSTOMERS)

# Save to CSV
print("\n💾 Saving CSV files...\n")

credit_bureau_file = f"{OUTPUT_DIR}/credit_bureau_report.csv"
income_file = f"{OUTPUT_DIR}/income_verification.csv"

credit_bureau_df.to_csv(credit_bureau_file, index=False)
print(f"✅ Saved: {credit_bureau_file}")
print(f"   Size: {os.path.getsize(credit_bureau_file) / 1024 / 1024:.1f} MB")
print(f"   Rows: {len(credit_bureau_df):,}")

income_verification_df.to_csv(income_file, index=False)
print(f"✅ Saved: {income_file}")
print(f"   Size: {os.path.getsize(income_file) / 1024 / 1024:.1f} MB")
print(f"   Rows: {len(income_verification_df):,}")

# Sample data
print("\n📊 Sample Data Preview:\n")
print("CREDIT_BUREAU_REPORT (first 3 rows):")
print(credit_bureau_df.head(3).to_string())
print("\nINCOME_VERIFICATION (first 3 rows):")
print(income_verification_df.head(3).to_string())

# Summary
print("\n" + "=" * 70)
print("✅ CSV Files Generated Successfully!")
print("=" * 70)
print(f"\nLocation: {OUTPUT_DIR}/")
print(f"Files:")
print(f"  1. credit_bureau_report.csv   ({len(credit_bureau_df):,} rows)")
print(f"  2. income_verification.csv    ({len(income_verification_df):,} rows)")
print(f"\nTotal: {len(credit_bureau_df) + len(income_verification_df):,} records")
print("\n" + "=" * 70)
print("Next Steps:")
print("=" * 70)
print("""
1. Go to Databricks: https://dbc-6730e836-5587.cloud.databricks.com

2. Navigate to: Data → sowcatalog → credit_bureau

3. Create tables (if not exists):
   - Click "+ Create" → "Table" → "Upload File"
   - Or use SQL Editor to create empty tables first

4. Upload CSV files:
   - credit_bureau_report.csv → CREDIT_BUREAU_REPORT table
   - income_verification.csv → INCOME_VERIFICATION table

5. Verify:
   SELECT COUNT(*) FROM sowcatalog.credit_bureau.CREDIT_BUREAU_REPORT;
   -- Expected: 100,000
""")
