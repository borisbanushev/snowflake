-- ============================================
-- Snowflake Credit Decisioning Platform
-- ETL: Feature Engineering Dynamic Table
-- Creates 50+ ML features for credit scoring
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;

-- ============================================
-- CREDIT SCORING FEATURES
-- ============================================
-- This Dynamic Table creates all features needed for ML model training
-- Refreshes every 15 minutes automatically

CREATE OR REPLACE DYNAMIC TABLE ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES
  TARGET_LAG = '15 minutes'
  WAREHOUSE = COMPUTE_WH
  COMMENT = 'ML Feature Store - 50+ engineered features for credit scoring'
AS
SELECT 
    -- Customer ID and timestamp
    c.CUSTOMER_ID,
    CURRENT_TIMESTAMP() AS FEATURE_DATE,
    
    -- ============================================
    -- DEMOGRAPHIC FEATURES
    -- ============================================
    DATEDIFF('YEAR', c.DATE_OF_BIRTH, CURRENT_DATE()) AS F_AGE,
    CASE WHEN c.GENDER = 'M' THEN 1 ELSE 0 END AS F_GENDER_ENCODED,
    CASE 
        WHEN c.MARITAL_STATUS = 'SINGLE' THEN 1
        WHEN c.MARITAL_STATUS = 'MARRIED' THEN 2
        WHEN c.MARITAL_STATUS = 'DIVORCED' THEN 3
        ELSE 0
    END AS F_MARITAL_STATUS_ENCODED,
    
    -- ============================================
    -- RELATIONSHIP FEATURES
    -- ============================================
    DATEDIFF('MONTH', c.CUSTOMER_SINCE, CURRENT_DATE()) AS F_RELATIONSHIP_MONTHS,
    CASE WHEN c.CUSTOMER_STATUS = 'ACTIVE' THEN 1 ELSE 0 END AS F_IS_ACTIVE,
    
    -- ============================================
    -- FINANCIAL FEATURES - Accounts
    -- ============================================
    COALESCE(acc.TOTAL_ACCOUNTS, 0) AS F_TOTAL_ACCOUNTS,
    COALESCE(acc.TOTAL_BALANCE, 0) AS F_TOTAL_BALANCE,
    COALESCE(acc.AVG_BALANCE, 0) AS F_AVG_BALANCE,
    COALESCE(acc.MAX_BALANCE, 0) AS F_MAX_BALANCE,
    COALESCE(acc.TOTAL_AVAILABLE_LIMIT, 0) AS F_TOTAL_AVAILABLE_LIMIT,
    COALESCE(acc.UTILIZATION_RATIO, 0) AS F_ACCOUNT_UTILIZATION,
    
    -- ============================================
    -- FINANCIAL FEATURES - Loans
    -- ============================================
    COALESCE(loan.TOTAL_LOANS, 0) AS F_TOTAL_LOANS,
    COALESCE(loan.TOTAL_OUTSTANDING, 0) AS F_TOTAL_OUTSTANDING,
    COALESCE(loan.AVG_LOAN_AMOUNT, 0) AS F_AVG_LOAN_AMOUNT,
    COALESCE(loan.TOTAL_MONTHLY_PAYMENT, 0) AS F_TOTAL_MONTHLY_PAYMENT,
    COALESCE(loan.DAYS_PAST_DUE_MAX, 0) AS F_MAX_DAYS_PAST_DUE,
    COALESCE(loan.TOTAL_ARREARS, 0) AS F_TOTAL_ARREARS,
    COALESCE(loan.DELINQUENT_LOANS, 0) AS F_DELINQUENT_LOANS,
    
    -- ============================================
    -- DEBT-TO-INCOME RATIO
    -- ============================================
    CASE 
        WHEN COALESCE(loan.TOTAL_MONTHLY_PAYMENT, 0) > 0 
             AND COALESCE(acc.AVG_MONTHLY_INCOME, 0) > 0
        THEN loan.TOTAL_MONTHLY_PAYMENT / acc.AVG_MONTHLY_INCOME
        ELSE 0
    END AS F_DEBT_TO_INCOME,
    
    -- ============================================
    -- TRANSACTION FEATURES - 3 Month Window
    -- ============================================
    COALESCE(txn3m.TXN_COUNT_3M, 0) AS F_TXN_COUNT_3M,
    COALESCE(txn3m.TXN_AMOUNT_3M, 0) AS F_TXN_AMOUNT_3M,
    COALESCE(txn3m.AVG_TXN_AMOUNT_3M, 0) AS F_AVG_TXN_AMOUNT_3M,
    COALESCE(txn3m.DEBIT_COUNT_3M, 0) AS F_DEBIT_COUNT_3M,
    COALESCE(txn3m.CREDIT_COUNT_3M, 0) AS F_CREDIT_COUNT_3M,
    COALESCE(txn3m.TXN_VELOCITY_3M, 0) AS F_TXN_VELOCITY_3M, -- transactions per day
    
    -- ============================================
    -- TRANSACTION FEATURES - 6 Month Window
    -- ============================================
    COALESCE(txn6m.TXN_COUNT_6M, 0) AS F_TXN_COUNT_6M,
    COALESCE(txn6m.TXN_AMOUNT_6M, 0) AS F_TXN_AMOUNT_6M,
    COALESCE(txn6m.AVG_TXN_AMOUNT_6M, 0) AS F_AVG_TXN_AMOUNT_6M,
    
    -- ============================================
    -- TRANSACTION FEATURES - 12 Month Window
    -- ============================================
    COALESCE(txn12m.TXN_COUNT_12M, 0) AS F_TXN_COUNT_12M,
    COALESCE(txn12m.TXN_AMOUNT_12M, 0) AS F_TXN_AMOUNT_12M,
    
    -- ============================================
    -- CREDIT BUREAU FEATURES
    -- ============================================
    COALESCE(cb.CREDIT_SCORE, 650) AS F_CREDIT_SCORE, -- Default to 650 if missing
    COALESCE(cb.CREDIT_UTILIZATION, 0) AS F_CREDIT_UTILIZATION,
    COALESCE(cb.TOTAL_TRADELINES, 0) AS F_TOTAL_TRADELINES,
    COALESCE(cb.OPEN_TRADELINES, 0) AS F_OPEN_TRADELINES,
    COALESCE(cb.DELINQUENT_TRADELINES, 0) AS F_DELINQUENT_TRADELINES,
    COALESCE(cb.PUBLIC_RECORDS, 0) AS F_PUBLIC_RECORDS,
    COALESCE(cb.INQUIRIES_6M, 0) AS F_INQUIRIES_6M,
    COALESCE(cb.INQUIRIES_12M, 0) AS F_INQUIRIES_12M,
    
    -- ============================================
    -- DIGITAL BEHAVIOR FEATURES
    -- ============================================
    COALESCE(dig.LOGIN_COUNT, 0) AS F_LOGIN_COUNT,
    COALESCE(dig.SESSION_COUNT_30D, 0) AS F_SESSION_COUNT_30D,
    COALESCE(dig.AVG_SESSION_DURATION, 0) AS F_AVG_SESSION_DURATION,
    COALESCE(dig.EVENT_COUNT_30D, 0) AS F_EVENT_COUNT_30D,
    COALESCE(dig.DAYS_SINCE_LAST_LOGIN, 999) AS F_DAYS_SINCE_LAST_LOGIN,
    CASE WHEN dig.MFA_ENABLED = TRUE THEN 1 ELSE 0 END AS F_MFA_ENABLED,
    CASE WHEN dig.BIOMETRIC_ENABLED = TRUE THEN 1 ELSE 0 END AS F_BIOMETRIC_ENABLED,
    
    -- ============================================
    -- EMPLOYMENT & PROPERTY FEATURES
    -- ============================================
    -- These would come from income verification, using defaults for now
    0 AS F_YEARS_EMPLOYED, -- Placeholder - would come from income verification
    CASE WHEN c.SECTOR IN ('CORPORATE', 'BUSINESS') THEN 1 ELSE 0 END AS F_EMPLOYMENT_STATUS_ENCODED,
    0 AS F_PROPERTY_OWNER, -- Placeholder - would come from additional data
    
    -- ============================================
    -- RISK FEATURES
    -- ============================================
    CASE WHEN c.RISK_CATEGORY = 'HIGH' THEN 1 ELSE 0 END AS F_HIGH_RISK,
    CASE WHEN c.KYC_STATUS = 'VERIFIED' THEN 1 ELSE 0 END AS F_KYC_VERIFIED,
    DATEDIFF('DAYS', COALESCE(c.KYC_LAST_REVIEW, c.CUSTOMER_SINCE), CURRENT_DATE()) AS F_DAYS_SINCE_KYC_REVIEW,
    
    -- ============================================
    -- TARGET VARIABLE (for training)
    -- ============================================
    -- Create target based on credit score bands (0-9 for 10 bands)
    CASE 
        WHEN COALESCE(cb.CREDIT_SCORE, 650) >= 800 THEN 9
        WHEN COALESCE(cb.CREDIT_SCORE, 650) >= 750 THEN 8
        WHEN COALESCE(cb.CREDIT_SCORE, 650) >= 700 THEN 7
        WHEN COALESCE(cb.CREDIT_SCORE, 650) >= 650 THEN 6
        WHEN COALESCE(cb.CREDIT_SCORE, 650) >= 600 THEN 5
        WHEN COALESCE(cb.CREDIT_SCORE, 650) >= 550 THEN 4
        WHEN COALESCE(cb.CREDIT_SCORE, 650) >= 500 THEN 3
        WHEN COALESCE(cb.CREDIT_SCORE, 650) >= 450 THEN 2
        WHEN COALESCE(cb.CREDIT_SCORE, 650) >= 400 THEN 1
        ELSE 0
    END AS TARGET_CREDIT_SCORE_BAND

