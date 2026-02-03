#!/usr/bin/env python3
"""
Create Credit Bureau Managed Tables in Databricks Unity Catalog
Uses Databricks-managed storage (no external S3/ADLS/GCS needed)
"""

from databricks import sql
from databricks.sdk import WorkspaceClient
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os
from tqdm import tqdm

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

# Configuration
DATABRICKS_HOST = os.getenv('DATABRICKS_HOST', '')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN', '')
DATABRICKS_WAREHOUSE = os.getenv('DATABRICKS_WAREHOUSE_ID', '')
CATALOG_NAME = os.getenv('DATABRICKS_CATALOG', 'credit_bureau_data')
SCHEMA_NAME = os.getenv('DATABRICKS_SCHEMA', 'credit_bureau')

NUM_CUSTOMERS = int(os.getenv('NUM_CUSTOMERS', '100000'))

print("=" * 70)
print("Databricks Credit Bureau Data Loader (Managed Tables)")
print("=" * 70)
print(f"Catalog: {CATALOG_NAME}")
print(f"Schema: {SCHEMA_NAME}")
print(f"Storage: Databricks-managed (serverless)")
print("=" * 70)

def get_databricks_connection():
    """Connect to Databricks SQL Warehouse"""
    try:
        # Get HTTP path for SQL warehouse
        w = WorkspaceClient(host=DATABRICKS_HOST, token=DATABRICKS_TOKEN)
        warehouses = list(w.warehouses.list())
        
        if not warehouses:
            print("⚠️  No SQL warehouses found. Creating one...")
            warehouse = w.warehouses.create(
                name="Snowflake-Integration-WH",
                cluster_size="Small",
                max_num_clusters=1
            )
            http_path = warehouse.odbc_params.path
        else:
            http_path = warehouses[0].odbc_params.path
            print(f"✅ Using warehouse: {warehouses[0].name}")
        
        connection = sql.connect(
            server_hostname=DATABRICKS_HOST.replace('https://', ''),
            http_path=http_path,
            access_token=DATABRICKS_TOKEN
        )
        
        print("✅ Connected to Databricks successfully!\n")
        return connection
    
    except Exception as e:
        print(f"❌ Failed to connect to Databricks: {e}")
        print("\nTroubleshooting:")
        print("1. Check DATABRICKS_HOST and DATABRICKS_TOKEN in .env")
        print("2. Verify token has not expired")
        print("3. Ensure you have Databricks SQL or Workspace access")
        return None

def create_catalog_and_schema(connection):
    """Create Unity Catalog and schema for managed tables"""
    cursor = connection.cursor()
    
    print("📦 Setting up Unity Catalog...")
    
    # Create catalog if not exists
    cursor.execute(f"""
        CREATE CATALOG IF NOT EXISTS {CATALOG_NAME}
        COMMENT 'Credit Bureau data for Snowflake integration'
    """)
    print(f"✅ Catalog: {CATALOG_NAME}")
    
    # Use catalog
    cursor.execute(f"USE CATALOG {CATALOG_NAME}")
    
    # Create schema (no LOCATION needed for managed tables)
    cursor.execute(f"""
        CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}
        COMMENT 'Credit bureau managed tables - accessible via Polaris'
    """)
    print(f"✅ Schema: {SCHEMA_NAME}")
    print(f"📁 Storage: Databricks-managed (serverless)\n")
    
    cursor.close()

