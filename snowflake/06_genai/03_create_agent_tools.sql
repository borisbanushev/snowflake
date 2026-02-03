-- ============================================
-- Snowflake Credit Decisioning Platform
-- GenAI Phase 1: Create Agent Tools
-- ============================================
-- Role: ACCOUNTADMIN

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;
USE SCHEMA AGENT_TOOLS;

-- ============================================
-- TOOL 1: GET CUSTOMER DATA
-- ============================================
-- Returns customer 360 profile as JSON

CREATE OR REPLACE FUNCTION GET_CUSTOMER_DATA(
    customer_id VARCHAR
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
    SELECT OBJECT_CONSTRUCT(
        'CUSTOMER_ID', CUSTOMER_ID,
        'FULL_NAME', FULL_NAME,
        'CREDIT_SCORE', CREDIT_SCORE,
        'RISK_CATEGORY', RISK_CATEGORY,
        'VERIFIED_ANNUAL_INCOME', (COALESCE(AVG_BALANCE, 0) * 12),
        'DEBT_TO_INCOME_RATIO', DEBT_TO_INCOME_RATIO,
        'RELATIONSHIP_TENURE_MONTHS', RELATIONSHIP_MONTHS,
        'TOTAL_DEPOSITS', TOTAL_BALANCE,
        'TOTAL_LOANS_OUTSTANDING', TOTAL_OUTSTANDING,
        'F_TOTAL_BALANCE', TOTAL_BALANCE,
        'F_DEBT_TO_INCOME', DEBT_TO_INCOME_RATIO
    )::VARIANT
    FROM ANALYTICS_CUSTOMER_360.CUSTOMER_360_UNIFIED
    WHERE CUSTOMER_ID = customer_id
    LIMIT 1
$$;

-- ============================================
-- TOOL 2: GET CREDIT SCORE
-- ============================================
-- Returns credit score and rating from Customer 360 (bureau + view).
-- For real-time ML prediction use: CALL ML_INFERENCE.PREDICT_CREDIT_SCORE_BY_ID_V4('<customer_id>');

CREATE OR REPLACE FUNCTION GET_CREDIT_SCORE(
    customer_id VARCHAR
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
    SELECT OBJECT_CONSTRUCT(
        'CUSTOMER_ID', CUSTOMER_ID,
        'CREDIT_SCORE', CREDIT_SCORE,
        'CREDIT_RATING', CREDIT_RATING,
        'CREDIT_UTILIZATION', CREDIT_UTILIZATION,
        'DEBT_TO_INCOME_RATIO', DEBT_TO_INCOME_RATIO,
        'SOURCE', 'CUSTOMER_360'
    )::VARIANT
    FROM ANALYTICS_CUSTOMER_360.CUSTOMER_360_UNIFIED
    WHERE CUSTOMER_ID = customer_id
    LIMIT 1
$$;

-- ============================================
-- TOOL 3: GET TRANSACTION HISTORY
-- ============================================
-- Returns recent transaction summary from core banking (T24)

CREATE OR REPLACE FUNCTION GET_TRANSACTION_HISTORY(
    customer_id VARCHAR,
    months INTEGER DEFAULT 12
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
    SELECT OBJECT_CONSTRUCT(
        'CUSTOMER_ID', customer_id,
        'PERIOD_MONTHS', months,
        'TOTAL_TRANSACTIONS', COUNT(*),
        'TOTAL_AMOUNT', SUM(AMOUNT),
        'AVG_TRANSACTION_AMOUNT', AVG(AMOUNT),
        'LATE_PAYMENTS', 0,
        'ON_TIME_PAYMENTS', 0
    )::VARIANT
    FROM CREDIT_DECISIONING_DB.CORE_BANKING.T24_TRANSACTION
    WHERE CUSTOMER_ID = customer_id
      AND VALUE_DATE >= DATEADD('MONTH', -months, CURRENT_DATE())
$$;

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

GRANT USAGE ON FUNCTION CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_CUSTOMER_DATA(VARCHAR) 
  TO ROLE SYSADMIN;

GRANT USAGE ON FUNCTION CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_CREDIT_SCORE(VARCHAR) 
  TO ROLE SYSADMIN;

GRANT USAGE ON FUNCTION CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_TRANSACTION_HISTORY(VARCHAR, INTEGER) 
  TO ROLE SYSADMIN;

-- ============================================
-- TEST FUNCTIONS
-- ============================================

-- Test 1: Get customer data
SELECT 
    'Test 1: Customer Data' AS TEST_NAME,
    GET_CUSTOMER_DATA('CUS-000001') AS CUSTOMER_DATA;

-- Test 2: Get credit score (if customer exists in predictions)
-- Note: This will only work if ML model has scored this customer
SELECT 
    'Test 2: Credit Score' AS TEST_NAME,
    GET_CREDIT_SCORE('CUS-000001') AS CREDIT_SCORE;

-- Test 3: Get transaction history
SELECT 
    'Test 3: Transaction History' AS TEST_NAME,
    GET_TRANSACTION_HISTORY('CUS-000001', 12) AS TXN_HISTORY;

-- ============================================
-- VERIFICATION
-- ============================================

SELECT 
    'Agent tools created successfully' AS STATUS,
    FUNCTION_NAME,
    FUNCTION_TYPE
FROM INFORMATION_SCHEMA.FUNCTIONS
WHERE FUNCTION_SCHEMA = 'AGENT_TOOLS'
ORDER BY FUNCTION_NAME;
