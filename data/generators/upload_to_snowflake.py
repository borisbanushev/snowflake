#!/usr/bin/env python3
"""
Upload all generated CSV files to Snowflake
Uses Snowflake connector to PUT files to stage and COPY INTO tables
"""

import snowflake.connector
import os
from pathlib import Path
from tqdm import tqdm
import sys

# Configuration
CSV_DIR = 'data/generated_csv'
SNOWFLAKE_ACCOUNT = 'mzhguvk-bc67154'  # lowercase
SNOWFLAKE_USER = 'ACCOUNTADMIN'
SNOWFLAKE_PASSWORD = 'L@lolo87Snowflake'
SNOWFLAKE_DATABASE = 'CREDIT_DECISIONING_DB'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
SNOWFLAKE_STAGE = 'CSV_DATA_STAGE'
SNOWFLAKE_ROLE = 'ACCOUNTADMIN'

# Table mapping: CSV filename -> (schema, table_name)
TABLE_MAPPINGS = {
    # Digital Banking
    'digital_customer_profile.csv': ('DIGITAL_BANKING', 'DIGITAL_CUSTOMER_PROFILE'),
    'digital_session.csv': ('DIGITAL_BANKING', 'DIGITAL_SESSION'),
    'digital_event.csv': ('DIGITAL_BANKING', 'DIGITAL_EVENT'),
    'digital_kyc_document.csv': ('DIGITAL_BANKING', 'DIGITAL_KYC_DOCUMENT'),
    
    # Core Banking
    't24_customer.csv': ('CORE_BANKING', 'T24_CUSTOMER'),
    't24_account.csv': ('CORE_BANKING', 'T24_ACCOUNT'),
    't24_loan.csv': ('CORE_BANKING', 'T24_LOAN'),
    't24_transaction.csv': ('CORE_BANKING', 'T24_TRANSACTION'),
    't24_payment_schedule.csv': ('CORE_BANKING', 'T24_PAYMENT_SCHEDULE'),
    't24_collateral.csv': ('CORE_BANKING', 'T24_COLLATERAL'),
    
    # Credit Bureau
    'credit_score.csv': ('CREDIT_BUREAU', 'CREDIT_SCORE'),
    'credit_inquiry.csv': ('CREDIT_BUREAU', 'CREDIT_INQUIRY'),
    'tradeline.csv': ('CREDIT_BUREAU', 'TRADELINE'),
    'public_record.csv': ('CREDIT_BUREAU', 'PUBLIC_RECORD'),
    
    # Reference Data
    'country_code.csv': ('REFERENCE_DATA', 'COUNTRY_CODE'),
    'currency_code.csv': ('REFERENCE_DATA', 'CURRENCY_CODE'),
    'product_catalog.csv': ('REFERENCE_DATA', 'PRODUCT_CATALOG'),
    'branch_directory.csv': ('REFERENCE_DATA', 'BRANCH_DIRECTORY'),
    'relationship_manager.csv': ('REFERENCE_DATA', 'RELATIONSHIP_MANAGER'),
}

def connect_to_snowflake():
    """Establish connection to Snowflake"""
    print("\n🔌 Connecting to Snowflake...")
    print(f"   Account: {SNOWFLAKE_ACCOUNT}")
    print(f"   User: {SNOWFLAKE_USER}")
    print(f"   Database: {SNOWFLAKE_DATABASE}")
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            role=SNOWFLAKE_ROLE
        )
        print("✓ Connected successfully!")
        return conn
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print(f"\nTrying alternative connection method...")
        # Try with lowercase account
        try:
            conn = snowflake.connector.connect(
                user=SNOWFLAKE_USER.upper(),
                password=SNOWFLAKE_PASSWORD,
                account='mzhguvk.bc67154',  # Try with dot notation
                warehouse=SNOWFLAKE_WAREHOUSE,
                database=SNOWFLAKE_DATABASE,
                role=SNOWFLAKE_ROLE
            )
            print("✓ Connected successfully with alternative method!")
            return conn
        except Exception as e2:
            print(f"✗ Alternative connection also failed: {e2}")
            sys.exit(1)

