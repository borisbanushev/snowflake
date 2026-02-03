#!/bin/bash
# ============================================
# Export MySQL Data and Upload to Snowflake
# ============================================

set -e

echo "======================================================================"
echo "MySQL to Snowflake Data Export & Upload"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Create export directory
EXPORT_DIR="$(pwd)/data/mysql_export"
mkdir -p "$EXPORT_DIR"

echo -e "${YELLOW}[1/3] Exporting MySQL data to CSV...${NC}"
echo ""

# Export tables from MySQL to CSV
docker exec mysql-digital bash -c "
mysql -udigitaluser -pDigitalPass! digital_banking -e \"
SET NAMES 'utf8mb4';
SELECT * FROM DIGITAL_CUSTOMER_PROFILE 
INTO OUTFILE '/tmp/digital_customer_profile.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\\\"'
LINES TERMINATED BY '\\n';
\"
"

docker exec mysql-digital bash -c "
mysql -udigitaluser -pDigitalPass! digital_banking -e \"
SELECT * FROM DIGITAL_SESSION 
INTO OUTFILE '/tmp/digital_session.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\\\"'
LINES TERMINATED BY '\\n';
\"
"

docker exec mysql-digital bash -c "
mysql -udigitaluser -pDigitalPass! digital_banking -e \"
SELECT * FROM DIGITAL_EVENT 
INTO OUTFILE '/tmp/digital_event.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\\\"'
LINES TERMINATED BY '\\n';
\"
"

# Copy files from container to local
echo -e "${YELLOW}   Copying CSV files from container...${NC}"
docker cp mysql-digital:/tmp/digital_customer_profile.csv "$EXPORT_DIR/"
docker cp mysql-digital:/tmp/digital_session.csv "$EXPORT_DIR/"
docker cp mysql-digital:/tmp/digital_event.csv "$EXPORT_DIR/"

echo -e "${GREEN}✅ Exported 3 CSV files to $EXPORT_DIR${NC}"
echo ""