def create_iceberg_tables(connection):
    """Create managed Delta tables in Unity Catalog"""
    cursor = connection.cursor()
    cursor.execute(f"USE {CATALOG_NAME}.{SCHEMA_NAME}")
    
    print("📊 Creating managed Delta tables...\n")
    
    # Drop existing tables
    for table in ['FRAUD_INDICATORS', 'ALTERNATIVE_DATA', 'INCOME_VERIFICATION', 'CREDIT_BUREAU_REPORT']:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
        except:
            pass
    
    # 1. CREDIT_BUREAU_REPORT
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {CATALOG_NAME}.{SCHEMA_NAME}.CREDIT_BUREAU_REPORT (
            REPORT_ID STRING,
            CUSTOMER_ID STRING,
            BUREAU_NAME STRING,
            REPORT_DATE DATE,
            CREDIT_SCORE INT,
            CREDIT_SCORE_VERSION STRING,
            SCORE_FACTORS STRING,
            CREDIT_LIMIT_UTILIZATION DECIMAL(5,4),
            TOTAL_ACCOUNTS INT,
            OPEN_ACCOUNTS INT,
            CLOSED_ACCOUNTS INT,
            DELINQUENT_ACCOUNTS INT,
            PUBLIC_RECORDS INT,
            BANKRUPTCIES INT,
            TAX_LIENS INT,
            JUDGMENTS INT,
            COLLECTIONS INT,
            INQUIRIES_LAST_6M INT,
            INQUIRIES_LAST_12M INT,
            OLDEST_ACCOUNT_DATE DATE,
            NEWEST_ACCOUNT_DATE DATE,
            AVERAGE_ACCOUNT_AGE_MONTHS INT,
            TOTAL_BALANCE DECIMAL(18,2),
            TOTAL_CREDIT_LIMIT DECIMAL(18,2),
            TOTAL_MONTHLY_PAYMENT DECIMAL(18,2),
            DELINQUENCY_30_DAYS INT,
            DELINQUENCY_60_DAYS INT,
            DELINQUENCY_90_DAYS INT,
            CREATED_TIMESTAMP TIMESTAMP,
            MODIFIED_TIMESTAMP TIMESTAMP
        )
        COMMENT 'Credit bureau reports from external agencies - Managed by Databricks'
    """)
    print("✅ Created CREDIT_BUREAU_REPORT (managed table)")
    
    # 2. INCOME_VERIFICATION
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {CATALOG_NAME}.{SCHEMA_NAME}.INCOME_VERIFICATION (
            VERIFICATION_ID STRING,
            CUSTOMER_ID STRING,
            VERIFICATION_TYPE STRING,
            VERIFICATION_DATE DATE,
            EMPLOYER_NAME STRING,
            EMPLOYMENT_STATUS STRING,
            JOB_TITLE STRING,
            EMPLOYMENT_START_DATE DATE,
            EMPLOYMENT_SECTOR STRING,
            ANNUAL_INCOME DECIMAL(18,2),
            MONTHLY_INCOME DECIMAL(18,2),
            INCOME_SOURCE STRING,
            INCOME_STABILITY_SCORE INT,
            VERIFICATION_METHOD STRING,
            VERIFIED_BY STRING,
            VERIFICATION_STATUS STRING,
            DOCUMENTS_PROVIDED STRING,
            CONFIDENCE_LEVEL STRING,
            NOTES STRING,
            CREATED_TIMESTAMP TIMESTAMP
        )
        COMMENT 'Income and employment verification data - Managed by Databricks'
    """)
    print("✅ Created INCOME_VERIFICATION (managed table)")
    
    # 3. ALTERNATIVE_DATA
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {CATALOG_NAME}.{SCHEMA_NAME}.ALTERNATIVE_DATA (
            ALT_DATA_ID STRING,
            CUSTOMER_ID STRING,
            DATA_SOURCE STRING,
            DATA_TYPE STRING,
            COLLECTION_DATE DATE,
            UTILITY_PAYMENT_SCORE INT,
            RENT_PAYMENT_SCORE INT,
            MOBILE_PAYMENT_SCORE INT,
            ECOMMERCE_HISTORY_MONTHS INT,
            ECOMMERCE_TRANSACTION_COUNT INT,
            ECOMMERCE_AVERAGE_ORDER_VALUE DECIMAL(10,2),
            SOCIAL_MEDIA_SCORE INT,
            EDUCATION_LEVEL STRING,
            PROFESSIONAL_CERTIFICATIONS STRING,
            DIGITAL_FOOTPRINT_SCORE INT,
            GIG_ECONOMY_INCOME DECIMAL(18,2),
            FREELANCE_PLATFORMS STRING,
            ONLINE_REPUTATION_SCORE INT,
            CREATED_TIMESTAMP TIMESTAMP
        )
        COMMENT 'Alternative credit data from non-traditional sources - Managed by Databricks'
    """)
    print("✅ Created ALTERNATIVE_DATA (managed table)")
    
    # 4. FRAUD_INDICATORS
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {CATALOG_NAME}.{SCHEMA_NAME}.FRAUD_INDICATORS (
            INDICATOR_ID STRING,
            CUSTOMER_ID STRING,
            CHECK_DATE DATE,
            FRAUD_RISK_SCORE INT,
            IDENTITY_VERIFICATION_STATUS STRING,
            DOCUMENT_AUTHENTICITY_SCORE INT,
            BIOMETRIC_MATCH_SCORE DECIMAL(5,4),
            WATCHLIST_MATCHES INT,
            SANCTIONS_CHECK STRING,
            PEP_CHECK STRING,
            ADVERSE_MEDIA_HITS INT,
            DEVICE_FINGERPRINT_RISK STRING,
            IP_ADDRESS_RISK STRING,
            BEHAVIORAL_ANOMALIES STRING,
            VELOCITY_CHECKS STRING,
            SYNTHETIC_IDENTITY_SCORE INT,
            FIRST_PARTY_FRAUD_RISK INT,
            THIRD_PARTY_FRAUD_RISK INT,
            CREATED_TIMESTAMP TIMESTAMP
        )
        COMMENT 'Fraud detection and prevention indicators - Managed by Databricks'
    """)
    print("✅ Created FRAUD_INDICATORS (managed table)\n")
    
    cursor.close()

