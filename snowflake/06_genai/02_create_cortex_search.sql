-- ============================================
-- Snowflake Credit Decisioning Platform
-- GenAI Phase 1: Create Cortex Search Service
-- ============================================
-- Role: ACCOUNTADMIN
--
-- If you see "model unavailable in your region" / EMBED_TEXT_768 error:
-- Run this ONCE as ACCOUNTADMIN (account-level setting), then re-run this script:
--
--   ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
--
-- Or restrict to specific regions: 'AWS_US,AWS_EU' (see Snowflake docs).
-- https://docs.snowflake.com/en/user-guide/snowflake-cortex/cross-region-inference

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;
USE SCHEMA CORTEX;

-- ============================================
-- CREATE CORTEX SEARCH SERVICE
-- ============================================
-- Note: Cortex Search Service requires Enterprise Edition
-- ON = text column to search (from the query result), not the table name
-- ATTRIBUTES = columns available for filtering
-- WAREHOUSE = required for index builds and refreshes

CREATE OR REPLACE CORTEX SEARCH SERVICE POLICY_SEARCH_SERVICE
  ON CONTENT
  ATTRIBUTES POLICY_ID, DOCUMENT_NAME, DOCUMENT_TYPE, CATEGORY, EFFECTIVE_DATE, VERSION
  WAREHOUSE = COMPUTE_WH
  TARGET_LAG = '1 minute'
  AS (
    SELECT 
        POLICY_ID,
        DOCUMENT_NAME,
        DOCUMENT_TYPE,
        CATEGORY,
        FULL_TEXT AS CONTENT,
        EFFECTIVE_DATE,
        VERSION
    FROM CREDIT_DECISIONING_DB.CORTEX.CREDIT_POLICIES
    WHERE IS_ACTIVE = TRUE
      AND FULL_TEXT IS NOT NULL
  );

-- ============================================
-- NOTE: No SEARCH_POLICIES wrapper function
-- ============================================
-- SEARCH_PREVIEW() requires its second argument (query params JSON) to be a
-- compile-time constant, so we cannot wrap it in a UDF that takes (query_text, num_results).
-- The Cortex Agent uses SEARCH_SERVICE = POLICY_SEARCH_SERVICE directly to search policies.
-- For ad-hoc SQL testing, use SEARCH_PREVIEW with a literal JSON string below.

-- ============================================
-- TEST SEARCH (literal query only - constant required)
-- ============================================

-- Test 1: Search for credit score band policy
-- SEARCH_PREVIEW returns VARCHAR (JSON string); parse to VARIANT so resp['results'] works
WITH search_res AS (
    SELECT PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'CREDIT_DECISIONING_DB.CORTEX.POLICY_SEARCH_SERVICE',
        '{"query": "What is the policy for credit score band 8?", "columns": ["DOCUMENT_NAME", "CATEGORY", "CONTENT"], "limit": 3}'
    )) AS resp
),
flattened AS (
    SELECT PARSE_JSON(f.value) AS result_obj
    FROM search_res, LATERAL FLATTEN(INPUT => search_res.resp['results']) f
)
SELECT 
    'Test 1: Credit Score Band Policy' AS TEST_NAME,
    result_obj:DOCUMENT_NAME::VARCHAR AS DOCUMENT_NAME,
    result_obj:CATEGORY::VARCHAR AS CATEGORY,
    LEFT(result_obj:CONTENT::VARCHAR, 200) AS CONTENT_PREVIEW
FROM flattened;

-- Test 2: Search for DTI ratio policy
WITH search_res AS (
    SELECT PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'CREDIT_DECISIONING_DB.CORTEX.POLICY_SEARCH_SERVICE',
        '{"query": "What is the maximum debt to income ratio?", "columns": ["DOCUMENT_NAME", "CATEGORY", "CONTENT"], "limit": 3}'
    )) AS resp
),
flattened AS (
    SELECT PARSE_JSON(f.value) AS result_obj
    FROM search_res, LATERAL FLATTEN(INPUT => search_res.resp['results']) f
)
SELECT 
    'Test 2: DTI Ratio Policy' AS TEST_NAME,
    result_obj:DOCUMENT_NAME::VARCHAR AS DOCUMENT_NAME,
    result_obj:CATEGORY::VARCHAR AS CATEGORY,
    LEFT(result_obj:CONTENT::VARCHAR, 200) AS CONTENT_PREVIEW
FROM flattened;

-- ============================================
-- VERIFICATION
-- ============================================

SELECT 
    'Cortex Search Service created successfully' AS STATUS,
    SERVICE_NAME,
    TARGET_LAG,
    STATE
FROM INFORMATION_SCHEMA.SEARCH_SERVICES
WHERE SERVICE_SCHEMA = 'CORTEX'
AND SERVICE_NAME = 'POLICY_SEARCH_SERVICE';