# Show file sizes
echo "Exported files:"
ls -lh "$EXPORT_DIR"/*.csv
echo ""

echo -e "${YELLOW}[2/3] Preparing Snowflake upload script...${NC}"
cat > "$EXPORT_DIR/upload_to_snowflake.sql" << 'EOF'
-- ============================================
-- Upload MySQL Data to Snowflake
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE ETL_WH;
USE SCHEMA RAW_ZONE;

-- Create MySQL_SRC schema if not exists
CREATE SCHEMA IF NOT EXISTS RAW_ZONE.MYSQL_SRC
    COMMENT = 'Raw data from MySQL Digital Banking';

USE SCHEMA RAW_ZONE.MYSQL_SRC;

-- Create stage for CSV uploads
CREATE OR REPLACE STAGE MYSQL_UPLOAD_STAGE
    FILE_FORMAT = (
        TYPE = CSV
        FIELD_DELIMITER = ','
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 0
        TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'
        NULL_IF = ('NULL', '', 'null')
        EMPTY_FIELD_AS_NULL = TRUE
    )
    COMMENT = 'Stage for uploading MySQL CSV files';

-- Create tables matching MySQL schema
CREATE OR REPLACE TABLE DIGITAL_CUSTOMER_PROFILE (
    DIGITAL_ID VARCHAR(36),
    CUSTOMER_ID VARCHAR(20),
    EMAIL VARCHAR(100),
    MOBILE_NUMBER VARCHAR(20),
    USERNAME VARCHAR(50),
    REGISTRATION_DATE TIMESTAMP_NTZ,
    LAST_LOGIN TIMESTAMP_NTZ,
    LOGIN_COUNT NUMBER(10,0),
    FAILED_LOGIN_COUNT NUMBER(10,0),
    MFA_ENABLED BOOLEAN,
    MFA_TYPE VARCHAR(20),
    DEVICE_COUNT NUMBER(10,0),
    PRIMARY_DEVICE_TYPE VARCHAR(20),
    BIOMETRIC_ENABLED BOOLEAN,
    PUSH_NOTIFICATIONS BOOLEAN,
    EMAIL_VERIFIED BOOLEAN,
    MOBILE_VERIFIED BOOLEAN,
    EKYC_STATUS VARCHAR(20),
    EKYC_DATE TIMESTAMP_NTZ,
    PREFERRED_LANGUAGE VARCHAR(10),
    TIMEZONE VARCHAR(50),
    CREATED_DATE TIMESTAMP_NTZ,
    MODIFIED_DATE TIMESTAMP_NTZ,
    CONSTRAINT PK_DIGITAL_ID PRIMARY KEY (DIGITAL_ID)
)
COMMENT = 'Digital customer profiles from MySQL';

CREATE OR REPLACE TABLE DIGITAL_SESSION (
    SESSION_ID VARCHAR(36),
    DIGITAL_ID VARCHAR(36),
    CUSTOMER_ID VARCHAR(20),
    SESSION_START TIMESTAMP_NTZ,
    SESSION_END TIMESTAMP_NTZ,
    DURATION_SECONDS NUMBER(10,0),
    DEVICE_ID VARCHAR(100),
    DEVICE_TYPE VARCHAR(20),
    DEVICE_MODEL VARCHAR(50),
    OS_VERSION VARCHAR(20),
    APP_VERSION VARCHAR(20),
    IP_ADDRESS VARCHAR(45),
    GEOLOCATION_LAT NUMBER(10,7),
    GEOLOCATION_LON NUMBER(10,7),
    CITY VARCHAR(100),
    COUNTRY VARCHAR(3),
    PAGES_VIEWED NUMBER(10,0),
    TRANSACTIONS_INITIATED NUMBER(10,0),
    TRANSACTIONS_COMPLETED NUMBER(10,0),
    ERROR_COUNT NUMBER(10,0),
    SESSION_QUALITY_SCORE NUMBER(5,2),
    EXIT_REASON VARCHAR(30),
    CREATED_DATE TIMESTAMP_NTZ,
    CONSTRAINT PK_SESSION_ID PRIMARY KEY (SESSION_ID)
)
COMMENT = 'Digital banking sessions from MySQL';

CREATE OR REPLACE TABLE DIGITAL_EVENT (
    EVENT_ID VARCHAR(36),
    SESSION_ID VARCHAR(36),
    DIGITAL_ID VARCHAR(36),
    CUSTOMER_ID VARCHAR(20),
    EVENT_TYPE VARCHAR(50),
    EVENT_NAME VARCHAR(100),
    EVENT_TIMESTAMP TIMESTAMP_NTZ,
    PAGE_NAME VARCHAR(100),
    ELEMENT_ID VARCHAR(100),
    EVENT_DATA TEXT,
    RESPONSE_TIME_MS NUMBER(10,0),
    SUCCESS BOOLEAN,
    ERROR_CODE VARCHAR(20),
    ERROR_MESSAGE VARCHAR(500),
    CREATED_DATE TIMESTAMP_NTZ,
    CONSTRAINT PK_EVENT_ID PRIMARY KEY (EVENT_ID)
)
COMMENT = 'Digital banking events from MySQL';

-- Show progress
SELECT 'Tables created successfully' AS STATUS;

-- Note: After running this script, upload CSV files via Snowflake UI or SnowSQL:
-- PUT file:///<path>/digital_customer_profile.csv @MYSQL_UPLOAD_STAGE AUTO_COMPRESS=TRUE;
-- PUT file:///<path>/digital_session.csv @MYSQL_UPLOAD_STAGE AUTO_COMPRESS=TRUE;
-- PUT file:///<path>/digital_event.csv @MYSQL_UPLOAD_STAGE AUTO_COMPRESS=TRUE;
--
-- Then load data:
-- COPY INTO DIGITAL_CUSTOMER_PROFILE FROM @MYSQL_UPLOAD_STAGE/digital_customer_profile.csv.gz;
-- COPY INTO DIGITAL_SESSION FROM @MYSQL_UPLOAD_STAGE/digital_session.csv.gz;
-- COPY INTO DIGITAL_EVENT FROM @MYSQL_UPLOAD_STAGE/digital_event.csv.gz;
--
-- Verify:
-- SELECT COUNT(*) FROM DIGITAL_CUSTOMER_PROFILE; -- Expected: 100,000
-- SELECT COUNT(*) FROM DIGITAL_SESSION;          -- Expected: 1,000,000
-- SELECT COUNT(*) FROM DIGITAL_EVENT;            -- Expected: 5,000,000
EOF

echo -e "${GREEN}✅ Snowflake upload script created${NC}"
echo ""

echo -e "${YELLOW}[3/3] Creating Python upload script...${NC}"

# Install snowflake-connector-python if needed
pip install -q snowflake-connector-python python-dotenv

cat > "$EXPORT_DIR/upload_via_python.py" << 'EOFPY'
#!/usr/bin/env python3
"""
Upload MySQL CSV files to Snowflake using Python
"""

import snowflake.connector
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Snowflake connection
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')

print("=" * 70)
print("MySQL to Snowflake Data Upload")
print("=" * 70)
print(f"Account: {SNOWFLAKE_ACCOUNT}")
print(f"User: {SNOWFLAKE_USER}")
print("=" * 70)
print()

# Connect to Snowflake
print("🔌 Connecting to Snowflake...")
conn = snowflake.connector.connect(
    account=SNOWFLAKE_ACCOUNT,
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    warehouse='ETL_WH',
    database='CREDIT_DECISIONING_DB',
    schema='RAW_ZONE'
)
print("✅ Connected to Snowflake\n")

cursor = conn.cursor()

# Setup
print("🔧 Setting up schemas and stage...")
cursor.execute("CREATE SCHEMA IF NOT EXISTS RAW_ZONE.MYSQL_SRC")
cursor.execute("USE SCHEMA RAW_ZONE.MYSQL_SRC")

# Create stage
cursor.execute("""
CREATE OR REPLACE STAGE MYSQL_UPLOAD_STAGE
    FILE_FORMAT = (
        TYPE = CSV
        FIELD_DELIMITER = ','
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 0
        TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'
        NULL_IF = ('NULL', '', 'null')
        EMPTY_FIELD_AS_NULL = TRUE
    )
""")
print("✅ Stage created\n")

# Create tables (schema from previous SQL)
print("📋 Creating tables...")

cursor.execute("""
CREATE OR REPLACE TABLE DIGITAL_CUSTOMER_PROFILE (
    DIGITAL_ID VARCHAR(36),
    CUSTOMER_ID VARCHAR(20),
    EMAIL VARCHAR(100),
    MOBILE_NUMBER VARCHAR(20),
    USERNAME VARCHAR(50),
    REGISTRATION_DATE TIMESTAMP_NTZ,
    LAST_LOGIN TIMESTAMP_NTZ,
    LOGIN_COUNT NUMBER(10,0),
    FAILED_LOGIN_COUNT NUMBER(10,0),
    MFA_ENABLED BOOLEAN,
    MFA_TYPE VARCHAR(20),
    DEVICE_COUNT NUMBER(10,0),
    PRIMARY_DEVICE_TYPE VARCHAR(20),
    BIOMETRIC_ENABLED BOOLEAN,
    PUSH_NOTIFICATIONS BOOLEAN,
    EMAIL_VERIFIED BOOLEAN,
    MOBILE_VERIFIED BOOLEAN,
    EKYC_STATUS VARCHAR(20),
    EKYC_DATE TIMESTAMP_NTZ,
    PREFERRED_LANGUAGE VARCHAR(10),
    TIMEZONE VARCHAR(50),
    CREATED_DATE TIMESTAMP_NTZ,
    MODIFIED_DATE TIMESTAMP_NTZ,
    CONSTRAINT PK_DIGITAL_ID PRIMARY KEY (DIGITAL_ID)
)
""")

cursor.execute("""
CREATE OR REPLACE TABLE DIGITAL_SESSION (
    SESSION_ID VARCHAR(36),
    DIGITAL_ID VARCHAR(36),
    CUSTOMER_ID VARCHAR(20),
    SESSION_START TIMESTAMP_NTZ,
    SESSION_END TIMESTAMP_NTZ,
    DURATION_SECONDS NUMBER(10,0),
    DEVICE_ID VARCHAR(100),
    DEVICE_TYPE VARCHAR(20),
    DEVICE_MODEL VARCHAR(50),
    OS_VERSION VARCHAR(20),
    APP_VERSION VARCHAR(20),
    IP_ADDRESS VARCHAR(45),
    GEOLOCATION_LAT NUMBER(10,7),
    GEOLOCATION_LON NUMBER(10,7),
    CITY VARCHAR(100),
    COUNTRY VARCHAR(3),
    PAGES_VIEWED NUMBER(10,0),
    TRANSACTIONS_INITIATED NUMBER(10,0),
    TRANSACTIONS_COMPLETED NUMBER(10,0),
    ERROR_COUNT NUMBER(10,0),
    SESSION_QUALITY_SCORE NUMBER(5,2),
    EXIT_REASON VARCHAR(30),
    CREATED_DATE TIMESTAMP_NTZ,
    CONSTRAINT PK_SESSION_ID PRIMARY KEY (SESSION_ID)
)
""")

cursor.execute("""
CREATE OR REPLACE TABLE DIGITAL_EVENT (
    EVENT_ID VARCHAR(36),
    SESSION_ID VARCHAR(36),
    DIGITAL_ID VARCHAR(36),
    CUSTOMER_ID VARCHAR(20),
    EVENT_TYPE VARCHAR(50),
    EVENT_NAME VARCHAR(100),
    EVENT_TIMESTAMP TIMESTAMP_NTZ,
    PAGE_NAME VARCHAR(100),
    ELEMENT_ID VARCHAR(100),
    EVENT_DATA TEXT,
    RESPONSE_TIME_MS NUMBER(10,0),
    SUCCESS BOOLEAN,
    ERROR_CODE VARCHAR(20),
    ERROR_MESSAGE VARCHAR(500),
    CREATED_DATE TIMESTAMP_NTZ,
    CONSTRAINT PK_EVENT_ID PRIMARY KEY (EVENT_ID)
)
""")
print("✅ Tables created\n")

# Upload files
export_dir = Path(__file__).parent
csv_files = [
    'digital_customer_profile.csv',
    'digital_session.csv',
    'digital_event.csv'
]

for csv_file in csv_files:
    file_path = export_dir / csv_file
    if not file_path.exists():
        print(f"⚠️  {csv_file} not found, skipping")
        continue
    
    print(f"📤 Uploading {csv_file}...")
    cursor.execute(f"PUT file://{file_path} @MYSQL_UPLOAD_STAGE AUTO_COMPRESS=TRUE OVERWRITE=TRUE")
    print(f"✅ Uploaded {csv_file}\n")

# Load data
print("📥 Loading data into tables...")

table_mappings = {
    'DIGITAL_CUSTOMER_PROFILE': 'digital_customer_profile.csv.gz',
    'DIGITAL_SESSION': 'digital_session.csv.gz',
    'DIGITAL_EVENT': 'digital_event.csv.gz'
}

for table, file in table_mappings.items():
    print(f"   Loading {table}...")
    cursor.execute(f"COPY INTO {table} FROM @MYSQL_UPLOAD_STAGE/{file} ON_ERROR='CONTINUE'")
    result = cursor.fetchone()
    print(f"   ✅ {result[0]} rows loaded\n")

# Verify
print("=" * 70)
print("🎉 Data Load Complete!")
print("=" * 70)

for table in table_mappings.keys():
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count:,} rows")

print("\n✅ MySQL data is now in Snowflake!")

cursor.close()
conn.close()
EOFPY

chmod +x "$EXPORT_DIR/upload_via_python.py"

echo -e "${GREEN}✅ Python upload script created${NC}"
echo ""

echo "======================================================================"
echo -e "${GREEN}✅ Export Complete!${NC}"
echo "======================================================================"
echo ""
echo "CSV files exported to: $EXPORT_DIR"
echo ""
echo "Next Steps - Choose One:"
echo ""
echo "  Option A: Python Upload (EASIEST)"
echo "    cd $EXPORT_DIR"
echo "    python3 upload_via_python.py"
echo ""
echo "  Option B: Snowflake UI Upload"
echo "    1. Log into Snowflake: https://app.snowflake.com"
echo "    2. Run SQL script: $EXPORT_DIR/upload_to_snowflake.sql"
echo "    3. Go to Databases > CREDIT_DECISIONING_DB > RAW_ZONE > MYSQL_SRC"
echo "    4. Upload CSV files via UI to stage MYSQL_UPLOAD_STAGE"
echo "    5. Run COPY INTO commands (in SQL script comments)"
echo ""
echo "Expected Results:"
echo "  - DIGITAL_CUSTOMER_PROFILE: 100,000 rows"
echo "  - DIGITAL_SESSION:          1,000,000 rows"
echo "  - DIGITAL_EVENT:            5,000,000 rows"
echo ""
