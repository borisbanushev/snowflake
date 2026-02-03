-- ============================================
-- Snowflake Credit Decisioning Platform
-- GenAI Phase 1: Load Policy Documents
-- ============================================
-- Role: ACCOUNTADMIN

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;
USE SCHEMA CORTEX;

-- ============================================
-- CREATE POLICY DOCUMENTS TABLE
-- ============================================

CREATE OR REPLACE TABLE CREDIT_POLICIES (
    POLICY_ID VARCHAR(36) DEFAULT UUID_STRING() PRIMARY KEY,
    DOCUMENT_NAME VARCHAR(200) NOT NULL,
    DOCUMENT_TYPE VARCHAR(50),  -- POLICY, GUIDELINE, REGULATION, PROCEDURE
    CATEGORY VARCHAR(100),       -- CREDIT_SCORING, RISK_MANAGEMENT, COLLECTIONS, etc.
    VERSION VARCHAR(20),
    EFFECTIVE_DATE DATE,
    EXPIRY_DATE DATE,
    
    -- Content
    FULL_TEXT TEXT,
    
    -- Metadata
    DEPARTMENT VARCHAR(100),
    APPROVED_BY VARCHAR(100),
    LAST_REVIEWED DATE,
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Bank credit policy documents for Cortex Search';

-- ============================================
-- LOAD CREDIT SCORING POLICY
-- ============================================

INSERT INTO CREDIT_POLICIES 
(DOCUMENT_NAME, DOCUMENT_TYPE, CATEGORY, VERSION, EFFECTIVE_DATE, FULL_TEXT, DEPARTMENT, IS_ACTIVE)
VALUES
('Credit Scoring Model Usage Policy', 'POLICY', 'CREDIT_SCORING', 'v2.1', '2025-01-01',
$$CREDIT SCORING MODEL USAGE POLICY
Version 2.1 - Effective January 2025

1. PURPOSE
This policy establishes guidelines for using the XGBoost Credit Scoring Model in credit decisioning.

2. CREDIT SCORE BANDS AND DECISIONS
The ML model produces a score band from 1-10, mapped to credit ratings:

Score Band | Rating | Default Decision | Max Credit Limit Multiplier
--------------------------------------------------------------------------
10         | A+     | AUTO APPROVE     | 3.0x annual income
9          | A      | AUTO APPROVE     | 2.5x annual income
8          | B+     | AUTO APPROVE     | 2.0x annual income
7          | B      | APPROVE          | 1.5x annual income
6          | C+     | APPROVE          | 1.0x annual income
5          | C      | REFER            | 0.75x annual income
4          | C-     | REFER            | 0.5x annual income
3          | D      | DECLINE          | N/A
2          | E      | DECLINE          | N/A
1          | F      | DECLINE          | N/A

3. OVERRIDE AUTHORITY
- Score Bands 5-6: Credit Officers may approve with documented justification
- Score Bands 3-4: Requires Senior Credit Manager approval
- Score Bands 1-2: Requires Credit Committee approval (loans > $50,000)

4. SPECIAL CONSIDERATIONS
- Existing customers with 24+ months good standing: May upgrade 1 band
- Government employees: May upgrade 1 band for stability
- Self-employed < 2 years: Downgrade 1 band unless collateralized

5. MODEL LIMITATIONS
The model should not be the sole decision factor. Officers must consider:
- Purpose of credit
- Industry/employment sector risks
- Collateral quality
- Relationship history
- Local market conditions

6. DOCUMENTATION REQUIREMENTS
All approvals must include:
- ML score band and rating
- Key factors influencing decision
- Any policy exceptions applied
- Justification for overrides

7. MODEL GOVERNANCE
- Model version must be logged for each decision
- Model performance monitored quarterly
- Model retraining annually or when performance degrades
- Bias testing required before deployment

8. PROHIBITED FACTORS
The following must NOT influence credit decisions:
- Race, color, religion, national origin
- Gender, marital status
- Age (except for legal capacity)
- Source of income (public assistance)
- Geographic location (redlining)

9. APPEALS PROCESS
Declined applicants have right to:
- Receive specific reasons for decline
- Request manual review within 30 days
- Provide additional supporting documentation

10. COMPLIANCE
This policy complies with:
- Fair Credit Reporting Act (FCRA)
- Equal Credit Opportunity Act (ECOA)
- Model Risk Management SR 11-7
- Local consumer protection regulations$$,
'Risk Management', TRUE);

-- ============================================
-- ADDITIONAL POLICY DOCUMENTS (Examples)
-- ============================================

-- Personal Loan Guidelines
INSERT INTO CREDIT_POLICIES 
(DOCUMENT_NAME, DOCUMENT_TYPE, CATEGORY, VERSION, EFFECTIVE_DATE, FULL_TEXT, DEPARTMENT, IS_ACTIVE)
VALUES
('Personal Loan Guidelines', 'GUIDELINE', 'CREDIT_PRODUCTS', 'v1.0', '2025-01-01',
$$PERSONAL LOAN GUIDELINES
Version 1.0 - Effective January 2025

1. ELIGIBILITY CRITERIA
- Minimum age: 21 years
- Minimum income: $30,000 per year
- Minimum credit score: 600
- Maximum DTI ratio: 40%
- Employment: Minimum 6 months at current job

2. LOAN AMOUNTS
- Minimum: $5,000
- Maximum: $100,000 (or 3x annual income, whichever is lower)
- Loan-to-income ratio: Maximum 3.0x for highest credit scores

3. INTEREST RATES
Interest rates are determined by credit score bands:
- Score Band 10 (A+): 5.5% - 6.5% APR
- Score Band 9 (A): 6.0% - 7.0% APR
- Score Band 8 (B+): 6.5% - 7.5% APR
- Score Band 7 (B): 7.0% - 8.5% APR
- Score Band 6 (C+): 8.0% - 9.5% APR
- Score Band 5 (C): 9.5% - 11.0% APR
- Score Bands 1-4: Not eligible for unsecured personal loans

4. TERM OPTIONS
- 12 months (minimum)
- 24 months
- 36 months (standard)
- 48 months (for loans > $25,000)
- 60 months (for loans > $50,000)

5. DOCUMENTATION REQUIRED
- Proof of income (pay stubs, tax returns)
- Employment verification
- Bank statements (3 months)
- Government-issued ID
- Credit report authorization

6. APPROVAL PROCESS
- Applications with score band 8+ (B+ or higher): Auto-approve
- Applications with score band 6-7 (B to C+): Standard review
- Applications with score band 5 (C): Manual review required
- Applications with score band <5: Decline

7. COLLATERAL REQUIREMENTS
- Unsecured loans: Score band 6+ required
- Secured loans: Score band 3+ with acceptable collateral
- Collateral types: Real estate, vehicles, savings accounts, investments

8. SPECIAL PROGRAMS
- Relationship discount: 0.25% APR reduction for existing customers 24+ months
- Auto-pay discount: 0.25% APR reduction for automatic payments
- Government employee discount: 0.5% APR reduction$$,
'Product Management', TRUE);

-- ============================================
-- VERIFICATION
-- ============================================

SELECT 
    'Policy documents loaded successfully' AS STATUS,
    COUNT(*) AS TOTAL_POLICIES,
    COUNT(DISTINCT CATEGORY) AS CATEGORIES
FROM CREDIT_POLICIES
WHERE IS_ACTIVE = TRUE;

SELECT 
    DOCUMENT_NAME,
    CATEGORY,
    VERSION,
    EFFECTIVE_DATE,
    LENGTH(FULL_TEXT) AS TEXT_LENGTH
FROM CREDIT_POLICIES
WHERE IS_ACTIVE = TRUE
ORDER BY CATEGORY, DOCUMENT_NAME;
