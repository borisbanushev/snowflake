-- ============================================
-- Snowflake Openflow Connector for MySQL RDS
-- For AWS RDS MySQL with CDC enabled
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE ETL_WH;

-- ============================================
-- Step 0: Create Required Schemas
-- ============================================

-- Create schemas if they don't exist
CREATE SCHEMA IF NOT EXISTS RAW_ZONE
    COMMENT = 'Bronze layer - raw ingested data from external sources';

CREATE SCHEMA IF NOT EXISTS GOVERNANCE
    COMMENT = 'Data governance, policies, and audit';

-- ============================================
-- Step 1: Create Secret for MySQL Credentials
-- ============================================

CREATE OR REPLACE SECRET GOVERNANCE.mysql_rds_password
  TYPE = PASSWORD
  USERNAME = 'digitaluser'
  PASSWORD = 'DigitalPass123!';  -- Update if you changed the password

-- Verify secret
SELECT 'MySQL RDS secret created successfully' AS status;

-- ============================================
-- Step 2: Create Openflow Connector
-- ============================================

-- Note: Replace <RDS_ENDPOINT> with your actual RDS endpoint
-- Example: snowflake-credit-demo-mysql.abc123.ap-southeast-1.rds.amazonaws.com

CREATE OR REPLACE CONNECTOR RAW_ZONE.MYSQL_DIGITAL_OPENFLOW_CONNECTOR
  TYPE = 'MYSQL'
  CONNECTION_STRING = 'jdbc:mysql://snowflake-credit-demo-mysql.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com:3306/digital_banking'
  CREDENTIALS = (
    USERNAME = 'digitaluser'
    PASSWORD = SECRET 'GOVERNANCE.mysql_rds_password'
  )
  CDC_MODE = 'LOG_BASED'  -- Uses MySQL binlog for CDC
  DESTINATION_DATABASE = 'CREDIT_DECISIONING_DB'
  DESTINATION_SCHEMA = 'RAW_ZONE.MYSQL_SRC'
  TABLES = (
    'DIGITAL_CUSTOMER_PROFILE',
    'DIGITAL_SESSION',
    'DIGITAL_EVENT'
  )
  REFRESH_INTERVAL = '30 SECONDS'  -- High-frequency updates for digital events
  ENABLED = TRUE
  COMMENT = 'Openflow CDC connector for MySQL RDS digital banking system';

-- ============================================
-- Step 3: Monitor Initial Sync
-- ============================================

-- Check connector status
SELECT 
    'Openflow connector created' AS STATUS,
    'Initial sync will take 5-15 minutes' AS NOTE;

-- Wait 2-3 minutes, then check sync progress
SELECT 
    CONNECTOR_NAME,
    STATUS,
    LAST_SYNC_TIME,
    RECORDS_PROCESSED,
    ERROR_COUNT
FROM TABLE(INFORMATION_SCHEMA.CONNECTOR_HISTORY())
WHERE CONNECTOR_NAME = 'MYSQL_DIGITAL_OPENFLOW_CONNECTOR'
ORDER BY LAST_SYNC_TIME DESC
LIMIT 5;

-- ============================================
-- Step 4: Verify Data
-- ============================================

-- After initial sync completes (5-15 minutes), verify:

USE SCHEMA RAW_ZONE.MYSQL_SRC;

-- Check row counts
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

-- Check recent data
SELECT * FROM DIGITAL_CUSTOMER_PROFILE LIMIT 10;
SELECT * FROM DIGITAL_SESSION ORDER BY SESSION_START DESC LIMIT 10;
SELECT * FROM DIGITAL_EVENT ORDER BY EVENT_TIMESTAMP DESC LIMIT 10;

-- ============================================
-- Step 5: Create Monitoring Views
-- ============================================

