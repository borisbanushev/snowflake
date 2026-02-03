#!/usr/bin/env python3
"""
Upload PostgreSQL JDBC Driver to Snowflake for Openflow
"""

import snowflake.connector
import os

# Snowflake connection details (from your .env)
# Try different account formats
import os

# Get credentials - try environment or use defaults
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "MZHGUVK-BC67154")
SNOWFLAKE_USER = input("Enter your Snowflake username (or press Enter for 'ACCOUNTADMIN'): ").strip() or "ACCOUNTADMIN"
SNOWFLAKE_PASSWORD = input("Enter your Snowflake password: ").strip() or "L@lolo87Snowflake"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_ROLE = "ACCOUNTADMIN"

print(f"Using account: {SNOWFLAKE_ACCOUNT}")
print(f"Using user: {SNOWFLAKE_USER}")
print()

DRIVER_FILE = "postgresql-42.7.1.jar"
DRIVER_PATH = os.path.abspath(DRIVER_FILE)
STAGE_NAME = "OPENFLOW_DRIVERS"

print("=" * 70)
print("Uploading PostgreSQL JDBC Driver to Snowflake")
print("=" * 70)
print()
print(f"Driver file: {DRIVER_PATH}")
print(f"File exists: {os.path.exists(DRIVER_PATH)}")
print(f"File size: {os.path.getsize(DRIVER_PATH) / 1024:.1f} KB")
print()

try:
    # Connect to Snowflake
    print("Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        role=SNOWFLAKE_ROLE
    )
    cursor = conn.cursor()
    print("✅ Connected to Snowflake")
    print(f"   Session ID: {conn.session_id}")
    print()
    
    # Create database if not exists
    print("Setting up database...")
    cursor.execute("USE ROLE ACCOUNTADMIN")
    cursor.execute("CREATE DATABASE IF NOT EXISTS CREDIT_DECISIONING_DB")
    cursor.execute("USE DATABASE CREDIT_DECISIONING_DB")
    cursor.execute(f"USE WAREHOUSE {SNOWFLAKE_WAREHOUSE}")
    print("✅ Database ready")
    print()
    
    # Create stage if it doesn't exist
    print(f"Creating stage {STAGE_NAME} (if not exists)...")
    cursor.execute(f"""
        CREATE STAGE IF NOT EXISTS {STAGE_NAME}
        COMMENT = 'Stage for Openflow JDBC drivers'
    """)
    print(f"✅ Stage {STAGE_NAME} ready")
    print()
    
    # Upload the driver file using PUT
    print(f"Uploading {DRIVER_FILE} to stage...")
    print(f"   Source: {DRIVER_PATH}")
    print(f"   Destination: @{STAGE_NAME}")
    
    put_command = f"PUT file://{DRIVER_PATH} @{STAGE_NAME} AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
    print(f"   Executing: {put_command}")
    print()
    
    cursor.execute(put_command)
    result = cursor.fetchone()
    print(f"✅ Upload result: {result}")
    print()
    
    # List files in stage to verify
    print("Verifying upload...")
    cursor.execute(f"LIST @{STAGE_NAME}")
    files = cursor.fetchall()
    if files:
        for file_info in files:
            print(f"  ✓ {file_info[0]} ({file_info[1]} bytes)")
    else:
        print("  ⚠️  No files found in stage")
    print()
    
    cursor.close()
    conn.close()
    
    print("=" * 70)
    print("🎉 PostgreSQL Driver Upload Complete!")
    print("=" * 70)
    print()
    print("Driver Location for Openflow Configuration:")
    print(f"  @{STAGE_NAME}/{DRIVER_FILE}")
    print()
    print("Next Steps:")
    print("  1. In Snowflake Openflow, go to PostgreSQL Source Parameters")
    print("  2. Set 'PostgreSQL JDBC Driver' to:")
    print(f"     @{STAGE_NAME}/{DRIVER_FILE}")
    print("  3. Apply the parameters")
    print("  4. Enable the PostgreSQL Connection Pool")
    print("  5. Start the connector")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print()
    exit(1)
