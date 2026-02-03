#!/usr/bin/env python3
"""
Fast CSV Upload to Snowflake Stage
Uploads all CSV files from data/generated_csv/ to CSV_DATA_STAGE
"""

import snowflake.connector
import os
from pathlib import Path
from tqdm import tqdm

# Configuration from .env
SNOWFLAKE_ACCOUNT = "MZHGUVK-BC67154"
SNOWFLAKE_USER = "ACCOUNTADMIN"
SNOWFLAKE_PASSWORD = "L@lolo87Snowflake"
SNOWFLAKE_DATABASE = "CREDIT_DECISIONING_DB"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_STAGE = "CSV_DATA_STAGE"
SNOWFLAKE_ROLE = "ACCOUNTADMIN"

CSV_DIR = "data/generated_csv"

def main():
    print("🚀 Fast CSV Upload to Snowflake Stage\n")
    
    # Check CSV directory
    csv_path = Path(CSV_DIR)
    if not csv_path.exists():
        print(f"❌ Directory not found: {CSV_DIR}")
        return
    
    csv_files = list(csv_path.glob("*.csv"))
    if not csv_files:
        print(f"❌ No CSV files found in {CSV_DIR}")
        return
    
    print(f"📁 Found {len(csv_files)} CSV files\n")
    
    # Connect to Snowflake
    print("🔌 Connecting to Snowflake...")
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            role=SNOWFLAKE_ROLE
        )
        print("✅ Connected!\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Trying alternative connection format...")
        try:
            conn = snowflake.connector.connect(
                user=SNOWFLAKE_USER,
                password=SNOWFLAKE_PASSWORD,
                account=SNOWFLAKE_ACCOUNT.lower().replace('-', '.'),
                warehouse=SNOWFLAKE_WAREHOUSE,
                database=SNOWFLAKE_DATABASE,
                role=SNOWFLAKE_ROLE
            )
            print("✅ Connected with alternative format!\n")
        except Exception as e2:
            print(f"❌ Still failed: {e2}")
            return
    
    cursor = conn.cursor()
    
    # Set context
    cursor.execute(f"USE WAREHOUSE {SNOWFLAKE_WAREHOUSE}")
    cursor.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
    
    # Upload each CSV file
    print(f"📤 Uploading files to @{SNOWFLAKE_STAGE}...\n")
    
    success_count = 0
    for csv_file in tqdm(sorted(csv_files), desc="Uploading"):
        try:
            abs_path = csv_file.resolve()
            put_sql = f"PUT file://{abs_path} @{SNOWFLAKE_STAGE} AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
            cursor.execute(put_sql)
            success_count += 1
        except Exception as e:
            print(f"\n⚠️  Failed to upload {csv_file.name}: {e}")
    
    cursor.close()
    conn.close()
    
    print(f"\n✅ Successfully uploaded {success_count}/{len(csv_files)} files!")
    print(f"\n📋 Next step: Run 04_load_all_data.sql in Snowflake UI to load data into tables")

if __name__ == "__main__":
    main()