CREATE OR REPLACE VIEW GOVERNANCE.OPENFLOW_MYSQL_STATUS AS
SELECT 
    CONNECTOR_NAME,
    STATUS,
    LAST_SYNC_TIME,
    TIMESTAMPDIFF('SECOND', LAST_SYNC_TIME, CURRENT_TIMESTAMP()) AS SECONDS_SINCE_SYNC,
    RECORDS_PROCESSED,
    ERROR_COUNT,
    CASE 
        WHEN STATUS = 'RUNNING' AND TIMESTAMPDIFF('MINUTE', LAST_SYNC_TIME, CURRENT_TIMESTAMP()) < 2 THEN '🟢 HEALTHY'
        WHEN STATUS = 'RUNNING' AND TIMESTAMPDIFF('MINUTE', LAST_SYNC_TIME, CURRENT_TIMESTAMP()) < 10 THEN '🟡 LAGGING'
        WHEN STATUS = 'RUNNING' THEN '🟠 DELAYED'
        WHEN STATUS = 'FAILED' THEN '🔴 ERROR'
        ELSE '⚪ ' || STATUS
    END AS HEALTH_STATUS
FROM TABLE(INFORMATION_SCHEMA.CONNECTOR_HISTORY())
WHERE CONNECTOR_NAME = 'MYSQL_DIGITAL_OPENFLOW_CONNECTOR'
ORDER BY LAST_SYNC_TIME DESC
LIMIT 1;

-- Check status
SELECT * FROM GOVERNANCE.OPENFLOW_MYSQL_STATUS;

-- ============================================
-- Step 6: Test CDC (Change Data Capture)
-- ============================================

-- To test CDC, make a change in MySQL RDS:
/*
-- Connect to RDS:
mysql -h <RDS_ENDPOINT> -u digitaluser -pDigitalPass123! digital_banking

-- Make a test update:
UPDATE DIGITAL_CUSTOMER_PROFILE 
SET LOGIN_COUNT = LOGIN_COUNT + 1 
WHERE CUSTOMER_ID = 'CUS-000001';

-- Wait 30-60 seconds for CDC sync

-- Check in Snowflake:
SELECT * FROM RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE 
WHERE CUSTOMER_ID = 'CUS-000001';
*/

-- ============================================
-- Step 7: Query Change History (CDC Journal)
-- ============================================

-- Openflow creates journal tables to track all changes
-- Check what journal tables were created:
SHOW TABLES IN RAW_ZONE LIKE '%JOURNAL%';

-- Example: Query change history for a customer
-- Journal table format: <TABLE_NAME>_JOURNAL
/*
SELECT 
    _OPERATION_TYPE,  -- INSERT, UPDATE, DELETE
    _OPERATION_TIMESTAMP,
    CUSTOMER_ID,
    EMAIL,
    LOGIN_COUNT
FROM RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE_JOURNAL
WHERE CUSTOMER_ID = 'CUS-000001'
ORDER BY _OPERATION_TIMESTAMP DESC;
*/

-- ============================================
-- Summary
-- ============================================

SELECT 
    '✅ Openflow MySQL Connector Setup Complete!' AS STATUS,
    'Data syncs every 30 seconds via CDC' AS SYNC_MODE,
    'Check GOVERNANCE.OPENFLOW_MYSQL_STATUS for health' AS MONITORING;

-- ============================================
-- Troubleshooting
-- ============================================

/*
Common Issues:

1. Connection Timeout
   - Check RDS security group allows Snowflake IP ranges
   - Verify RDS is publicly accessible
   - Check VPC settings

2. Authentication Failed
   - Verify username/password in secret
   - Check MySQL user has REPLICATION CLIENT privilege

3. Binlog Not Enabled
   - Verify parameter group has binlog_format=ROW
   - Check with: SHOW VARIABLES LIKE 'binlog_format';

4. Tables Not Syncing
   - Ensure tables have PRIMARY KEY
   - Check connector logs in Openflow UI
   - Verify table names are correct (case-sensitive)

5. Slow Initial Sync
   - Normal for 6M+ rows
   - Monitor: SELECT * FROM GOVERNANCE.AUDIT.OPENFLOW_MYSQL_STATUS;
   - Increase Openflow runtime size if needed

For detailed logs:
SELECT * FROM TABLE(INFORMATION_SCHEMA.CONNECTOR_LOGS())
WHERE CONNECTOR_NAME = 'MYSQL_DIGITAL_OPENFLOW_CONNECTOR'
ORDER BY EVENT_TIMESTAMP DESC
LIMIT 100;
*/
