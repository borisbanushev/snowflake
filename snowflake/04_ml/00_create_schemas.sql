-- ============================================
-- Snowflake Credit Decisioning Platform
-- ML: Create ML Zone Schemas
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;

-- Create ML Zone schemas
-- Note: Snowflake doesn't support nested schemas, so we create separate schemas
CREATE SCHEMA IF NOT EXISTS ML_MODELS;
CREATE SCHEMA IF NOT EXISTS ML_INFERENCE;
CREATE SCHEMA IF NOT EXISTS ML_PREDICTIONS;

-- Grant permissions
GRANT USAGE ON SCHEMA ML_MODELS TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA ML_INFERENCE TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA ML_PREDICTIONS TO ROLE SYSADMIN;

SELECT 'ML Zone schemas created successfully' AS STATUS;
