-- ============================================
-- Snowflake Openflow Connector for Oracle T24
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE ETL_WH;

-- Create secret for Oracle password
CREATE OR REPLACE SECRET GOVERNANCE.POLICIES.oracle_t24_password
  TYPE = PASSWORD
  USERNAME = 't24user'
  PASSWORD = 'T24UserPass!';

-- Create Openflow Connector for Oracle T24
-- Note: Replace connection string with your actual Oracle endpoint
CREATE OR REPLACE CONNECTOR RAW_ZONE.ORACLE_T24_OPENFLOW_CONNECTOR
  TYPE = 'ORACLE'
  CONNECTION_STRING = 'jdbc:oracle:thin:@localhost:1521:XE'  -- Update with actual connection
  CREDENTIALS = (
    USERNAME = 't24user'
    PASSWORD = SECRET 'GOVERNANCE.POLICIES.oracle_t24_password'
  )
  CDC_MODE = 'LOG_BASED'  -- Uses Oracle LogMiner for CDC
  DESTINATION_DATABASE = 'CREDIT_DECISIONING_DB'
  DESTINATION_SCHEMA = 'RAW_ZONE.ORACLE_T24_SRC'
  TABLES = (
    'T24_CUSTOMER',
    'T24_ACCOUNT',
    'T24_LOAN',
    'T24_TRANSACTION',
    'T24_PAYMENT_SCHEDULE',
    'T24_COLLATERAL'
  )
  REFRESH_INTERVAL = '1 MINUTE'  -- Near real-time CDC
  ENABLED = TRUE
  COMMENT = 'Openflow CDC connector for Oracle T24 core banking system';

-- Monitor connector status
SELECT 
    'Oracle T24 Openflow Connector created successfully' AS STATUS,
    'Check INFORMATION_SCHEMA.CONNECTOR_HISTORY() for sync status' AS NEXT_STEP;

-- Query to monitor connector performance
-- Run this periodically to check sync status:
/*
SELECT 
    CONNECTOR_NAME,
    STATUS,
    LAST_SYNC_TIME,
    RECORDS_PROCESSED,
    ERROR_COUNT,
    ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.CONNECTOR_HISTORY(
    CONNECTOR_NAME => 'ORACLE_T24_OPENFLOW_CONNECTOR'
))
ORDER BY LAST_SYNC_TIME DESC
LIMIT 10;
*/