FROM CORE_BANKING.T24_CUSTOMER c

-- Account aggregations
LEFT JOIN (
    SELECT 
        CUSTOMER_ID,
        COUNT(*) AS TOTAL_ACCOUNTS,
        SUM(WORKING_BALANCE) AS TOTAL_BALANCE,
        AVG(WORKING_BALANCE) AS AVG_BALANCE,
        MAX(WORKING_BALANCE) AS MAX_BALANCE,
        SUM(AVAILABLE_LIMIT) AS TOTAL_AVAILABLE_LIMIT,
        CASE 
            WHEN SUM(AVAILABLE_LIMIT) > 0 
            THEN SUM(WORKING_BALANCE) / SUM(AVAILABLE_LIMIT)
            ELSE 0
        END AS UTILIZATION_RATIO,
        -- Estimate monthly income from transaction patterns (simplified)
        AVG(WORKING_BALANCE) * 0.1 AS AVG_MONTHLY_INCOME
    FROM CORE_BANKING.T24_ACCOUNT
    WHERE ACCOUNT_STATUS = 'ACTIVE'
    GROUP BY CUSTOMER_ID
) acc ON c.CUSTOMER_ID = acc.CUSTOMER_ID

-- Loan aggregations
LEFT JOIN (
    SELECT 
        CUSTOMER_ID,
        COUNT(*) AS TOTAL_LOANS,
        SUM(OUTSTANDING_PRINCIPAL) AS TOTAL_OUTSTANDING,
        AVG(PRINCIPAL_AMOUNT) AS AVG_LOAN_AMOUNT,
        SUM(MONTHLY_PAYMENT) AS TOTAL_MONTHLY_PAYMENT,
        MAX(DAYS_PAST_DUE) AS DAYS_PAST_DUE_MAX,
        SUM(ARREARS_AMOUNT) AS TOTAL_ARREARS,
        SUM(CASE WHEN DAYS_PAST_DUE > 0 THEN 1 ELSE 0 END) AS DELINQUENT_LOANS
    FROM CORE_BANKING.T24_LOAN
    WHERE LOAN_STATUS IN ('ACTIVE', 'PAST_DUE')
    GROUP BY CUSTOMER_ID
) loan ON c.CUSTOMER_ID = loan.CUSTOMER_ID

