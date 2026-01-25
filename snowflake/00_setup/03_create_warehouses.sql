-- ============================================
-- Snowflake Credit Decisioning Platform
-- Step 3: Create Warehouses
-- ============================================

USE ROLE ACCOUNTADMIN;

-- ============================================
-- ETL WAREHOUSE - Data pipeline processing
-- ============================================

CREATE OR REPLACE WAREHOUSE ETL_WH WITH
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 3
  SCALING_POLICY = 'STANDARD'
  COMMENT = 'Data pipeline processing - bronze to silver to gold';

-- ============================================
-- ML WAREHOUSE - Machine learning workloads
-- ============================================

CREATE OR REPLACE WAREHOUSE ML_WH WITH
  WAREHOUSE_SIZE = 'LARGE'
  WAREHOUSE_TYPE = 'SNOWPARK-OPTIMIZED'
  AUTO_SUSPEND = 600
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 2
  COMMENT = 'ML training and inference - Snowpark optimized';

-- ============================================
-- APP WAREHOUSE - Streamlit application
-- ============================================

CREATE OR REPLACE WAREHOUSE APP_WH WITH
  WAREHOUSE_SIZE = 'SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 5
  SCALING_POLICY = 'STANDARD'
  COMMENT = 'Streamlit application queries';

-- ============================================
-- TRANSACTIONAL WAREHOUSE - Hybrid Tables (OLTP)
-- ============================================

CREATE OR REPLACE WAREHOUSE TRANSACTIONAL_WH WITH
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 3
  COMMENT = 'Hybrid table transactional workloads (Unistore)';

-- Grant usage
GRANT USAGE ON WAREHOUSE ETL_WH TO ROLE SYSADMIN;
GRANT USAGE ON WAREHOUSE ML_WH TO ROLE SYSADMIN;
GRANT USAGE ON WAREHOUSE APP_WH TO ROLE SYSADMIN;
GRANT USAGE ON WAREHOUSE TRANSACTIONAL_WH TO ROLE SYSADMIN;

SELECT 'All warehouses created successfully' AS STATUS;