def upload_csv_to_stage(conn, csv_file_path, csv_filename):
    """Upload a CSV file to Snowflake internal stage"""
    cursor = conn.cursor()
    try:
        # Use absolute path for PUT command
        abs_path = os.path.abspath(csv_file_path)
        
        # PUT command to upload file to stage
        put_sql = f"PUT file://{abs_path} @{SNOWFLAKE_STAGE} AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
        cursor.execute(put_sql)
        
        return True
    except Exception as e:
        print(f"✗ Failed to upload {csv_filename}: {e}")
        return False
    finally:
        cursor.close()

def copy_into_table(conn, csv_filename, schema, table_name):
    """Copy data from stage into Snowflake table"""
    cursor = conn.cursor()
    try:
        # Set schema
        cursor.execute(f"USE SCHEMA {schema}")
        
        # Truncate table first
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        
        # COPY INTO command
        copy_sql = f"""
        COPY INTO {table_name}
        FROM @{SNOWFLAKE_STAGE}/{csv_filename}
        FILE_FORMAT = (
            TYPE = 'CSV'
            FIELD_DELIMITER = ','
            SKIP_HEADER = 1
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            NULL_IF = ('NULL', 'null', '')
            EMPTY_FIELD_AS_NULL = TRUE
            DATE_FORMAT = 'AUTO'
            TIMESTAMP_FORMAT = 'AUTO'
        )
        ON_ERROR = 'CONTINUE'
        """
        
        cursor.execute(copy_sql)
        result = cursor.fetchall()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        return row_count
    except Exception as e:
        print(f"✗ Failed to copy into {schema}.{table_name}: {e}")
        return None
    finally:
        cursor.close()

def validate_data(conn):
    """Validate all tables have data"""
    print("\n🔍 Validating data load...")
    cursor = conn.cursor()
    
    results = []
    for csv_file, (schema, table) in TABLE_MAPPINGS.items():
        try:
            cursor.execute(f"USE SCHEMA {schema}")
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            results.append((schema, table, count))
        except Exception as e:
            results.append((schema, table, f"ERROR: {e}"))
    
    cursor.close()
    return results

def main():
    """Main execution"""
    print("=" * 80)
    print("📤 SNOWFLAKE DATA UPLOADER")
    print("=" * 80)
    
    # Check CSV directory exists
    if not os.path.exists(CSV_DIR):
        print(f"✗ CSV directory not found: {CSV_DIR}")
        print("Please run generate_all_snowflake_data.py first!")
        sys.exit(1)
    
    # Get list of CSV files
    csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
    if not csv_files:
        print(f"✗ No CSV files found in {CSV_DIR}")
        sys.exit(1)
    
    print(f"\n📁 Found {len(csv_files)} CSV files to upload")
    
    # Connect to Snowflake
    conn = connect_to_snowflake()
    
    # Upload and load each file
    print("\n📤 Uploading CSV files to Snowflake stage...")
    upload_results = []
    
    for csv_file in tqdm(sorted(csv_files), desc="Uploading"):
        if csv_file in TABLE_MAPPINGS:
            csv_path = os.path.join(CSV_DIR, csv_file)
            success = upload_csv_to_stage(conn, csv_path, csv_file)
            upload_results.append((csv_file, success))
        else:
            print(f"⚠️  Skipping {csv_file} (no table mapping)")
    
    # Copy data into tables
    print("\n📥 Loading data into Snowflake tables...")
    load_results = []
    
    for csv_file in tqdm(sorted(csv_files), desc="Loading"):
        if csv_file in TABLE_MAPPINGS:
            schema, table = TABLE_MAPPINGS[csv_file]
            row_count = copy_into_table(conn, csv_file, schema, table)
            load_results.append((schema, table, row_count))
    
    # Validate
    validation_results = validate_data(conn)
    
    # Close connection
    conn.close()
    
    # Summary Report
    print("\n" + "=" * 80)
    print("✅ DATA LOAD COMPLETE!")
    print("=" * 80)
    
    print("\n📊 Load Summary:")
    total_rows = 0
    for schema, table, count in validation_results:
        if isinstance(count, int):
            total_rows += count
            print(f"   • {schema:20s}.{table:35s} {count:>10,} rows")
        else:
            print(f"   • {schema:20s}.{table:35s} {count}")
    
    print(f"\n🎯 Total Records Loaded: {total_rows:,}")
    print("\n✨ All data successfully loaded into Snowflake!")
    print("=" * 80)

if __name__ == "__main__":
    main()
