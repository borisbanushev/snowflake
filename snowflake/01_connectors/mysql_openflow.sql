-- ============================================
-- Snowflake Openflow Connector for MySQL Digital Banking
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE ETL_WH;

-- Create secret for MySQL password
CREATE OR REPLACE SECRET GOVERNANCE.POLICIES.mysql_digital_password
  TYPE = PASSWORD
  USERNAME = 'digitaluser'
  PASSWORD = 'DigitalPass!';

-- Create Openflow Connector for MySQL
-- Note: Replace connection string with your actual MySQL endpoint
CREATE OR REPLACE CONNECTOR RAW_ZONE.MYSQL_DIGITAL_OPENFLOW_CONNECTOR
  TYPE = 'MYSQL'
  CONNECTION_STRING = 'jdbc:mysql://localhost:3306/digital_banking'  -- Update with actual connection
  CREDENTIALS = (
    USERNAME = 'digitaluser'
    PASSWORD = SECRET 'GOVERNANCE.POLICIES.mysql_digital_password'
  )
  CDC_MODE = 'LOG_BASED'  -- Uses MySQL binlog for CDC
  DESTINATION_DATABASE = 'CREDIT_DECISIONING_DB'
  DESTINATION_SCHEMA = 'RAW_ZONE.MYSQL_SRC'
  TABLES = (
    'DIGITAL_CUSTOMER_PROFILE',
    'DIGITAL_SESSION',
    'DIGITAL_EVENT',
    'DIGITAL_KYC_DOCUMENT'
  )
  REFRESH_INTERVAL = '30 SECONDS'  -- High-frequency updates for digital events
  ENABLED = TRUE
  COMMENT = 'Openflow CDC connector for MySQL digital banking system';

-- Monitor connector status
SELECT 
    'MySQL Digital Openflow Connector created successfully' AS STATUS,
    'Data will sync every 30 seconds' AS SYNC_FREQUENCY;

-- Create monitoring view
CREATE OR REPLACE VIEW GOVERNANCE.AUDIT.OPENFLOW_CONNECTOR_STATUS AS
SELECT 
    CONNECTOR_NAME,
    STATUS,
    LAST_SYNC_TIME,
    DATEDIFF('SECOND', LAST_SYNC_TIME, CURRENT_TIMESTAMP()) AS SECONDS_SINCE_SYNC,
    RECORDS_PROCESSED,
    ERROR_COUNT,
    CASE 
        WHEN STATUS = 'RUNNING' AND DATEDIFF('MINUTE', LAST_SYNC_TIME, CURRENT_TIMESTAMP()) < 5 THEN 'HEALTHY'
        WHEN STATUS = 'RUNNING' THEN 'LAGGING'
        ELSE 'ERROR'
    END AS HEALTH_STATUS
FROM TABLE(INFORMATION_SCHEMA.CONNECTOR_HISTORY())
WHERE CONNECTOR_NAME IN ('ORACLE_T24_OPENFLOW_CONNECTOR', 'MYSQL_DIGITAL_OPENFLOW_CONNECTOR')
ORDER BY LAST_SYNC_TIME DESC;

SELECT * FROM GOVERNANCE.AUDIT.OPENFLOW_CONNECTOR_STATUS LIMIT 5;