-- Transaction features - 3 months
LEFT JOIN (
    SELECT 
        t.CUSTOMER_ID,
        COUNT(*) AS TXN_COUNT_3M,
        SUM(ABS(AMOUNT)) AS TXN_AMOUNT_3M,
        AVG(ABS(AMOUNT)) AS AVG_TXN_AMOUNT_3M,
        SUM(CASE WHEN AMOUNT < 0 THEN 1 ELSE 0 END) AS DEBIT_COUNT_3M,
        SUM(CASE WHEN AMOUNT > 0 THEN 1 ELSE 0 END) AS CREDIT_COUNT_3M,
        COUNT(*) / 90.0 AS TXN_VELOCITY_3M
    FROM CORE_BANKING.T24_TRANSACTION t
    WHERE t.VALUE_DATE >= DATEADD('DAY', -90, CURRENT_DATE())
    GROUP BY t.CUSTOMER_ID
) txn3m ON c.CUSTOMER_ID = txn3m.CUSTOMER_ID

-- Transaction features - 6 months
LEFT JOIN (
    SELECT 
        t.CUSTOMER_ID,
        COUNT(*) AS TXN_COUNT_6M,
        SUM(ABS(AMOUNT)) AS TXN_AMOUNT_6M,
        AVG(ABS(AMOUNT)) AS AVG_TXN_AMOUNT_6M
    FROM CORE_BANKING.T24_TRANSACTION t
    WHERE t.VALUE_DATE >= DATEADD('DAY', -180, CURRENT_DATE())
    GROUP BY t.CUSTOMER_ID
) txn6m ON c.CUSTOMER_ID = txn6m.CUSTOMER_ID

