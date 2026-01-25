-- ============================================
-- Apache Polaris Catalog Integration for Databricks
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE ETL_WH;

-- ============================================
-- Step 1: Create External Volume for Iceberg data
-- ============================================

-- Note: Update with your actual S3 bucket and AWS credentials
CREATE OR REPLACE EXTERNAL VOLUME DATABRICKS_ICEBERG_VOLUME
  STORAGE_LOCATIONS = (
    (
      NAME = 'databricks-iceberg-s3'
      STORAGE_PROVIDER = 'S3'
      STORAGE_BASE_URL = 's3://your-bank-datalake-bucket/iceberg/'  -- Update with your bucket
      STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/snowflake-polaris-access'  -- Update with your role
      STORAGE_AWS_EXTERNAL_ID = 'snowflake_polaris_external_id'  -- Use your external ID
    )
  )
  COMMENT = 'External volume for Databricks Iceberg tables';

-- Show the storage integration details for AWS setup
DESC EXTERNAL VOLUME DATABRICKS_ICEBERG_VOLUME;

-- ============================================
-- Step 2: Create Polaris OAuth Secret
-- ============================================

CREATE OR REPLACE SECRET GOVERNANCE.POLICIES.polaris_oauth_secret
  TYPE = OAUTH2
  OAUTH_CLIENT_ID = 'polaris-snowflake-client'  -- Update with your Polaris client ID
  OAUTH_CLIENT_SECRET = 'your-polaris-client-secret'  -- Update with your secret
  OAUTH_TOKEN_ENDPOINT = 'https://polaris.your-databricks.cloud/api/catalog/v1/oauth/tokens';

-- ============================================
-- Step 3: Create Polaris Catalog Integration
-- ============================================

CREATE OR REPLACE CATALOG INTEGRATION POLARIS_DATABRICKS_CATALOG
  CATALOG_SOURCE = POLARIS
  TABLE_FORMAT = ICEBERG
  CATALOG_NAMESPACE = 'credit_bureau_data'
  REST_CONFIG = (
    CATALOG_URI = 'https://polaris.your-databricks.cloud/api/catalog'  -- Update with your Polaris endpoint
    WAREHOUSE = 'databricks_warehouse'
  )
  REST_AUTHENTICATION = (
    TYPE = OAUTH
    OAUTH_CLIENT_ID = 'polaris-snowflake-client'
    OAUTH_CLIENT_SECRET = SECRET 'GOVERNANCE.POLICIES.polaris_oauth_secret'
    OAUTH_TOKEN_URI = 'https://polaris.your-databricks.cloud/api/catalog/v1/oauth/tokens'
    SCOPE = 'PRINCIPAL_ROLE:ALL'
  )
  ENABLED = TRUE
  COMMENT = 'Polaris catalog for Databricks credit bureau Iceberg tables';

-- Show catalog integration details
DESC CATALOG INTEGRATION POLARIS_DATABRICKS_CATALOG;

-- ============================================
-- Step 4: Create Iceberg Tables pointing to Databricks
-- ============================================

-- Credit Bureau Reports
CREATE OR REPLACE ICEBERG TABLE RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT
  CATALOG = 'POLARIS_DATABRICKS_CATALOG'
  EXTERNAL_VOLUME = 'DATABRICKS_ICEBERG_VOLUME'
  CATALOG_TABLE_NAME = 'credit_bureau.credit_bureau_report'
  AUTO_REFRESH = TRUE
  REFRESH_INTERVAL_SECONDS = 300  -- Refresh every 5 minutes
  COMMENT = 'Credit bureau reports from Databricks via Polaris';

-- Income Verification
CREATE OR REPLACE ICEBERG TABLE RAW_ZONE.DATABRICKS_SRC.INCOME_VERIFICATION
  CATALOG = 'POLARIS_DATABRICKS_CATALOG'
  EXTERNAL_VOLUME = 'DATABRICKS_ICEBERG_VOLUME'
  CATALOG_TABLE_NAME = 'credit_bureau.income_verification'
  AUTO_REFRESH = TRUE
  REFRESH_INTERVAL_SECONDS = 300
  COMMENT = 'Income verification data from Databricks via Polaris';

-- Alternative Data
CREATE OR REPLACE ICEBERG TABLE RAW_ZONE.DATABRICKS_SRC.ALTERNATIVE_DATA
  CATALOG = 'POLARIS_DATABRICKS_CATALOG'
  EXTERNAL_VOLUME = 'DATABRICKS_ICEBERG_VOLUME'
  CATALOG_TABLE_NAME = 'credit_bureau.alternative_data'
  AUTO_REFRESH = TRUE
  REFRESH_INTERVAL_SECONDS = 300
  COMMENT = 'Alternative credit data from Databricks via Polaris';

-- Fraud Indicators
CREATE OR REPLACE ICEBERG TABLE RAW_ZONE.DATABRICKS_SRC.FRAUD_INDICATORS
  CATALOG = 'POLARIS_DATABRICKS_CATALOG'
  EXTERNAL_VOLUME = 'DATABRICKS_ICEBERG_VOLUME'
  CATALOG_TABLE_NAME = 'credit_bureau.fraud_indicators'
  AUTO_REFRESH = TRUE
  REFRESH_INTERVAL_SECONDS = 300
  COMMENT = 'Fraud risk indicators from Databricks via Polaris';

-- ============================================
-- Step 5: Create Monitoring View
-- ============================================

CREATE OR REPLACE VIEW GOVERNANCE.AUDIT.POLARIS_SYNC_STATUS AS
SELECT 
    TABLE_NAME,
    CATALOG_NAME,
    LAST_REFRESH_TIME,
    REFRESH_STATUS,
    DATEDIFF('MINUTE', LAST_REFRESH_TIME, CURRENT_TIMESTAMP()) AS MINUTES_SINCE_REFRESH,
    CASE 
        WHEN REFRESH_STATUS = 'SUCCESS' AND DATEDIFF('MINUTE', LAST_REFRESH_TIME, CURRENT_TIMESTAMP()) < 10 
        THEN 'HEALTHY'
        WHEN REFRESH_STATUS = 'SUCCESS' THEN 'STALE'
        ELSE 'ERROR'
    END AS SYNC_HEALTH,
    ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.ICEBERG_TABLE_REFRESH_HISTORY())
WHERE CATALOG_NAME = 'POLARIS_DATABRICKS_CATALOG'
ORDER BY LAST_REFRESH_TIME DESC;

-- Test query
SELECT 
    'Polaris integration created successfully' AS STATUS,
    COUNT(*) AS ICEBERG_TABLES_CREATED
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'DATABRICKS_SRC'
AND TABLE_TYPE = 'ICEBERG';

-- View sync status
SELECT * FROM GOVERNANCE.AUDIT.POLARIS_SYNC_STATUS;