def generate_credit_reports(num_customers):
    """Generate credit bureau reports"""
    print(f"📊 Generating {num_customers:,} credit bureau reports...")
    
    data = []
    for i in tqdm(range(num_customers)):
        # Credit score with realistic distribution
        score = int(np.random.beta(5, 3) * 550 + 300)
        
        total_accounts = random.randint(2, 20)
        open_accounts = random.randint(1, total_accounts)
        
        data.append({
            'REPORT_ID': f'RPT-{i:08d}',
            'CUSTOMER_ID': f'CUS-{i:06d}',
            'BUREAU_NAME': random.choice(['EXPERIAN', 'EQUIFAX', 'TRANSUNION']),
            'REPORT_DATE': (datetime.now() - timedelta(days=random.randint(0, 90))).date(),
            'CREDIT_SCORE': score,
            'CREDIT_SCORE_VERSION': 'FICO-8',
            'SCORE_FACTORS': str(['Payment History', 'Credit Utilization', 'Length of History']),
            'CREDIT_LIMIT_UTILIZATION': round(random.uniform(0.1, 0.8), 4),
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
            'OLDEST_ACCOUNT_DATE': (datetime.now() - timedelta(days=random.randint(730, 7300))).date(),
            'NEWEST_ACCOUNT_DATE': (datetime.now() - timedelta(days=random.randint(0, 730))).date(),
            'AVERAGE_ACCOUNT_AGE_MONTHS': random.randint(12, 120),
            'TOTAL_BALANCE': round(random.uniform(5000, 150000), 2),
            'TOTAL_CREDIT_LIMIT': round(random.uniform(20000, 300000), 2),
            'TOTAL_MONTHLY_PAYMENT': round(random.uniform(500, 5000), 2),
            'DELINQUENCY_30_DAYS': random.randint(0, 3),
            'DELINQUENCY_60_DAYS': random.randint(0, 1),
            'DELINQUENCY_90_DAYS': random.randint(0, 1),
            'CREATED_TIMESTAMP': datetime.now(),
            'MODIFIED_TIMESTAMP': datetime.now()
        })
    
    return pd.DataFrame(data)

