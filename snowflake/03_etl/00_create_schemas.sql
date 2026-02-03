-- ============================================
-- Snowflake Credit Decisioning Platform
-- ETL: Create Analytics Zone Schemas
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;

-- Create Analytics Zone schemas for ETL outputs
-- Note: Snowflake doesn't support nested schemas, so we create separate schemas
CREATE SCHEMA IF NOT EXISTS ANALYTICS_FEATURE_STORE;
CREATE SCHEMA IF NOT EXISTS ANALYTICS_CUSTOMER_360;
CREATE SCHEMA IF NOT EXISTS ANALYTICS_RISK_ANALYTICS;

-- Grant permissions
GRANT USAGE ON SCHEMA ANALYTICS_FEATURE_STORE TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA ANALYTICS_CUSTOMER_360 TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA ANALYTICS_RISK_ANALYTICS TO ROLE SYSADMIN;

SELECT 'Analytics Zone schemas created successfully' AS STATUS;
