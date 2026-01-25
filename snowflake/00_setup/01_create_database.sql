-- ============================================
-- Snowflake Credit Decisioning Platform
-- Step 1: Create Database
-- ============================================

USE ROLE ACCOUNTADMIN;

-- Create main database
CREATE OR REPLACE DATABASE CREDIT_DECISIONING_DB
  DATA_RETENTION_TIME_IN_DAYS = 90
  COMMENT = 'Financial Services Credit Decisioning Demo - Showcasing Snowflake Enterprise Capabilities';

-- Grant usage to roles
GRANT USAGE ON DATABASE CREDIT_DECISIONING_DB TO ROLE SYSADMIN;

-- Set context
USE DATABASE CREDIT_DECISIONING_DB;

SELECT 'Database CREDIT_DECISIONING_DB created successfully' AS STATUS;
