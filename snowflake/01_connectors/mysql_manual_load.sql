-- ============================================
-- Alternative: Manual MySQL Data Load to Snowflake
-- (Use this if Openflow is not available)
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE ETL_WH;

-- ============================================
-- Step 1: Create Schemas
-- ============================================

CREATE SCHEMA IF NOT EXISTS RAW_ZONE
    COMMENT = 'Bronze layer - raw ingested data from external sources';

CREATE SCHEMA IF NOT EXISTS GOVERNANCE
    COMMENT = 'Data governance, policies, and audit';

-- ============================================
-- Step 2: Create MySQL Source Schema
-- ============================================

USE SCHEMA RAW_ZONE;

CREATE SCHEMA IF NOT EXISTS MYSQL_SRC
    COMMENT = 'Raw data from MySQL Digital Banking';

USE SCHEMA MYSQL_SRC;

-- ============================================
-- Step 3: Create File Format for CSV
-- ============================================

CREATE OR REPLACE FILE FORMAT mysql_csv_format
    TYPE = CSV
    FIELD_DELIMITER = ','
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 0
    TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF9'
    NULL_IF = ('NULL', '', 'null', '\\N')
    EMPTY_FIELD_AS_NULL = TRUE
    ESCAPE_UNENCLOSED_FIELD = NONE
    COMMENT = 'CSV format for MySQL exports';

-- ============================================
-- Step 4: Create Stage for MySQL Data
-- ============================================

CREATE OR REPLACE STAGE mysql_upload_stage
    FILE_FORMAT = mysql_csv_format
    COMMENT = 'Stage for uploading MySQL CSV files';

-- ============================================
-- Step 5: Create Tables
-- ============================================

-- Digital Customer Profile
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
COMMENT = 'Digital customer profiles from MySQL RDS';

-- Digital Session
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
COMMENT = 'Digital banking sessions from MySQL RDS';

-- Digital Event
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
COMMENT = 'Digital banking events from MySQL RDS';

SELECT 'Tables created successfully!' AS status;

-- ============================================
-- Step 6: Export Data from MySQL RDS
-- ============================================

-- Run this on your local machine to export MySQL data:
/*

# Export from RDS MySQL to CSV
mysql -h snowflake-credit-demo-mysql.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com \
      -P 3306 -u digitaluser -pDigitalPass123! digital_banking \
      -e "SELECT * FROM DIGITAL_CUSTOMER_PROFILE" | sed 's/\t/,/g' > digital_customer_profile.csv

mysql -h snowflake-credit-demo-mysql.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com \
      -P 3306 -u digitaluser -pDigitalPass123! digital_banking \
      -e "SELECT * FROM DIGITAL_SESSION" | sed 's/\t/,/g' > digital_session.csv

mysql -h snowflake-credit-demo-mysql.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com \
      -P 3306 -u digitaluser -pDigitalPass123! digital_banking \
      -e "SELECT * FROM DIGITAL_EVENT" | sed 's/\t/,/g' > digital_event.csv

*/

-- ============================================
-- Step 7: Upload CSV Files
-- ============================================

-- Option A: Using SnowSQL (from terminal)
/*
snowsql -a MZHGUVK-BC67154 -u ACCOUNTADMIN

USE DATABASE CREDIT_DECISIONING_DB;
USE SCHEMA RAW_ZONE.MYSQL_SRC;

PUT file:///path/to/digital_customer_profile.csv @mysql_upload_stage AUTO_COMPRESS=TRUE OVERWRITE=TRUE;
PUT file:///path/to/digital_session.csv @mysql_upload_stage AUTO_COMPRESS=TRUE OVERWRITE=TRUE;
PUT file:///path/to/digital_event.csv @mysql_upload_stage AUTO_COMPRESS=TRUE OVERWRITE=TRUE;
*/

-- Option B: Using Snowflake UI
-- 1. Go to Data > Databases > CREDIT_DECISIONING_DB > RAW_ZONE > MYSQL_SRC > Stages
-- 2. Click on mysql_upload_stage
-- 3. Click "+ Files" and upload the CSV files

-- ============================================
-- Step 8: Load Data into Tables
-- ============================================

-- After files are uploaded to stage, run:

COPY INTO DIGITAL_CUSTOMER_PROFILE
FROM @mysql_upload_stage/digital_customer_profile.csv.gz
FILE_FORMAT = mysql_csv_format
ON_ERROR = 'CONTINUE'
PURGE = TRUE;

COPY INTO DIGITAL_SESSION
FROM @mysql_upload_stage/digital_session.csv.gz
FILE_FORMAT = mysql_csv_format
ON_ERROR = 'CONTINUE'
PURGE = TRUE;

COPY INTO DIGITAL_EVENT
FROM @mysql_upload_stage/digital_event.csv.gz
FILE_FORMAT = mysql_csv_format
ON_ERROR = 'CONTINUE'
PURGE = TRUE;

-- ============================================
-- Step 9: Verify Data
-- ============================================

SELECT 
    'DIGITAL_CUSTOMER_PROFILE' AS table_name, 
    COUNT(*) AS row_count,
    '100,000 expected' AS expected
FROM DIGITAL_CUSTOMER_PROFILE
UNION ALL
SELECT 
    'DIGITAL_SESSION', 
    COUNT(*),
    '1,000,000 expected'
FROM DIGITAL_SESSION
UNION ALL
SELECT 
    'DIGITAL_EVENT', 
    COUNT(*),
    '5,000,000 expected'
FROM DIGITAL_EVENT;

-- Check sample data
SELECT * FROM DIGITAL_CUSTOMER_PROFILE LIMIT 10;
SELECT * FROM DIGITAL_SESSION ORDER BY SESSION_START DESC LIMIT 10;
SELECT * FROM DIGITAL_EVENT ORDER BY EVENT_TIMESTAMP DESC LIMIT 10;

-- ============================================
-- Summary
-- ============================================

SELECT 
    '✅ MySQL Data Loaded to Snowflake!' AS status,
    'Tables available in RAW_ZONE.MYSQL_SRC' AS location,
    'Data is static (no real-time CDC without Openflow)' AS note;