-- Transaction features - 12 months
LEFT JOIN (
    SELECT 
        t.CUSTOMER_ID,
        COUNT(*) AS TXN_COUNT_12M,
        SUM(ABS(AMOUNT)) AS TXN_AMOUNT_12M
    FROM CORE_BANKING.T24_TRANSACTION t
    WHERE t.VALUE_DATE >= DATEADD('DAY', -365, CURRENT_DATE())
    GROUP BY t.CUSTOMER_ID
) txn12m ON c.CUSTOMER_ID = txn12m.CUSTOMER_ID

-- Credit Bureau features
LEFT JOIN (
    SELECT 
        cs.CUSTOMER_ID,
        cs.SCORE AS CREDIT_SCORE,
        cs.CREDIT_UTILIZATION,
        COUNT(DISTINCT tl.TRADELINE_ID) AS TOTAL_TRADELINES,
        SUM(CASE WHEN tl.ACCOUNT_STATUS = 'OPEN' THEN 1 ELSE 0 END) AS OPEN_TRADELINES,
        SUM(CASE WHEN tl.PAYMENT_STATUS IN ('PAST_DUE', 'DELINQUENT', 'DEFAULT') THEN 1 ELSE 0 END) AS DELINQUENT_TRADELINES,
        COUNT(DISTINCT pr.RECORD_ID) AS PUBLIC_RECORDS,
        SUM(CASE WHEN ci.INQUIRY_DATE >= DATEADD('MONTH', -6, CURRENT_DATE()) THEN 1 ELSE 0 END) AS INQUIRIES_6M,
        SUM(CASE WHEN ci.INQUIRY_DATE >= DATEADD('MONTH', -12, CURRENT_DATE()) THEN 1 ELSE 0 END) AS INQUIRIES_12M
    FROM CREDIT_BUREAU.CREDIT_SCORE cs
    LEFT JOIN CREDIT_BUREAU.TRADELINE tl ON cs.CUSTOMER_ID = tl.CUSTOMER_ID
    LEFT JOIN CREDIT_BUREAU.PUBLIC_RECORD pr ON cs.CUSTOMER_ID = pr.CUSTOMER_ID
    LEFT JOIN CREDIT_BUREAU.CREDIT_INQUIRY ci ON cs.CUSTOMER_ID = ci.CUSTOMER_ID
    GROUP BY cs.CUSTOMER_ID, cs.SCORE, cs.CREDIT_UTILIZATION
) cb ON c.CUSTOMER_ID = cb.CUSTOMER_ID

-- Digital behavior features
LEFT JOIN (
    SELECT 
        dcp.CUSTOMER_ID,
        dcp.LOGIN_COUNT,
        dcp.MFA_ENABLED,
        dcp.BIOMETRIC_ENABLED,
        COUNT(DISTINCT ds.SESSION_ID) AS SESSION_COUNT_30D,
        AVG(ds.DURATION_SECONDS) AS AVG_SESSION_DURATION,
        COUNT(DISTINCT de.EVENT_ID) AS EVENT_COUNT_30D,
        DATEDIFF('DAY', dcp.LAST_LOGIN, CURRENT_DATE()) AS DAYS_SINCE_LAST_LOGIN
    FROM DIGITAL_BANKING.DIGITAL_CUSTOMER_PROFILE dcp
    LEFT JOIN DIGITAL_BANKING.DIGITAL_SESSION ds 
        ON dcp.DIGITAL_ID = ds.DIGITAL_ID
        AND ds.SESSION_START >= DATEADD('DAY', -30, CURRENT_DATE())
    LEFT JOIN DIGITAL_BANKING.DIGITAL_EVENT de
        ON ds.SESSION_ID = de.SESSION_ID
        AND de.EVENT_TIMESTAMP >= DATEADD('DAY', -30, CURRENT_DATE())
    GROUP BY dcp.CUSTOMER_ID, dcp.LOGIN_COUNT, dcp.MFA_ENABLED, 
             dcp.BIOMETRIC_ENABLED, dcp.LAST_LOGIN
) dig ON c.CUSTOMER_ID = dig.CUSTOMER_ID;

-- Grant permissions
GRANT SELECT ON DYNAMIC TABLE ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES TO ROLE SYSADMIN;

-- Verify creation
SELECT 
    'Feature Store Created' AS STATUS,
    COUNT(*) AS FEATURE_COUNT,
    COUNT(DISTINCT CUSTOMER_ID) AS CUSTOMER_COUNT
FROM ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES;

SELECT 'Feature engineering Dynamic Table created successfully!' AS STATUS;
