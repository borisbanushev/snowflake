#!/usr/bin/env python3
"""
Upload PostgreSQL JDBC Driver to Snowflake for Openflow
"""

import snowflake.connector
import os

# Snowflake connection details
SNOWFLAKE_ACCOUNT = "MZHGUVK-BC67154"
SNOWFLAKE_USER = "ACCOUNTADMIN"
SNOWFLAKE_PASSWORD = "L@lolo87Snowflake"
SNOWFLAKE_DATABASE = "CREDIT_DECISIONING_DB"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"

DRIVER_FILE = "postgresql-42.7.1.jar"
STAGE_NAME = "@OPENFLOW_DRIVERS"

print("=" * 70)
print("Uploading PostgreSQL JDBC Driver to Snowflake")
print("=" * 70)
print()

try:
    # Connect to Snowflake
    print("Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        database=SNOWFLAKE_DATABASE,
        warehouse=SNOWFLAKE_WAREHOUSE
    )
    cursor = conn.cursor()
    print("✅ Connected to Snowflake")
    print()
    
    # Create stage if it doesn't exist
    print(f"Creating stage {STAGE_NAME} (if not exists)...")
    cursor.execute(f"""
        CREATE STAGE IF NOT EXISTS {STAGE_NAME}
        COMMENT = 'Stage for Openflow JDBC drivers'
    """)
    print(f"✅ Stage {STAGE_NAME} ready")
    print()
    
    # Upload the driver file
    print(f"Uploading {DRIVER_FILE} to stage...")
    cursor.execute(f"""
        PUT file://{DRIVER_FILE} {STAGE_NAME}
        AUTO_COMPRESS = FALSE
        OVERWRITE = TRUE
    """)
    print(f"✅ Driver uploaded successfully")
    print()
    
    # List files in stage to verify
    print("Verifying upload...")
    cursor.execute(f"LIST {STAGE_NAME}")
    files = cursor.fetchall()
    for file_info in files:
        print(f"  ✓ {file_info[0]}")
    print()
    
    # Get the stage location for Openflow configuration
    cursor.execute(f"DESC STAGE {STAGE_NAME}")
    stage_info = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    print("=" * 70)
    print("🎉 PostgreSQL Driver Upload Complete!")
    print("=" * 70)
    print()
    print("Driver Location for Openflow Configuration:")
    print(f"  {STAGE_NAME}/{DRIVER_FILE}")
    print()
    print("Next Steps:")
    print("  1. In Snowflake Openflow, go to PostgreSQL Source Parameters")
    print("  2. Set 'PostgreSQL JDBC Driver' to:")
    print(f"     {STAGE_NAME}/{DRIVER_FILE}")
    print("  3. Apply the parameters")
    print("  4. Enable the PostgreSQL Connection Pool")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Troubleshooting:")
    print("  - Check Snowflake credentials")
    print("  - Verify warehouse and database exist")
    print("  - Ensure driver file exists in current directory")
    exit(1)
