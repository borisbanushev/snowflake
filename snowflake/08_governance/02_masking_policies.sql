-- ============================================
-- Dynamic Data Masking Policies
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE ETL_WH;

-- ============================================
-- MASKING POLICY: Customer Names
-- ============================================

CREATE OR REPLACE MASKING POLICY GOVERNANCE.POLICIES.MASK_CUSTOMER_NAME AS
  (val VARCHAR) RETURNS VARCHAR ->
  CASE
    -- Full access for admins and compliance
    WHEN IS_ROLE_IN_SESSION('ACCOUNTADMIN') THEN val
    WHEN IS_ROLE_IN_SESSION('COMPLIANCE_OFFICER') THEN val
    
    -- Partial access for credit officers (first initial + last name)
    WHEN IS_ROLE_IN_SESSION('CREDIT_OFFICER') THEN 
      CONCAT(LEFT(val, 1), '. ', SPLIT_PART(val, ' ', -1))
    
    -- Masked for all others
    ELSE '***MASKED***'
  END
  COMMENT = 'Mask customer names based on role';

-- ============================================
-- MASKING POLICY: Date of Birth
-- ============================================

CREATE OR REPLACE MASKING POLICY GOVERNANCE.POLICIES.MASK_DOB AS
  (val DATE) RETURNS DATE ->
  CASE
    -- Full access for admins and compliance
    WHEN IS_ROLE_IN_SESSION('ACCOUNTADMIN') THEN val
    WHEN IS_ROLE_IN_SESSION('COMPLIANCE_OFFICER') THEN val
    
    -- Year only for credit officers (for age verification)
    WHEN IS_ROLE_IN_SESSION('CREDIT_OFFICER') THEN 
      DATE_FROM_PARTS(YEAR(val), 1, 1)
    
    -- Null for all others
    ELSE NULL
  END
  COMMENT = 'Mask date of birth - show year only for authorized roles';

-- ============================================
-- MASKING POLICY: Income
-- ============================================

CREATE OR REPLACE MASKING POLICY GOVERNANCE.POLICIES.MASK_INCOME AS
  (val NUMBER) RETURNS VARCHAR ->
  CASE
    -- Full access for admins and credit officers
    WHEN IS_ROLE_IN_SESSION('ACCOUNTADMIN') THEN val::VARCHAR
    WHEN IS_ROLE_IN_SESSION('CREDIT_OFFICER') THEN val::VARCHAR
    
    -- Range for risk managers
    WHEN IS_ROLE_IN_SESSION('RISK_MANAGER') THEN 
      CASE 
        WHEN val < 50000 THEN '$0-50K'
        WHEN val < 100000 THEN '$50-100K'
        WHEN val < 200000 THEN '$100-200K'
        WHEN val < 500000 THEN '$200-500K'
        ELSE '$500K+'
      END
    
    -- Masked for all others
    ELSE '***MASKED***'
  END
  COMMENT = 'Mask income - show ranges for some roles';

-- ============================================
-- MASKING POLICY: Account Numbers
-- ============================================

CREATE OR REPLACE MASKING POLICY GOVERNANCE.POLICIES.MASK_ACCOUNT_NUMBER AS
  (val VARCHAR) RETURNS VARCHAR ->
  CASE
    -- Full access for admins and compliance
    WHEN IS_ROLE_IN_SESSION('ACCOUNTADMIN') THEN val
    WHEN IS_ROLE_IN_SESSION('COMPLIANCE_OFFICER') THEN val
    
    -- Last 4 digits for authorized users
    WHEN IS_ROLE_IN_SESSION('CREDIT_OFFICER') THEN 
      CONCAT('****', RIGHT(val, 4))
    WHEN IS_ROLE_IN_SESSION('RISK_MANAGER') THEN 
      CONCAT('****', RIGHT(val, 4))
    
    -- Fully masked for all others
    ELSE '****'
  END
  COMMENT = 'Mask account numbers - show last 4 digits for authorized roles';

-- ============================================
-- APPLY MASKING POLICIES
-- ============================================

-- Apply to Customer 360 table
ALTER TABLE ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED 
  MODIFY COLUMN FULL_NAME 
  SET MASKING POLICY GOVERNANCE.POLICIES.MASK_CUSTOMER_NAME;

ALTER TABLE ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED 
  MODIFY COLUMN DATE_OF_BIRTH 
  SET MASKING POLICY GOVERNANCE.POLICIES.MASK_DOB;

ALTER TABLE ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED 
  MODIFY COLUMN VERIFIED_ANNUAL_INCOME 
  SET MASKING POLICY GOVERNANCE.POLICIES.MASK_INCOME;

-- ============================================
-- TEST MASKING POLICIES
-- ============================================

-- Test as different roles
-- SET ROLE = CREDIT_OFFICER;
-- SELECT CUSTOMER_ID, FULL_NAME, DATE_OF_BIRTH, VERIFIED_ANNUAL_INCOME
-- FROM ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED LIMIT 5;

-- SET ROLE = RISK_MANAGER;
-- SELECT CUSTOMER_ID, FULL_NAME, DATE_OF_BIRTH, VERIFIED_ANNUAL_INCOME
-- FROM ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED LIMIT 5;

SELECT 'Masking policies created and applied successfully' AS STATUS,
       'Test with different roles to verify masking' AS NEXT_STEP;

-- View applied masking policies
SELECT 
    POLICY_DB,
    POLICY_SCHEMA,
    POLICY_NAME,
    REF_DATABASE_NAME,
    REF_SCHEMA_NAME,
    REF_ENTITY_NAME,
    REF_COLUMN_NAME,
    POLICY_KIND
FROM SNOWFLAKE.ACCOUNT_USAGE.POLICY_REFERENCES
WHERE POLICY_DB = 'CREDIT_DECISIONING_DB'
AND POLICY_KIND = 'MASKING_POLICY'
ORDER BY REF_ENTITY_NAME, REF_COLUMN_NAME;
