-- ============================================
-- Check Openflow Availability
-- ============================================

USE ROLE ACCOUNTADMIN;

-- Check if Openflow is enabled in your account
SHOW PARAMETERS LIKE 'ENABLE_OPENFLOW' IN ACCOUNT;

-- Check available connectors
-- SHOW CONNECTORS;  -- Uncomment if Openflow is enabled

-- Check your Snowflake edition
SELECT CURRENT_REGION() AS region, 
       CURRENT_ACCOUNT() AS account,
       CURRENT_VERSION() AS version;

-- Note: Openflow requires:
-- 1. Enterprise Edition or higher
-- 2. Openflow must be enabled by Snowflake support
-- 3. Only available in certain AWS/Azure regions