def generate_income_verification(num_customers):
    """Generate income verification records"""
    print(f"💰 Generating {num_customers:,} income verification records...")
    
    data = []
    for i in tqdm(range(num_customers)):
        annual_income = random.uniform(30000, 500000)
        
        data.append({
            'VERIFICATION_ID': f'INC-{i:08d}',
            'CUSTOMER_ID': f'CUS-{i:06d}',
            'VERIFICATION_TYPE': random.choice(['EMPLOYMENT', 'SELF_EMPLOYED', 'INVESTMENT']),
            'VERIFICATION_DATE': (datetime.now() - timedelta(days=random.randint(0, 180))).date(),
            'EMPLOYER_NAME': fake.company(),
            'EMPLOYMENT_STATUS': random.choice(['FULL_TIME', 'PART_TIME', 'CONTRACT', 'SELF_EMPLOYED']),
            'JOB_TITLE': fake.job(),
            'EMPLOYMENT_START_DATE': (datetime.now() - timedelta(days=random.randint(365, 3650))).date(),
            'EMPLOYMENT_SECTOR': random.choice(['TECH', 'FINANCE', 'HEALTHCARE', 'RETAIL', 'MANUFACTURING']),
            'ANNUAL_INCOME': round(annual_income, 2),
            'MONTHLY_INCOME': round(annual_income / 12, 2),
            'INCOME_SOURCE': random.choice(['SALARY', 'BUSINESS', 'INVESTMENT', 'RENTAL']),
            'INCOME_STABILITY_SCORE': random.randint(60, 100),
            'VERIFICATION_METHOD': random.choice(['PAY_STUB', 'TAX_RETURN', 'BANK_STATEMENT', 'EMPLOYER_CALL']),
            'VERIFIED_BY': f'VERIFIER-{random.randint(1, 50):03d}',
            'VERIFICATION_STATUS': random.choices(['VERIFIED', 'PENDING', 'FAILED'], weights=[85, 10, 5])[0],
            'DOCUMENTS_PROVIDED': str(['Pay Stub', 'Tax Return']),
            'CONFIDENCE_LEVEL': random.choice(['HIGH', 'MEDIUM', 'LOW']),
            'NOTES': 'Verified successfully',
            'CREATED_TIMESTAMP': datetime.now()
        })
    
    return pd.DataFrame(data)

def load_dataframe_to_databricks(connection, table_name, df, batch_size=1000):
    """Load DataFrame to Databricks Iceberg table"""
    cursor = connection.cursor()
    
    print(f"📥 Loading {len(df):,} rows to {table_name}...")
    
    # Prepare SQL
    columns = df.columns.tolist()
    placeholders = ', '.join(['?' for _ in columns])
    sql = f"INSERT INTO {CATALOG_NAME}.{SCHEMA_NAME}.{table_name} VALUES ({placeholders})"
    
    # Convert to list of tuples
    data = [tuple(x) for x in df.to_numpy()]
    
    # Batch insert
    for i in tqdm(range(0, len(data), batch_size)):
        batch = data[i:i+batch_size]
        cursor.executemany(sql, batch)
    
    cursor.close()
    print(f"✅ Loaded {len(df):,} rows\n")

def main():
    # Connect
    conn = get_databricks_connection()
    if not conn:
        return
    
    # Create catalog and schema
    create_catalog_and_schema(conn)
    
    # Create Iceberg tables
    create_iceberg_tables(conn)
    
    # Generate data
    print("🎲 Generating credit bureau data...\n")
    credit_reports_df = generate_credit_reports(NUM_CUSTOMERS)
    income_verification_df = generate_income_verification(NUM_CUSTOMERS)
    
    # Load data
    print("📤 Loading data to Databricks Iceberg tables...\n")
    load_dataframe_to_databricks(conn, 'CREDIT_BUREAU_REPORT', credit_reports_df)
    load_dataframe_to_databricks(conn, 'INCOME_VERIFICATION', income_verification_df)
    
    # Verify
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {CATALOG_NAME}.{SCHEMA_NAME}.CREDIT_BUREAU_REPORT")
    report_count = cursor.fetchone()[0]
    cursor.execute(f"SELECT COUNT(*) FROM {CATALOG_NAME}.{SCHEMA_NAME}.INCOME_VERIFICATION")
    income_count = cursor.fetchone()[0]
    cursor.close()
    
    print("=" * 70)
    print("🎉 Databricks Data Load Complete!")
    print("=" * 70)
    print(f"Credit Reports:      {report_count:,}")
    print(f"Income Verification: {income_count:,}")
    print(f"\n📁 Storage: Databricks-managed (serverless)")
    print("\n✅ Databricks is ready for Snowflake Polaris integration!")
    print(f"   Catalog: {CATALOG_NAME}")
    print(f"   Schema: {SCHEMA_NAME}")
    print(f"   Format: Delta Lake (managed tables)")
    print("\n💡 Next: Configure Snowflake to read from Unity Catalog via Polaris")
    
    conn.close()

if __name__ == "__main__":
    main()
