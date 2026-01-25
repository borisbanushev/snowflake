# Snowflake Credit Decisioning Platform
## Complete Implementation Plan

**Version:** 2.0  
**Date:** January 25, 2026  
**Use Case:** Financial Services - Credit Decisioning & Risk Management  
**Target Platform:** Snowflake Enterprise Edition (AWS Singapore)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Data Model Design](#data-model-design)
4. [External Data Source Setup](#external-data-source-setup)
5. [Snowflake Core Implementation](#snowflake-core-implementation)
6. [Feature 1: SnowConvert AI Migration](#feature-1-snowconvert-ai-migration)
7. [Feature 2: Unistore & Hybrid Tables](#feature-2-unistore--hybrid-tables)
8. [Feature 3: Cortex Search with Policy Documents](#feature-3-cortex-search-with-policy-documents)
9. [Feature 4: Cortex Agent - AI Credit Analyst](#feature-4-cortex-agent---ai-credit-analyst)
10. [Feature 5: Snowflake Intelligence](#feature-5-snowflake-intelligence)
11. [Feature 6: Data Masking & PII Detection](#feature-6-data-masking--pii-detection)
12. [Feature 7: Apache Polaris Integration](#feature-7-apache-polaris-integration)
13. [Feature 8: Snowflake Openflow](#feature-8-snowflake-openflow)
14. [Feature 9: Snowpark ML Pipeline](#feature-9-snowpark-ml-pipeline)
15. [Feature 10: Dynamic Tables](#feature-10-dynamic-tables)
16. [Streamlit Application](#streamlit-application)
17. [Implementation Phases](#implementation-phases)
18. [GitHub Repository Structure](#github-repository-structure)
19. [Sample Data Generation](#sample-data-generation)
20. [Testing & Validation](#testing--validation)

---

## Executive Summary

This project demonstrates Snowflake's capabilities as a unified enterprise data platform for financial services. It implements an end-to-end credit decisioning system that:

- **Integrates data** from Oracle T24 (core banking), MySQL (digital banking), and Databricks (credit bureau) using Openflow CDC and Apache Polaris
- **Unifies data** into a governed Customer 360 view with automatic PII detection and masking
- **Scores applications** using Snowpark ML XGBoost model with real-time inference
- **Leverages AI agents** that evaluate applications using bank policies retrieved via Cortex Search
- **Enables natural language analytics** through Snowflake Intelligence for different personas
- **Processes transactions** using Unistore Hybrid Tables for low-latency OLTP workloads
- **Surfaces insights** through an interactive Streamlit application

### Key Differentiators Showcased

| Feature | Purpose in Demo |
|---------|----------------|
| **Snowflake Openflow** | Real-time CDC from Oracle T24 and MySQL |
| **Apache Polaris Catalog** | Federated access to Databricks Iceberg tables |
| **Cortex Agents** | AI-powered credit analyst that makes decisions |
| **Cortex Search** | RAG-based policy document retrieval |
| **Cortex Analyst** | Natural language to SQL queries |
| **Snowflake Intelligence** | Persona-based conversational analytics |
| **Unistore (Hybrid Tables)** | OLTP credit application processing |
| **Snowpark ML** | XGBoost model training and real-time inference |
| **Dynamic Tables** | Declarative data pipelines |
| **SnowConvert AI** | T24 PL/SQL to Snowflake migration |
| **Horizon Catalog** | Data lineage, classification, and governance |
| **Data Masking** | Role-based dynamic PII masking |
| **Native Apps (Bonus)** | Package as distributable Snowflake app |

---

## Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL DATA SOURCES                                          │
├───────────────────┬───────────────────┬─────────────────────────────────────────────────┤
│   DATABRICKS      │      MySQL        │              Oracle (T24)                        │
│  (Iceberg/Polaris)│   (Openflow CDC)  │           (Openflow CDC)                         │
│                   │                   │                                                  │
│ • Credit Bureau   │ • Digital Banking │ • Core Banking Tables                           │
│ • Alt Data        │ • Sessions/Events │ • PL/SQL Procedures ──► SnowConvert AI          │
│ • Fraud Scores    │ • eKYC Documents  │ • T24 Enquiries      ──► Snowflake SQL          │
└────────┬──────────┴─────────┬─────────┴──────────────────────┬──────────────────────────┘
         │                    │                                 │
         │ Apache Polaris     │ Openflow                        │ Openflow + SnowConvert
         │ (Iceberg REST)     │ (Managed CDC)                   │ (Managed CDC + Migration)
         │                    │                                 │
         ▼                    ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         SNOWFLAKE DATA PLATFORM                                          │
│                         (Enterprise - AWS Singapore)                                     │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                    DATA INGESTION LAYER                                          │    │
│  │  • Openflow Connectors (Oracle CDC, MySQL CDC)                                  │    │
│  │  • Polaris Catalog Integration (Databricks Iceberg)                             │    │
│  │  • SnowConvert AI (T24 PL/SQL → Snowflake SQL migration)                        │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                    GOVERNANCE LAYER (Horizon Catalog)                            │    │
│  │  • Automatic PII Detection (names, SSN, emails, phone)                          │    │
│  │  • Data Classification Tags (CONFIDENTIAL, PII, SENSITIVE)                      │    │
│  │  • Dynamic Data Masking (role-based)                                            │    │
│  │  • Column-Level Lineage Tracking                                                │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                    PROCESSING LAYER (Dynamic Tables)                             │    │
│  │  • Bronze → Silver → Gold medallion architecture                                │    │
│  │  • Customer 360 Unified View                                                     │    │
│  │  • Feature Engineering for ML                                                    │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                                 │
│              ┌─────────────────────────┴─────────────────────────┐                      │
│              ▼                                                   ▼                      │
│  ┌───────────────────────────────┐           ┌───────────────────────────────────┐      │
│  │     SNOWPARK ML ZONE          │           │      UNISTORE (Hybrid Tables)     │      │
│  │                               │           │                                   │      │
│  │  • Feature Store              │           │  • CREDIT_APPLICATIONS (OLTP)     │      │
│  │  • XGBoost Training           │           │  • CREDIT_DECISIONS (OLTP)        │      │
│  │  • Model Registry             │           │  • AGENT_SESSIONS (OLTP)          │      │
│  │  • Real-time UDF Inference    │           │  • Real-time reads/writes         │      │
│  └───────────────────────────────┘           │  • Concurrent transactions        │      │
│                                              └───────────────────────────────────┘      │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         CORTEX AI LAYER                                          │    │
│  │                                                                                  │    │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────────┐     │    │
│  │  │ CORTEX SEARCH   │  │ CORTEX ANALYST   │  │ CORTEX AGENT                │     │    │
│  │  │                 │  │                  │  │ (Credit Decisioning Agent)  │     │    │
│  │  │ • Bank Policies │  │ • Text-to-SQL    │  │                             │     │    │
│  │  │ • Credit Guides │  │ • Semantic Model │  │ • Evaluates applications    │     │    │
│  │  │ • Regulations   │  │ • NL Queries     │  │ • Applies bank policies     │     │    │
│  │  │ • RAG Context   │  │                  │  │ • Uses ML credit score      │     │    │
│  │  └────────┬────────┘  └────────┬─────────┘  │ • Makes recommendations     │     │    │
│  │           │                    │            │ • Explains decisions        │     │    │
│  │           └────────────────────┴────────────┴──────────────┬──────────────┘     │    │
│  │                                                            │                     │    │
│  │                                                            ▼                     │    │
│  │                              ┌─────────────────────────────────────────┐         │    │
│  │                              │      SNOWFLAKE INTELLIGENCE             │         │    │
│  │                              │                                         │         │    │
│  │                              │  Natural language interface for:        │         │    │
│  │                              │  • Credit Officers                      │         │    │
│  │                              │  • Risk Managers                        │         │    │
│  │                              │  • Compliance Teams                     │         │    │
│  │                              │  • Branch Managers                      │         │    │
│  │                              └─────────────────────────────────────────┘         │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         STREAMLIT APPLICATION                                    │    │
│  │                                                                                  │    │
│  │  • Executive Dashboard          • AI Credit Agent Interface                     │    │
│  │  • Customer 360 View            • Policy Document Manager                       │    │
│  │  • Credit Application Portal    • Governance & Lineage Explorer                 │    │
│  │  • Portfolio Analytics          • Natural Language Analytics                    │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Snowflake Object Hierarchy

```
CREDIT_DECISIONING_DB
├── RAW_ZONE                          # Bronze layer
│   ├── DATABRICKS_SRC               # Polaris-managed Iceberg tables
│   ├── MYSQL_SRC                    # Openflow CDC streams
│   └── ORACLE_T24_SRC               # Openflow CDC streams
│
├── CURATED_ZONE                      # Silver layer  
│   ├── CUSTOMER                     # Cleaned customer entities
│   ├── ACCOUNTS                     # Cleaned account entities
│   ├── TRANSACTIONS                 # Cleaned transaction entities
│   ├── DIGITAL                      # Cleaned digital banking entities
│   └── T24_MIGRATED                 # SnowConverted T24 procedures
│
├── ANALYTICS_ZONE                    # Gold layer
│   ├── CUSTOMER_360                 # Unified customer view
│   ├── FEATURE_STORE                # ML feature engineering
│   └── METRICS                      # Business KPIs
│
├── ML_ZONE                           # Machine learning
│   ├── TRAINING                     # Training datasets
│   ├── MODELS                       # Model registry
│   └── INFERENCE                    # Prediction outputs
│
├── APP_ZONE                          # Application layer
│   ├── STREAMLIT                    # App-specific objects
│   ├── CORTEX                       # AI/LLM objects
│   ├── TRANSACTIONAL                # Hybrid Tables (Unistore)
│   └── INTELLIGENCE                 # Snowflake Intelligence configs
│
└── GOVERNANCE                        # Governance objects
    ├── TAGS                         # Data classification
    ├── POLICIES                     # Masking & row access
    ├── AUDIT                        # Access logging
    └── MIGRATION                    # SnowConvert tracking
```

---

## Data Model Design

### 1. Oracle T24 Source (Core Banking) - 6 Tables

#### Table: `T24_CUSTOMER`
```sql
CREATE TABLE T24_CUSTOMER (
    CUSTOMER_ID VARCHAR(20) PRIMARY KEY,
    MNEMONIC VARCHAR(50),
    SHORT_NAME VARCHAR(100),
    NAME_1 VARCHAR(100),
    NAME_2 VARCHAR(100),
    GENDER VARCHAR(10),
    DATE_OF_BIRTH DATE,
    MARITAL_STATUS VARCHAR(20),
    NATIONALITY VARCHAR(3),
    RESIDENCE VARCHAR(3),
    SECTOR VARCHAR(10),
    INDUSTRY VARCHAR(10),
    TARGET_MARKET VARCHAR(20),
    CUSTOMER_STATUS VARCHAR(20),
    CUSTOMER_SINCE DATE,
    KYC_STATUS VARCHAR(20),
    KYC_LAST_REVIEW DATE,
    RISK_CATEGORY VARCHAR(20),
    RELATIONSHIP_MANAGER VARCHAR(50),
    BRANCH_CODE VARCHAR(10),
    CREATED_DATE TIMESTAMP_NTZ,
    MODIFIED_DATE TIMESTAMP_NTZ
);
```

#### Table: `T24_ACCOUNT`
```sql
CREATE TABLE T24_ACCOUNT (
    ACCOUNT_ID VARCHAR(20) PRIMARY KEY,
    CUSTOMER_ID VARCHAR(20),
    ACCOUNT_TITLE VARCHAR(100),
    CATEGORY VARCHAR(10),
    PRODUCT_CODE VARCHAR(20),
    PRODUCT_NAME VARCHAR(100),
    CURRENCY VARCHAR(3),
    WORKING_BALANCE NUMBER(18,2),
    ONLINE_ACTUAL_BAL NUMBER(18,2),
    LOCKED_AMOUNT NUMBER(18,2),
    AVAILABLE_LIMIT NUMBER(18,2),
    ACCOUNT_STATUS VARCHAR(20),
    OPENING_DATE DATE,
    LAST_ACTIVITY_DATE DATE,
    INTEREST_RATE NUMBER(8,4),
    BRANCH_CODE VARCHAR(10),
    JOINT_HOLDER_1 VARCHAR(20),
    JOINT_HOLDER_2 VARCHAR(20),
    CREATED_DATE TIMESTAMP_NTZ,
    MODIFIED_DATE TIMESTAMP_NTZ
);
```

#### Table: `T24_LOAN`
```sql
CREATE TABLE T24_LOAN (
    LOAN_ID VARCHAR(20) PRIMARY KEY,
    CUSTOMER_ID VARCHAR(20),
    ACCOUNT_ID VARCHAR(20),
    LOAN_TYPE VARCHAR(30),
    PRODUCT_CODE VARCHAR(20),
    PRODUCT_NAME VARCHAR(100),
    CURRENCY VARCHAR(3),
    PRINCIPAL_AMOUNT NUMBER(18,2),
    OUTSTANDING_PRINCIPAL NUMBER(18,2),
    INTEREST_RATE NUMBER(8,4),
    INTEREST_TYPE VARCHAR(20),
    TERM_MONTHS INTEGER,
    MONTHLY_PAYMENT NUMBER(18,2),
    START_DATE DATE,
    MATURITY_DATE DATE,
    NEXT_PAYMENT_DATE DATE,
    PAYMENTS_MADE INTEGER,
    PAYMENTS_REMAINING INTEGER,
    DAYS_PAST_DUE INTEGER,
    ARREARS_AMOUNT NUMBER(18,2),
    LOAN_STATUS VARCHAR(20),
    COLLATERAL_TYPE VARCHAR(30),
    COLLATERAL_VALUE NUMBER(18,2),
    LTV_RATIO NUMBER(8,4),
    APPROVAL_DATE DATE,
    APPROVED_BY VARCHAR(50),
    CREATED_DATE TIMESTAMP_NTZ,
    MODIFIED_DATE TIMESTAMP_NTZ
);
```

#### Table: `T24_TRANSACTION`
```sql
CREATE TABLE T24_TRANSACTION (
    TRANSACTION_ID VARCHAR(30) PRIMARY KEY,
    ACCOUNT_ID VARCHAR(20),
    CUSTOMER_ID VARCHAR(20),
    TRANSACTION_TYPE VARCHAR(30),
    TRANSACTION_CODE VARCHAR(10),
    TRANSACTION_DESC VARCHAR(200),
    AMOUNT NUMBER(18,2),
    CURRENCY VARCHAR(3),
    AMOUNT_LCY NUMBER(18,2),
    EXCHANGE_RATE NUMBER(12,6),
    VALUE_DATE DATE,
    BOOKING_DATE DATE,
    PROCESSING_TIME TIMESTAMP_NTZ,
    BALANCE_AFTER NUMBER(18,2),
    CHANNEL VARCHAR(30),
    MERCHANT_NAME VARCHAR(100),
    MERCHANT_CATEGORY VARCHAR(50),
    COUNTERPARTY_ACCT VARCHAR(30),
    COUNTERPARTY_NAME VARCHAR(100),
    COUNTERPARTY_BANK VARCHAR(100),
    REFERENCE VARCHAR(50),
    REVERSAL_FLAG BOOLEAN,
    REVERSED_TXN_ID VARCHAR(30),
    CREATED_DATE TIMESTAMP_NTZ
);
```

#### Table: `T24_PAYMENT_SCHEDULE`
```sql
CREATE TABLE T24_PAYMENT_SCHEDULE (
    SCHEDULE_ID VARCHAR(30) PRIMARY KEY,
    LOAN_ID VARCHAR(20),
    CUSTOMER_ID VARCHAR(20),
    INSTALLMENT_NUMBER INTEGER,
    DUE_DATE DATE,
    PRINCIPAL_DUE NUMBER(18,2),
    INTEREST_DUE NUMBER(18,2),
    TOTAL_DUE NUMBER(18,2),
    PRINCIPAL_PAID NUMBER(18,2),
    INTEREST_PAID NUMBER(18,2),
    TOTAL_PAID NUMBER(18,2),
    PAYMENT_DATE DATE,
    PAYMENT_STATUS VARCHAR(20),
    DAYS_LATE INTEGER,
    PENALTY_AMOUNT NUMBER(18,2),
    CREATED_DATE TIMESTAMP_NTZ,
    MODIFIED_DATE TIMESTAMP_NTZ
);
```

#### Table: `T24_COLLATERAL`
```sql
CREATE TABLE T24_COLLATERAL (
    COLLATERAL_ID VARCHAR(20) PRIMARY KEY,
    LOAN_ID VARCHAR(20),
    CUSTOMER_ID VARCHAR(20),
    COLLATERAL_TYPE VARCHAR(30),
    DESCRIPTION VARCHAR(500),
    ORIGINAL_VALUE NUMBER(18,2),
    CURRENT_VALUE NUMBER(18,2),
    VALUATION_DATE DATE,
    VALUATION_SOURCE VARCHAR(100),
    CURRENCY VARCHAR(3),
    LOCATION VARCHAR(200),
    INSURANCE_POLICY VARCHAR(50),
    INSURANCE_EXPIRY DATE,
    LIEN_POSITION INTEGER,
    REGISTRATION_REF VARCHAR(50),
    STATUS VARCHAR(20),
    CREATED_DATE TIMESTAMP_NTZ,
    MODIFIED_DATE TIMESTAMP_NTZ
);
```

### 2. MySQL Source (Digital Banking) - 4 Tables

#### Table: `DIGITAL_CUSTOMER_PROFILE`
```sql
CREATE TABLE DIGITAL_CUSTOMER_PROFILE (
    DIGITAL_ID VARCHAR(36) PRIMARY KEY,
    CUSTOMER_ID VARCHAR(20),
    EMAIL VARCHAR(100),
    MOBILE_NUMBER VARCHAR(20),
    USERNAME VARCHAR(50),
    REGISTRATION_DATE TIMESTAMP,
    LAST_LOGIN TIMESTAMP,
    LOGIN_COUNT INTEGER,
    FAILED_LOGIN_COUNT INTEGER,
    MFA_ENABLED BOOLEAN,
    MFA_TYPE VARCHAR(20),
    DEVICE_COUNT INTEGER,
    PRIMARY_DEVICE_TYPE VARCHAR(20),
    BIOMETRIC_ENABLED BOOLEAN,
    PUSH_NOTIFICATIONS BOOLEAN,
    EMAIL_VERIFIED BOOLEAN,
    MOBILE_VERIFIED BOOLEAN,
    EKYC_STATUS VARCHAR(20),
    EKYC_DATE TIMESTAMP,
    PREFERRED_LANGUAGE VARCHAR(10),
    TIMEZONE VARCHAR(50),
    CREATED_DATE TIMESTAMP,
    MODIFIED_DATE TIMESTAMP
);
```

#### Table: `DIGITAL_SESSION`
```sql
CREATE TABLE DIGITAL_SESSION (
    SESSION_ID VARCHAR(36) PRIMARY KEY,
    DIGITAL_ID VARCHAR(36),
    CUSTOMER_ID VARCHAR(20),
    SESSION_START TIMESTAMP,
    SESSION_END TIMESTAMP,
    DURATION_SECONDS INTEGER,
    DEVICE_ID VARCHAR(100),
    DEVICE_TYPE VARCHAR(20),
    DEVICE_MODEL VARCHAR(50),
    OS_VERSION VARCHAR(20),
    APP_VERSION VARCHAR(20),
    IP_ADDRESS VARCHAR(45),
    GEOLOCATION_LAT NUMBER(10,7),
    GEOLOCATION_LON NUMBER(10,7),
    CITY VARCHAR(100),
    COUNTRY VARCHAR(3),
    PAGES_VIEWED INTEGER,
    TRANSACTIONS_INITIATED INTEGER,
    TRANSACTIONS_COMPLETED INTEGER,
    ERROR_COUNT INTEGER,
    SESSION_QUALITY_SCORE NUMBER(5,2),
    EXIT_REASON VARCHAR(30),
    CREATED_DATE TIMESTAMP
);
```

#### Table: `DIGITAL_EVENT`
```sql
CREATE TABLE DIGITAL_EVENT (
    EVENT_ID VARCHAR(36) PRIMARY KEY,
    SESSION_ID VARCHAR(36),
    DIGITAL_ID VARCHAR(36),
    CUSTOMER_ID VARCHAR(20),
    EVENT_TYPE VARCHAR(50),
    EVENT_NAME VARCHAR(100),
    EVENT_TIMESTAMP TIMESTAMP,
    PAGE_NAME VARCHAR(100),
    ELEMENT_ID VARCHAR(100),
    EVENT_DATA TEXT,
    RESPONSE_TIME_MS INTEGER,
    SUCCESS BOOLEAN,
    ERROR_CODE VARCHAR(20),
    ERROR_MESSAGE VARCHAR(500),
    CREATED_DATE TIMESTAMP
);
```

#### Table: `DIGITAL_KYC_DOCUMENT`
```sql
CREATE TABLE DIGITAL_KYC_DOCUMENT (
    DOCUMENT_ID VARCHAR(36) PRIMARY KEY,
    DIGITAL_ID VARCHAR(36),
    CUSTOMER_ID VARCHAR(20),
    DOCUMENT_TYPE VARCHAR(30),
    DOCUMENT_NUMBER VARCHAR(50),
    ISSUING_COUNTRY VARCHAR(3),
    ISSUE_DATE DATE,
    EXPIRY_DATE DATE,
    UPLOAD_DATE TIMESTAMP,
    VERIFICATION_STATUS VARCHAR(20),
    VERIFICATION_DATE TIMESTAMP,
    VERIFICATION_METHOD VARCHAR(30),
    CONFIDENCE_SCORE NUMBER(5,2),
    REJECTION_REASON VARCHAR(200),
    FACE_MATCH_SCORE NUMBER(5,2),
    LIVENESS_CHECK BOOLEAN,
    CREATED_DATE TIMESTAMP,
    MODIFIED_DATE TIMESTAMP
);
```

### 3. Databricks Source (Customer 360 & External Data) - 4 Iceberg Tables

#### Table: `CREDIT_BUREAU_REPORT`
```sql
CREATE ICEBERG TABLE CREDIT_BUREAU_REPORT (
    REPORT_ID STRING,
    CUSTOMER_ID STRING,
    BUREAU_NAME STRING,
    REPORT_DATE DATE,
    CREDIT_SCORE INT,
    SCORE_VERSION STRING,
    TOTAL_ACCOUNTS INT,
    OPEN_ACCOUNTS INT,
    CLOSED_ACCOUNTS INT,
    DELINQUENT_ACCOUNTS INT,
    TOTAL_CREDIT_LIMIT DECIMAL(18,2),
    TOTAL_BALANCE DECIMAL(18,2),
    CREDIT_UTILIZATION DECIMAL(5,2),
    OLDEST_ACCOUNT_AGE_MONTHS INT,
    AVERAGE_ACCOUNT_AGE_MONTHS INT,
    HARD_INQUIRIES_12M INT,
    SOFT_INQUIRIES_12M INT,
    PUBLIC_RECORDS INT,
    COLLECTIONS_COUNT INT,
    COLLECTIONS_AMOUNT DECIMAL(18,2),
    PAYMENT_HISTORY_ONTIME_PCT DECIMAL(5,2),
    WORST_DELINQUENCY_EVER STRING,
    MONTHS_SINCE_DELINQUENCY INT,
    CREATED_TIMESTAMP TIMESTAMP
);
```

#### Table: `INCOME_VERIFICATION`
```sql
CREATE ICEBERG TABLE INCOME_VERIFICATION (
    VERIFICATION_ID STRING,
    CUSTOMER_ID STRING,
    VERIFICATION_DATE DATE,
    VERIFICATION_SOURCE STRING,
    EMPLOYER_NAME STRING,
    EMPLOYMENT_STATUS STRING,
    EMPLOYMENT_TYPE STRING,
    JOB_TITLE STRING,
    EMPLOYMENT_START_DATE DATE,
    YEARS_AT_EMPLOYER DECIMAL(4,1),
    ANNUAL_INCOME DECIMAL(18,2),
    MONTHLY_INCOME DECIMAL(18,2),
    INCOME_CURRENCY STRING,
    INCOME_STABILITY_SCORE DECIMAL(5,2),
    ADDITIONAL_INCOME DECIMAL(18,2),
    ADDITIONAL_INCOME_SOURCE STRING,
    DEBT_TO_INCOME_RATIO DECIMAL(5,2),
    VERIFICATION_CONFIDENCE DECIMAL(5,2),
    CREATED_TIMESTAMP TIMESTAMP
);
```

#### Table: `ALTERNATIVE_DATA`
```sql
CREATE ICEBERG TABLE ALTERNATIVE_DATA (
    ALT_DATA_ID STRING,
    CUSTOMER_ID STRING,
    DATA_DATE DATE,
    RENT_PAYMENT_HISTORY STRING,
    RENT_MONTHS_REPORTED INT,
    UTILITY_PAYMENT_HISTORY STRING,
    UTILITY_MONTHS_REPORTED INT,
    TELECOM_PAYMENT_HISTORY STRING,
    TELECOM_MONTHS_REPORTED INT,
    SOCIAL_MEDIA_PRESENCE BOOLEAN,
    LINKEDIN_VERIFIED BOOLEAN,
    PROFESSIONAL_NETWORK_SCORE DECIMAL(5,2),
    RESIDENTIAL_STABILITY_YEARS DECIMAL(4,1),
    PROPERTY_OWNERSHIP STRING,
    VEHICLE_OWNERSHIP BOOLEAN,
    EDUCATION_LEVEL STRING,
    INSURANCE_HISTORY STRING,
    BANK_ACCOUNT_AGE_MONTHS INT,
    SAVINGS_PATTERN STRING,
    EXPENSE_STABILITY_SCORE DECIMAL(5,2),
    CREATED_TIMESTAMP TIMESTAMP
);
```

#### Table: `FRAUD_INDICATORS`
```sql
CREATE ICEBERG TABLE FRAUD_INDICATORS (
    INDICATOR_ID STRING,
    CUSTOMER_ID STRING,
    ASSESSMENT_DATE DATE,
    IDENTITY_VERIFICATION_SCORE DECIMAL(5,2),
    ADDRESS_VERIFICATION_SCORE DECIMAL(5,2),
    PHONE_VERIFICATION_SCORE DECIMAL(5,2),
    EMAIL_RISK_SCORE DECIMAL(5,2),
    DEVICE_RISK_SCORE DECIMAL(5,2),
    IP_RISK_SCORE DECIMAL(5,2),
    VELOCITY_CHECK_PASSED BOOLEAN,
    SYNTHETIC_ID_RISK DECIMAL(5,2),
    APPLICATION_FRAUD_SCORE DECIMAL(5,2),
    ACCOUNT_TAKEOVER_RISK DECIMAL(5,2),
    WATCHLIST_MATCH BOOLEAN,
    WATCHLIST_DETAILS STRING,
    ADVERSE_MEDIA_FLAG BOOLEAN,
    OVERALL_FRAUD_RISK STRING,
    RECOMMENDED_ACTION STRING,
    CREATED_TIMESTAMP TIMESTAMP
);
```

### 4. Snowflake Gold Layer - Unified Views

#### Table: `CUSTOMER_360_UNIFIED`
```sql
CREATE OR REPLACE TABLE CUSTOMER_360_UNIFIED AS
SELECT 
    -- Core Identity
    c.CUSTOMER_ID,
    c.NAME_1 AS FULL_NAME,
    c.DATE_OF_BIRTH,
    DATEDIFF('YEAR', c.DATE_OF_BIRTH, CURRENT_DATE()) AS AGE,
    c.GENDER,
    c.NATIONALITY,
    c.RESIDENCE AS RESIDENCE_COUNTRY,
    c.TARGET_MARKET AS CUSTOMER_SEGMENT,
    c.CUSTOMER_SINCE,
    DATEDIFF('MONTH', c.CUSTOMER_SINCE, CURRENT_DATE()) AS RELATIONSHIP_TENURE_MONTHS,
    
    -- KYC & Risk
    c.KYC_STATUS,
    c.RISK_CATEGORY,
    
    -- Financial Summary (from T24)
    COALESCE(acct_summary.TOTAL_DEPOSITS, 0) AS TOTAL_DEPOSITS,
    COALESCE(loan_summary.TOTAL_LOANS_OUTSTANDING, 0) AS TOTAL_LOANS_OUTSTANDING,
    COALESCE(loan_summary.TOTAL_CREDIT_LIMIT, 0) AS TOTAL_CREDIT_LIMIT,
    COALESCE(acct_summary.PRODUCT_COUNT, 0) AS ACTIVE_PRODUCTS_COUNT,
    COALESCE(loan_summary.CURRENT_DPD, 0) AS CURRENT_DPD,
    COALESCE(loan_summary.MAX_DPD_12M, 0) AS MAX_DPD_12M,
    COALESCE(loan_summary.ONTIME_PAYMENT_PCT, 100) AS LOAN_PAYMENT_ONTIME_PCT,
    
    -- Transaction Behavior (from T24)
    COALESCE(txn_summary.TXN_COUNT_12M, 0) AS TOTAL_TRANSACTIONS_12M,
    COALESCE(txn_summary.AVG_MONTHLY_CREDITS, 0) AS AVG_MONTHLY_CREDITS,
    COALESCE(txn_summary.AVG_MONTHLY_DEBITS, 0) AS AVG_MONTHLY_DEBITS,
    
    -- Digital Banking (from MySQL)
    CASE WHEN dig.DIGITAL_ID IS NOT NULL THEN TRUE ELSE FALSE END AS DIGITAL_ENROLLED,
    CASE WHEN dig.LAST_LOGIN >= DATEADD('DAY', -30, CURRENT_DATE()) THEN TRUE ELSE FALSE END AS DIGITAL_ACTIVE_30D,
    dig.PRIMARY_DEVICE_TYPE AS PREFERRED_CHANNEL,
    COALESCE(dig_activity.SESSIONS_30D, 0) AS MOBILE_APP_SESSIONS_30D,
    CASE WHEN dig.EKYC_STATUS = 'VERIFIED' THEN TRUE ELSE FALSE END AS EKYC_COMPLETED,
    
    -- Credit Bureau (from Databricks)
    cbr.CREDIT_SCORE,
    cbr.CREDIT_UTILIZATION,
    
    -- Income Verification (from Databricks)
    iv.DEBT_TO_INCOME_RATIO,
    iv.ANNUAL_INCOME AS VERIFIED_ANNUAL_INCOME,
    iv.EMPLOYMENT_STATUS,
    iv.YEARS_AT_EMPLOYER,
    
    -- Alternative Data (from Databricks)
    ad.PROPERTY_OWNERSHIP,
    
    -- Fraud Assessment (from Databricks)
    fi.OVERALL_FRAUD_RISK AS FRAUD_RISK_LEVEL,
    
    -- Calculated Risk Score
    CASE 
        WHEN cbr.CREDIT_SCORE < 550 THEN 80
        WHEN cbr.CREDIT_SCORE < 650 THEN 60
        WHEN cbr.CREDIT_SCORE < 700 THEN 40
        WHEN cbr.CREDIT_SCORE < 750 THEN 25
        ELSE 15
    END +
    CASE 
        WHEN loan_summary.MAX_DPD_12M > 90 THEN 15
        WHEN loan_summary.MAX_DPD_12M > 30 THEN 8
        ELSE 0
    END +
    CASE
        WHEN fi.OVERALL_FRAUD_RISK = 'CRITICAL' THEN 10
        WHEN fi.OVERALL_FRAUD_RISK = 'HIGH' THEN 5
        ELSE 0
    END AS OVERALL_RISK_SCORE,
    
    CURRENT_TIMESTAMP() AS LAST_UPDATED

FROM RAW_ZONE.ORACLE_T24_SRC.T24_CUSTOMER c

-- Account summary
LEFT JOIN (
    SELECT 
        CUSTOMER_ID,
        SUM(CASE WHEN ACCOUNT_STATUS = 'ACTIVE' THEN WORKING_BALANCE ELSE 0 END) AS TOTAL_DEPOSITS,
        COUNT(*) AS PRODUCT_COUNT
    FROM RAW_ZONE.ORACLE_T24_SRC.T24_ACCOUNT
    WHERE ACCOUNT_STATUS = 'ACTIVE'
    GROUP BY CUSTOMER_ID
) acct_summary ON c.CUSTOMER_ID = acct_summary.CUSTOMER_ID

-- Loan summary
LEFT JOIN (
    SELECT 
        CUSTOMER_ID,
        SUM(OUTSTANDING_PRINCIPAL) AS TOTAL_LOANS_OUTSTANDING,
        SUM(AVAILABLE_LIMIT) AS TOTAL_CREDIT_LIMIT,
        MAX(DAYS_PAST_DUE) AS CURRENT_DPD,
        MAX(CASE WHEN MODIFIED_DATE >= DATEADD('MONTH', -12, CURRENT_DATE()) 
            THEN DAYS_PAST_DUE ELSE 0 END) AS MAX_DPD_12M,
        AVG(CASE WHEN PAYMENTS_MADE > 0 
            THEN (PAYMENTS_MADE * 100.0 / (PAYMENTS_MADE + PAYMENTS_REMAINING)) 
            ELSE 100 END) AS ONTIME_PAYMENT_PCT
    FROM RAW_ZONE.ORACLE_T24_SRC.T24_LOAN
    WHERE LOAN_STATUS NOT IN ('CLOSED', 'WRITTEN_OFF')
    GROUP BY CUSTOMER_ID
) loan_summary ON c.CUSTOMER_ID = loan_summary.CUSTOMER_ID

-- Transaction summary
LEFT JOIN (
    SELECT 
        CUSTOMER_ID,
        COUNT(*) AS TXN_COUNT_12M,
        AVG(CASE WHEN TRANSACTION_TYPE = 'CREDIT' THEN AMOUNT_LCY ELSE 0 END) AS AVG_MONTHLY_CREDITS,
        AVG(CASE WHEN TRANSACTION_TYPE = 'DEBIT' THEN AMOUNT_LCY ELSE 0 END) AS AVG_MONTHLY_DEBITS
    FROM RAW_ZONE.ORACLE_T24_SRC.T24_TRANSACTION
    WHERE VALUE_DATE >= DATEADD('MONTH', -12, CURRENT_DATE())
    GROUP BY CUSTOMER_ID
) txn_summary ON c.CUSTOMER_ID = txn_summary.CUSTOMER_ID

-- Digital profile
LEFT JOIN RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE dig
    ON c.CUSTOMER_ID = dig.CUSTOMER_ID

-- Digital activity
LEFT JOIN (
    SELECT 
        CUSTOMER_ID,
        COUNT(*) AS SESSIONS_30D
    FROM RAW_ZONE.MYSQL_SRC.DIGITAL_SESSION
    WHERE SESSION_START >= DATEADD('DAY', -30, CURRENT_DATE())
    GROUP BY CUSTOMER_ID
) dig_activity ON c.CUSTOMER_ID = dig_activity.CUSTOMER_ID

-- Credit bureau (from Databricks via Polaris)
LEFT JOIN RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT cbr
    ON c.CUSTOMER_ID = cbr.CUSTOMER_ID
    AND cbr.REPORT_DATE = (SELECT MAX(REPORT_DATE) 
                           FROM RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT 
                           WHERE CUSTOMER_ID = c.CUSTOMER_ID)

-- Income verification (from Databricks via Polaris)
LEFT JOIN RAW_ZONE.DATABRICKS_SRC.INCOME_VERIFICATION iv
    ON c.CUSTOMER_ID = iv.CUSTOMER_ID
    AND iv.VERIFICATION_DATE = (SELECT MAX(VERIFICATION_DATE) 
                                FROM RAW_ZONE.DATABRICKS_SRC.INCOME_VERIFICATION 
                                WHERE CUSTOMER_ID = c.CUSTOMER_ID)

-- Alternative data (from Databricks via Polaris)
LEFT JOIN RAW_ZONE.DATABRICKS_SRC.ALTERNATIVE_DATA ad
    ON c.CUSTOMER_ID = ad.CUSTOMER_ID

-- Fraud indicators (from Databricks via Polaris)
LEFT JOIN RAW_ZONE.DATABRICKS_SRC.FRAUD_INDICATORS fi
    ON c.CUSTOMER_ID = fi.CUSTOMER_ID
    AND fi.ASSESSMENT_DATE = (SELECT MAX(ASSESSMENT_DATE) 
                              FROM RAW_ZONE.DATABRICKS_SRC.FRAUD_INDICATORS 
                              WHERE CUSTOMER_ID = c.CUSTOMER_ID);
```

### 5. ML Feature Store

#### Table: `CREDIT_SCORING_FEATURES`
```sql
CREATE OR REPLACE TABLE CREDIT_SCORING_FEATURES (
    CUSTOMER_ID VARCHAR(20) PRIMARY KEY,
    FEATURE_DATE DATE,
    
    -- Demographics
    F_AGE INTEGER,
    F_GENDER_ENCODED INTEGER,
    F_MARITAL_STATUS_ENCODED INTEGER,
    F_RESIDENTIAL_STABILITY FLOAT,
    F_PROPERTY_OWNER INTEGER,
    
    -- Employment & Income
    F_EMPLOYMENT_STATUS_ENCODED INTEGER,
    F_YEARS_EMPLOYED FLOAT,
    F_ANNUAL_INCOME FLOAT,
    F_DEBT_TO_INCOME FLOAT,
    F_INCOME_STABILITY_SCORE FLOAT,
    
    -- Credit Bureau
    F_CREDIT_SCORE INTEGER,
    F_CREDIT_UTILIZATION FLOAT,
    F_TOTAL_CREDIT_ACCOUNTS INTEGER,
    F_OPEN_CREDIT_ACCOUNTS INTEGER,
    F_DELINQUENT_ACCOUNTS INTEGER,
    F_HARD_INQUIRIES_12M INTEGER,
    F_OLDEST_ACCOUNT_MONTHS INTEGER,
    F_PAYMENT_HISTORY_PCT FLOAT,
    F_WORST_DELINQUENCY_ENCODED INTEGER,
    F_MONTHS_SINCE_DELINQUENCY INTEGER,
    
    -- Banking Relationship
    F_RELATIONSHIP_MONTHS INTEGER,
    F_TOTAL_PRODUCTS INTEGER,
    F_HAS_SAVINGS INTEGER,
    F_HAS_LOAN INTEGER,
    F_CURRENT_LOAN_DPD INTEGER,
    F_MAX_DPD_12M INTEGER,
    F_LOAN_PAYMENT_PCT FLOAT,
    F_AVG_BALANCE_3M FLOAT,
    F_BALANCE_TREND FLOAT,
    
    -- Transaction Behavior
    F_TXN_COUNT_3M INTEGER,
    F_AVG_TXN_AMOUNT FLOAT,
    F_CREDIT_TXN_RATIO FLOAT,
    F_SALARY_REGULARITY FLOAT,
    F_EXPENSE_VOLATILITY FLOAT,
    
    -- Digital Behavior
    F_DIGITAL_ACTIVE INTEGER,
    F_APP_SESSIONS_30D INTEGER,
    F_LOGIN_FREQUENCY FLOAT,
    F_DIGITAL_TXN_PCT FLOAT,
    
    -- Alternative Data
    F_RENT_PAYMENT_ENCODED INTEGER,
    F_UTILITY_PAYMENT_ENCODED INTEGER,
    F_EDUCATION_ENCODED INTEGER,
    
    -- Fraud Risk
    F_FRAUD_RISK_SCORE FLOAT,
    F_IDENTITY_VERIFICATION FLOAT,
    
    -- Target Variable
    TARGET_DEFAULT_90D INTEGER,
    TARGET_CREDIT_SCORE_BAND INTEGER
);
```

---

## External Data Source Setup

### 1. Oracle Database (T24 Core Banking)

**Deployment**: Oracle XE 21c in Docker

```bash
# Docker run command
docker run -d \
  --name oracle-t24 \
  -p 1521:1521 \
  -e ORACLE_PASSWORD=T24Demo2024! \
  -e APP_USER=t24user \
  -e APP_USER_PASSWORD=T24UserPass! \
  -v oracle-data:/opt/oracle/oradata \
  gvenzl/oracle-xe:21-slim
```

**Schema Creation**: See data model section for T24 table DDL

**Sample Data**: Generate 100K customers with realistic distributions

### 2. MySQL Database (Digital Banking)

**Deployment**: MySQL 8.0 in Docker

```bash
docker run -d \
  --name mysql-digital \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=DigitalDemo2024! \
  -e MYSQL_DATABASE=digital_banking \
  -e MYSQL_USER=digitaluser \
  -e MYSQL_PASSWORD=DigitalPass! \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0
```

### 3. Databricks (Customer 360 - Apache Iceberg)

**Setup**: Create Iceberg tables in Databricks workspace

```python
# Databricks notebook to create Iceberg tables

from pyspark.sql.types import *
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Credit Bureau Iceberg Tables") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.spark_catalog.type", "hive") \
    .getOrCreate()

# Create database
spark.sql("CREATE DATABASE IF NOT EXISTS credit_bureau")

# Create Iceberg table for credit bureau reports
spark.sql("""
    CREATE TABLE IF NOT EXISTS credit_bureau.credit_bureau_report
    USING ICEBERG
    LOCATION 's3://your-bucket/iceberg/credit_bureau_report'
    AS SELECT * FROM credit_bureau_staging.credit_bureau_report
""")
```

---

## Snowflake Core Implementation

### 1. Database and Schema Creation

```sql
-- ============================================
-- DATABASE SETUP
-- ============================================

CREATE OR REPLACE DATABASE CREDIT_DECISIONING_DB
  DATA_RETENTION_TIME_IN_DAYS = 90
  COMMENT = 'Financial Services Credit Decisioning Demo';

USE DATABASE CREDIT_DECISIONING_DB;

-- ============================================
-- BRONZE LAYER - Raw data ingestion
-- ============================================

CREATE SCHEMA RAW_ZONE COMMENT = 'Bronze layer - raw ingested data';
CREATE SCHEMA RAW_ZONE.DATABRICKS_SRC COMMENT = 'Databricks Polaris Iceberg tables';
CREATE SCHEMA RAW_ZONE.MYSQL_SRC COMMENT = 'MySQL Openflow CDC streams';
CREATE SCHEMA RAW_ZONE.ORACLE_T24_SRC COMMENT = 'Oracle T24 Openflow CDC streams';

-- ============================================
-- SILVER LAYER - Cleaned and validated data
-- ============================================

CREATE SCHEMA CURATED_ZONE COMMENT = 'Silver layer - cleaned, validated data';
CREATE SCHEMA CURATED_ZONE.CUSTOMER COMMENT = 'Customer entities';
CREATE SCHEMA CURATED_ZONE.ACCOUNTS COMMENT = 'Account entities';
CREATE SCHEMA CURATED_ZONE.LOANS COMMENT = 'Loan entities';
CREATE SCHEMA CURATED_ZONE.TRANSACTIONS COMMENT = 'Transaction entities';
CREATE SCHEMA CURATED_ZONE.DIGITAL COMMENT = 'Digital banking entities';
CREATE SCHEMA CURATED_ZONE.T24_MIGRATED COMMENT = 'SnowConverted T24 procedures';

-- ============================================
-- GOLD LAYER - Analytics and aggregations
-- ============================================

CREATE SCHEMA ANALYTICS_ZONE COMMENT = 'Gold layer - unified analytics';
CREATE SCHEMA ANALYTICS_ZONE.CUSTOMER_360 COMMENT = 'Unified customer views';
CREATE SCHEMA ANALYTICS_ZONE.FEATURE_STORE COMMENT = 'ML feature engineering';
CREATE SCHEMA ANALYTICS_ZONE.METRICS COMMENT = 'Business KPIs and metrics';

-- ============================================
-- ML ZONE - Machine learning assets
-- ============================================

CREATE SCHEMA ML_ZONE COMMENT = 'Machine learning assets';
CREATE SCHEMA ML_ZONE.TRAINING COMMENT = 'Training datasets';
CREATE SCHEMA ML_ZONE.MODELS COMMENT = 'Model registry';
CREATE SCHEMA ML_ZONE.INFERENCE COMMENT = 'Prediction outputs';

-- ============================================
-- APPLICATION ZONE - App layer
-- ============================================

CREATE SCHEMA APP_ZONE COMMENT = 'Application layer';
CREATE SCHEMA APP_ZONE.STREAMLIT COMMENT = 'Streamlit app objects';
CREATE SCHEMA APP_ZONE.CORTEX COMMENT = 'Cortex AI objects';
CREATE SCHEMA APP_ZONE.TRANSACTIONAL COMMENT = 'Hybrid Tables for OLTP';
CREATE SCHEMA APP_ZONE.INTELLIGENCE COMMENT = 'Snowflake Intelligence configs';

-- ============================================
-- GOVERNANCE ZONE
-- ============================================

CREATE SCHEMA GOVERNANCE COMMENT = 'Governance and audit';
CREATE SCHEMA GOVERNANCE.TAGS COMMENT = 'Data classification tags';
CREATE SCHEMA GOVERNANCE.POLICIES COMMENT = 'Security policies';
CREATE SCHEMA GOVERNANCE.AUDIT COMMENT = 'Audit logging';
CREATE SCHEMA GOVERNANCE.MIGRATION COMMENT = 'SnowConvert tracking';
```

### 2. Warehouses

```sql
-- ============================================
-- VIRTUAL WAREHOUSES
-- ============================================

-- ETL warehouse for data processing
CREATE OR REPLACE WAREHOUSE ETL_WH WITH
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 3
  SCALING_POLICY = 'STANDARD'
  COMMENT = 'Data pipeline processing';

-- ML warehouse with Snowpark optimization
CREATE OR REPLACE WAREHOUSE ML_WH WITH
  WAREHOUSE_SIZE = 'LARGE'
  WAREHOUSE_TYPE = 'SNOWPARK-OPTIMIZED'
  AUTO_SUSPEND = 600
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 2
  COMMENT = 'ML training and inference';

-- Streamlit app warehouse
CREATE OR REPLACE WAREHOUSE APP_WH WITH
  WAREHOUSE_SIZE = 'SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 5
  SCALING_POLICY = 'STANDARD'
  COMMENT = 'Streamlit application';

-- OLTP warehouse for Hybrid Tables
CREATE OR REPLACE WAREHOUSE TRANSACTIONAL_WH WITH
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 3
  COMMENT = 'Hybrid table transactional workloads';
```

### 3. Roles and Permissions

```sql
-- ============================================
-- ROLE-BASED ACCESS CONTROL
-- ============================================

-- Create custom roles
CREATE ROLE IF NOT EXISTS CREDIT_OFFICER;
CREATE ROLE IF NOT EXISTS RISK_MANAGER;
CREATE ROLE IF NOT EXISTS COMPLIANCE_OFFICER;
CREATE ROLE IF NOT EXISTS BRANCH_MANAGER;
CREATE ROLE IF NOT EXISTS DATA_ENGINEER;
CREATE ROLE IF NOT EXISTS ML_ENGINEER;

-- Grant database access
GRANT USAGE ON DATABASE CREDIT_DECISIONING_DB TO ROLE CREDIT_OFFICER;
GRANT USAGE ON DATABASE CREDIT_DECISIONING_DB TO ROLE RISK_MANAGER;
GRANT USAGE ON DATABASE CREDIT_DECISIONING_DB TO ROLE COMPLIANCE_OFFICER;
GRANT USAGE ON DATABASE CREDIT_DECISIONING_DB TO ROLE BRANCH_MANAGER;

-- Grant warehouse access
GRANT USAGE ON WAREHOUSE APP_WH TO ROLE CREDIT_OFFICER;
GRANT USAGE ON WAREHOUSE APP_WH TO ROLE RISK_MANAGER;
GRANT USAGE ON WAREHOUSE APP_WH TO ROLE COMPLIANCE_OFFICER;
GRANT USAGE ON WAREHOUSE APP_WH TO ROLE BRANCH_MANAGER;
GRANT USAGE ON WAREHOUSE TRANSACTIONAL_WH TO ROLE CREDIT_OFFICER;

-- Grant schema and table access
GRANT USAGE ON SCHEMA ANALYTICS_ZONE.CUSTOMER_360 TO ROLE CREDIT_OFFICER;
GRANT SELECT ON ALL TABLES IN SCHEMA ANALYTICS_ZONE.CUSTOMER_360 TO ROLE CREDIT_OFFICER;
GRANT USAGE ON SCHEMA APP_ZONE.TRANSACTIONAL TO ROLE CREDIT_OFFICER;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA APP_ZONE.TRANSACTIONAL TO ROLE CREDIT_OFFICER;

-- Grant full access to Risk Manager
GRANT USAGE ON ALL SCHEMAS IN DATABASE CREDIT_DECISIONING_DB TO ROLE RISK_MANAGER;
GRANT SELECT ON ALL TABLES IN DATABASE CREDIT_DECISIONING_DB TO ROLE RISK_MANAGER;
GRANT SELECT ON ALL VIEWS IN DATABASE CREDIT_DECISIONING_DB TO ROLE RISK_MANAGER;

-- Grant audit access to Compliance Officer
GRANT USAGE ON SCHEMA GOVERNANCE.AUDIT TO ROLE COMPLIANCE_OFFICER;
GRANT SELECT ON ALL TABLES IN SCHEMA GOVERNANCE.AUDIT TO ROLE COMPLIANCE_OFFICER;
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE COMPLIANCE_OFFICER; -- For ACCESS_HISTORY
```

---

## Feature 1: SnowConvert AI Migration

### Purpose
Migrate T24 PL/SQL stored procedures to Snowflake SQL/Snowpark using AI-powered code conversion.

### Implementation

```sql
-- ============================================
-- SNOWCONVERT AI MIGRATION TRACKING
-- ============================================

-- Create migration tracking table
CREATE OR REPLACE TABLE GOVERNANCE.MIGRATION.SNOWCONVERT_LOG (
    MIGRATION_ID VARCHAR(36) DEFAULT UUID_STRING(),
    SOURCE_SYSTEM VARCHAR(50),
    SOURCE_OBJECT_TYPE VARCHAR(50),
    SOURCE_OBJECT_NAME VARCHAR(200),
    SOURCE_CODE TEXT,
    TARGET_OBJECT_NAME VARCHAR(200),
    TARGET_CODE TEXT,
    CONVERSION_STATUS VARCHAR(20),
    CONVERSION_WARNINGS VARIANT,
    MANUAL_REVIEW_NEEDED BOOLEAN,
    MANUAL_EDITS_MADE TEXT,
    CONVERSION_METHOD VARCHAR(50) DEFAULT 'SNOWCONVERT_AI',
    CONVERTED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CONVERTED_BY VARCHAR(100),
    TESTED_AT TIMESTAMP_NTZ,
    TEST_RESULTS VARIANT,
    DEPLOYED_AT TIMESTAMP_NTZ,
    PRIMARY KEY (MIGRATION_ID)
);

-- Example T24 PL/SQL Procedure (Original Oracle code)
/*
CREATE OR REPLACE PROCEDURE T24_GET_CUSTOMER_RISK(
    p_customer_id IN VARCHAR2,
    p_risk_score OUT NUMBER,
    p_risk_category OUT VARCHAR2
) AS
    v_total_exposure NUMBER;
    v_payment_history NUMBER;
    v_days_past_due NUMBER;
BEGIN
    SELECT NVL(SUM(OUTSTANDING_PRINCIPAL), 0)
    INTO v_total_exposure
    FROM T24_LOAN
    WHERE CUSTOMER_ID = p_customer_id
    AND LOAN_STATUS NOT IN ('CLOSED', 'WRITTEN_OFF');
    
    SELECT NVL(AVG(CASE WHEN PAYMENT_STATUS = 'PAID' THEN 100 
                       WHEN PAYMENT_STATUS = 'PARTIAL' THEN 50 
                       ELSE 0 END), 0)
    INTO v_payment_history
    FROM T24_PAYMENT_SCHEDULE
    WHERE CUSTOMER_ID = p_customer_id
    AND DUE_DATE <= SYSDATE;
    
    SELECT NVL(MAX(DAYS_PAST_DUE), 0)
    INTO v_days_past_due
    FROM T24_LOAN
    WHERE CUSTOMER_ID = p_customer_id;
    
    p_risk_score := LEAST(100, GREATEST(0,
        (v_total_exposure / 100000) * 20 +
        (100 - v_payment_history) * 0.5 +
        CASE WHEN v_days_past_due > 90 THEN 40
             WHEN v_days_past_due > 60 THEN 30
             WHEN v_days_past_due > 30 THEN 20
             WHEN v_days_past_due > 0 THEN 10
             ELSE 0 END
    ));
    
    p_risk_category := CASE 
        WHEN p_risk_score >= 70 THEN 'HIGH'
        WHEN p_risk_score >= 40 THEN 'MEDIUM'
        ELSE 'LOW'
    END;
END;
*/

-- Converted Snowflake Stored Procedure (output from SnowConvert AI)
CREATE OR REPLACE PROCEDURE CURATED_ZONE.T24_MIGRATED.GET_CUSTOMER_RISK(
    P_CUSTOMER_ID VARCHAR
)
RETURNS TABLE (RISK_SCORE FLOAT, RISK_CATEGORY VARCHAR)
LANGUAGE SQL
COMMENT = 'Migrated from T24 PL/SQL via SnowConvert AI'
AS
$$
DECLARE
    v_total_exposure FLOAT DEFAULT 0;
    v_payment_history FLOAT DEFAULT 0;
    v_days_past_due INT DEFAULT 0;
    v_risk_score FLOAT;
    v_risk_category VARCHAR;
BEGIN
    -- Calculate total exposure
    SELECT COALESCE(SUM(OUTSTANDING_PRINCIPAL), 0)
    INTO :v_total_exposure
    FROM CURATED_ZONE.LOANS.FACT_LOANS
    WHERE CUSTOMER_ID = :P_CUSTOMER_ID
    AND LOAN_STATUS NOT IN ('CLOSED', 'WRITTEN_OFF');
    
    -- Get payment history percentage
    SELECT COALESCE(AVG(CASE WHEN PAYMENT_STATUS = 'PAID' THEN 100 
                            WHEN PAYMENT_STATUS = 'PARTIAL' THEN 50 
                            ELSE 0 END), 0)
    INTO :v_payment_history
    FROM CURATED_ZONE.LOANS.FACT_PAYMENT_SCHEDULE
    WHERE CUSTOMER_ID = :P_CUSTOMER_ID
    AND DUE_DATE <= CURRENT_DATE();
    
    -- Get worst days past due
    SELECT COALESCE(MAX(DAYS_PAST_DUE), 0)
    INTO :v_days_past_due
    FROM CURATED_ZONE.LOANS.FACT_LOANS
    WHERE CUSTOMER_ID = :P_CUSTOMER_ID;
    
    -- Calculate risk score (0-100, higher = riskier)
    v_risk_score := LEAST(100, GREATEST(0,
        (:v_total_exposure / 100000) * 20 +
        (100 - :v_payment_history) * 0.5 +
        CASE WHEN :v_days_past_due > 90 THEN 40
             WHEN :v_days_past_due > 60 THEN 30
             WHEN :v_days_past_due > 30 THEN 20
             WHEN :v_days_past_due > 0 THEN 10
             ELSE 0 END
    ));
    
    -- Categorize risk
    v_risk_category := CASE 
        WHEN :v_risk_score >= 70 THEN 'HIGH'
        WHEN :v_risk_score >= 40 THEN 'MEDIUM'
        ELSE 'LOW'
    END;
    
    RETURN TABLE(SELECT :v_risk_score AS RISK_SCORE, :v_risk_category AS RISK_CATEGORY);
END;
$$;

-- Log the migration
INSERT INTO GOVERNANCE.MIGRATION.SNOWCONVERT_LOG 
(SOURCE_SYSTEM, SOURCE_OBJECT_TYPE, SOURCE_OBJECT_NAME, TARGET_OBJECT_NAME, 
 CONVERSION_STATUS, MANUAL_REVIEW_NEEDED, CONVERTED_BY)
VALUES 
('T24_ORACLE', 'PROCEDURE', 'T24_GET_CUSTOMER_RISK', 
 'CURATED_ZONE.T24_MIGRATED.GET_CUSTOMER_RISK', 'SUCCESS', FALSE, 'SNOWCONVERT_AI');

-- Test the converted procedure
CALL CURATED_ZONE.T24_MIGRATED.GET_CUSTOMER_RISK('CUS-000001');
```

---

## Feature 2: Unistore & Hybrid Tables

### Purpose
Use Hybrid Tables for high-throughput, low-latency transactional workloads (credit application processing).

### Implementation

```sql
-- ============================================
-- HYBRID TABLES FOR TRANSACTIONAL WORKLOADS
-- ============================================

-- Credit Applications - High-volume OLTP workload
CREATE OR REPLACE HYBRID TABLE APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS (
    APPLICATION_ID VARCHAR(36) DEFAULT UUID_STRING() PRIMARY KEY,
    CUSTOMER_ID VARCHAR(20) NOT NULL,
    APPLICATION_TYPE VARCHAR(30) NOT NULL,
    PRODUCT_CODE VARCHAR(20) NOT NULL,
    REQUESTED_AMOUNT NUMBER(18,2) NOT NULL,
    REQUESTED_TERM_MONTHS INTEGER,
    PURPOSE VARCHAR(200),
    
    -- Application State
    STATUS VARCHAR(30) DEFAULT 'SUBMITTED',
    CURRENT_STAGE VARCHAR(50) DEFAULT 'INTAKE',
    ASSIGNED_OFFICER VARCHAR(50),
    PRIORITY VARCHAR(20) DEFAULT 'NORMAL',
    
    -- Timestamps
    SUBMITTED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    LAST_UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    DECISION_DUE_BY TIMESTAMP_NTZ,
    
    -- Locking for concurrent access
    LOCKED_BY VARCHAR(50),
    LOCKED_AT TIMESTAMP_NTZ,
    
    -- Indexes for fast lookups
    INDEX IDX_CUSTOMER (CUSTOMER_ID),
    INDEX IDX_STATUS (STATUS),
    INDEX IDX_OFFICER (ASSIGNED_OFFICER),
    INDEX IDX_SUBMITTED (SUBMITTED_AT)
);

-- Credit Decisions - Records every decision with audit trail
CREATE OR REPLACE HYBRID TABLE APP_ZONE.TRANSACTIONAL.CREDIT_DECISIONS (
    DECISION_ID VARCHAR(36) DEFAULT UUID_STRING() PRIMARY KEY,
    APPLICATION_ID VARCHAR(36) NOT NULL,
    CUSTOMER_ID VARCHAR(20) NOT NULL,
    
    -- ML Model Output
    ML_SCORE_BAND INTEGER,
    ML_CREDIT_RATING VARCHAR(5),
    ML_RECOMMENDED_DECISION VARCHAR(20),
    ML_MAX_CREDIT_LIMIT NUMBER(18,2),
    ML_MODEL_VERSION VARCHAR(20),
    ML_INFERENCE_TIMESTAMP TIMESTAMP_NTZ,
    
    -- Agent Reasoning
    AGENT_SESSION_ID VARCHAR(36),
    AGENT_ANALYSIS VARIANT,
    AGENT_POLICY_CHECKS VARIANT,
    AGENT_RISK_FACTORS VARIANT,
    AGENT_RECOMMENDATION VARCHAR(20),
    
    -- Final Decision
    FINAL_DECISION VARCHAR(20) NOT NULL,
    APPROVED_AMOUNT NUMBER(18,2),
    APPROVED_TERM_MONTHS INTEGER,
    INTEREST_RATE NUMBER(8,4),
    CONDITIONS VARIANT,
    DECLINE_REASONS VARIANT,
    
    -- Decision Metadata
    DECISION_TYPE VARCHAR(20),
    DECIDED_BY VARCHAR(100),
    DECISION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Compliance
    FOUR_EYES_REQUIRED BOOLEAN DEFAULT FALSE,
    FOUR_EYES_APPROVED_BY VARCHAR(50),
    FOUR_EYES_TIMESTAMP TIMESTAMP_NTZ,
    
    -- Foreign Key
    FOREIGN KEY (APPLICATION_ID) REFERENCES APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS(APPLICATION_ID),
    
    INDEX IDX_APP (APPLICATION_ID),
    INDEX IDX_CUSTOMER_DEC (CUSTOMER_ID),
    INDEX IDX_DECISION_TIME (DECISION_TIMESTAMP)
);

-- Agent Conversation Sessions
CREATE OR REPLACE HYBRID TABLE APP_ZONE.TRANSACTIONAL.AGENT_SESSIONS (
    SESSION_ID VARCHAR(36) DEFAULT UUID_STRING() PRIMARY KEY,
    APPLICATION_ID VARCHAR(36),
    CUSTOMER_ID VARCHAR(20),
    USER_ID VARCHAR(50) NOT NULL,
    USER_ROLE VARCHAR(50),
    
    -- Session State
    SESSION_STATUS VARCHAR(20) DEFAULT 'ACTIVE',
    STARTED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    LAST_ACTIVITY_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    ENDED_AT TIMESTAMP_NTZ,
    
    -- Conversation
    MESSAGE_COUNT INTEGER DEFAULT 0,
    MESSAGES VARIANT,
    
    -- Context
    POLICIES_REFERENCED VARIANT,
    DATA_ACCESSED VARIANT,
    TOOLS_USED VARIANT,
    
    -- Outcome
    DECISION_MADE BOOLEAN DEFAULT FALSE,
    DECISION_ID VARCHAR(36),
    
    INDEX IDX_APP_SESSION (APPLICATION_ID),
    INDEX IDX_USER_SESSION (USER_ID),
    INDEX IDX_STATUS_SESSION (SESSION_STATUS)
);

-- Transactional Stored Procedures

-- Submit new application
CREATE OR REPLACE PROCEDURE APP_ZONE.TRANSACTIONAL.SUBMIT_APPLICATION(
    P_CUSTOMER_ID VARCHAR,
    P_APPLICATION_TYPE VARCHAR,
    P_PRODUCT_CODE VARCHAR,
    P_REQUESTED_AMOUNT FLOAT,
    P_REQUESTED_TERM INTEGER,
    P_PURPOSE VARCHAR
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    v_app_id VARCHAR;
    v_sla_hours INTEGER DEFAULT 24;
BEGIN
    v_app_id := UUID_STRING();
    
    -- Set SLA based on amount
    IF (P_REQUESTED_AMOUNT > 500000) THEN
        v_sla_hours := 72;
    ELSEIF (P_REQUESTED_AMOUNT > 100000) THEN
        v_sla_hours := 48;
    END IF;
    
    -- Insert application (fast OLTP write)
    INSERT INTO APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS (
        APPLICATION_ID, CUSTOMER_ID, APPLICATION_TYPE, PRODUCT_CODE,
        REQUESTED_AMOUNT, REQUESTED_TERM_MONTHS, PURPOSE,
        DECISION_DUE_BY, PRIORITY
    ) VALUES (
        :v_app_id, :P_CUSTOMER_ID, :P_APPLICATION_TYPE, :P_PRODUCT_CODE,
        :P_REQUESTED_AMOUNT, :P_REQUESTED_TERM, :P_PURPOSE,
        DATEADD('HOUR', :v_sla_hours, CURRENT_TIMESTAMP()),
        CASE WHEN :P_REQUESTED_AMOUNT > 500000 THEN 'HIGH' ELSE 'NORMAL' END
    );
    
    RETURN v_app_id;
END;
$$;

-- Lock application for processing
CREATE OR REPLACE PROCEDURE APP_ZONE.TRANSACTIONAL.LOCK_APPLICATION(
    P_APPLICATION_ID VARCHAR,
    P_OFFICER_ID VARCHAR
)
RETURNS BOOLEAN
LANGUAGE SQL
AS
$$
BEGIN
    UPDATE APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS
    SET LOCKED_BY = :P_OFFICER_ID,
        LOCKED_AT = CURRENT_TIMESTAMP(),
        ASSIGNED_OFFICER = :P_OFFICER_ID,
        LAST_UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE APPLICATION_ID = :P_APPLICATION_ID
    AND (LOCKED_BY IS NULL OR LOCKED_AT < DATEADD('MINUTE', -30, CURRENT_TIMESTAMP()));
    
    RETURN (SQLROWCOUNT > 0);
END;
$$;

-- Record credit decision
CREATE OR REPLACE PROCEDURE APP_ZONE.TRANSACTIONAL.RECORD_DECISION(
    P_APPLICATION_ID VARCHAR,
    P_DECISION VARCHAR,
    P_DECISION_TYPE VARCHAR,
    P_AGENT_OUTPUT VARIANT
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    v_decision_id VARCHAR;
    v_customer_id VARCHAR;
BEGIN
    v_decision_id := UUID_STRING();
    
    -- Get customer ID
    SELECT CUSTOMER_ID INTO :v_customer_id
    FROM APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS
    WHERE APPLICATION_ID = :P_APPLICATION_ID;
    
    -- Insert decision
    INSERT INTO APP_ZONE.TRANSACTIONAL.CREDIT_DECISIONS (
        DECISION_ID, APPLICATION_ID, CUSTOMER_ID,
        ML_SCORE_BAND, ML_CREDIT_RATING, ML_RECOMMENDED_DECISION,
        AGENT_ANALYSIS, AGENT_RECOMMENDATION,
        FINAL_DECISION, DECISION_TYPE, DECIDED_BY
    ) VALUES (
        :v_decision_id, :P_APPLICATION_ID, :v_customer_id,
        P_AGENT_OUTPUT:ml_score_band::INTEGER,
        P_AGENT_OUTPUT:ml_credit_rating::VARCHAR,
        P_AGENT_OUTPUT:final_recommendation::VARCHAR,
        P_AGENT_OUTPUT:agent_analysis,
        P_AGENT_OUTPUT:final_recommendation::VARCHAR,
        :P_DECISION, :P_DECISION_TYPE, CURRENT_USER()
    );
    
    -- Update application status
    UPDATE APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS
    SET STATUS = CASE 
            WHEN :P_DECISION = 'APPROVE' THEN 'APPROVED'
            WHEN :P_DECISION = 'DECLINE' THEN 'DECLINED'
            ELSE 'IN_REVIEW'
        END,
        LAST_UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE APPLICATION_ID = :P_APPLICATION_ID;
    
    RETURN v_decision_id;
END;
$$;

-- Real-time queue view
CREATE OR REPLACE VIEW APP_ZONE.TRANSACTIONAL.V_APPLICATION_QUEUE AS
SELECT 
    a.APPLICATION_ID,
    a.CUSTOMER_ID,
    c.FULL_NAME AS CUSTOMER_NAME,
    a.APPLICATION_TYPE,
    a.PRODUCT_CODE,
    a.REQUESTED_AMOUNT,
    a.STATUS,
    a.CURRENT_STAGE,
    a.PRIORITY,
    a.ASSIGNED_OFFICER,
    a.SUBMITTED_AT,
    a.DECISION_DUE_BY,
    DATEDIFF('HOUR', a.SUBMITTED_AT, CURRENT_TIMESTAMP()) AS HOURS_IN_QUEUE,
    CASE 
        WHEN a.DECISION_DUE_BY < CURRENT_TIMESTAMP() THEN 'OVERDUE'
        WHEN a.DECISION_DUE_BY < DATEADD('HOUR', 4, CURRENT_TIMESTAMP()) THEN 'DUE_SOON'
        ELSE 'ON_TRACK'
    END AS SLA_STATUS,
    c.CREDIT_SCORE,
    c.RISK_CATEGORY
FROM APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS a
JOIN ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED c 
    ON a.CUSTOMER_ID = c.CUSTOMER_ID
WHERE a.STATUS NOT IN ('APPROVED', 'DECLINED', 'CANCELLED')
ORDER BY 
    CASE a.PRIORITY 
        WHEN 'URGENT' THEN 1 
        WHEN 'HIGH' THEN 2 
        WHEN 'NORMAL' THEN 3 
        ELSE 4 
    END,
    a.SUBMITTED_AT;
```

---

## Feature 3: Cortex Search with Policy Documents

### Purpose
Enable RAG (Retrieval-Augmented Generation) for the AI agent to access bank policies.

### Implementation

```sql
-- ============================================
-- CORTEX SEARCH FOR BANK POLICIES
-- ============================================

-- Create stage for policy documents
CREATE OR REPLACE STAGE APP_ZONE.CORTEX.POLICY_DOCUMENTS
  DIRECTORY = (ENABLE = TRUE)
  COMMENT = 'Bank credit policy documents for RAG';

-- Policy documents table
CREATE OR REPLACE TABLE APP_ZONE.CORTEX.CREDIT_POLICIES (
    POLICY_ID VARCHAR(36) DEFAULT UUID_STRING(),
    DOCUMENT_NAME VARCHAR(200),
    DOCUMENT_TYPE VARCHAR(50),
    CATEGORY VARCHAR(100),
    VERSION VARCHAR(20),
    EFFECTIVE_DATE DATE,
    EXPIRY_DATE DATE,
    
    -- Content
    FULL_TEXT TEXT,
    SUMMARY TEXT,
    
    -- Chunking for RAG
    CHUNK_ID INTEGER,
    CHUNK_TEXT TEXT,
    CHUNK_EMBEDDING VECTOR(FLOAT, 1024),
    
    -- Metadata
    DEPARTMENT VARCHAR(100),
    APPROVED_BY VARCHAR(100),
    LAST_REVIEWED DATE,
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample policy documents
INSERT INTO APP_ZONE.CORTEX.CREDIT_POLICIES 
(DOCUMENT_NAME, DOCUMENT_TYPE, CATEGORY, VERSION, EFFECTIVE_DATE, FULL_TEXT, DEPARTMENT)
VALUES
('Credit Scoring Model Usage Policy', 'POLICY', 'CREDIT_SCORING', 'v2.1', '2025-01-01',
$$CREDIT SCORING MODEL USAGE POLICY
Version 2.1 - Effective January 2025

1. PURPOSE
This policy establishes guidelines for using the XGBoost Credit Scoring Model.

2. CREDIT SCORE BANDS AND DECISIONS
Score Band | Rating | Default Decision | Max Credit Limit
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
- Score Bands 5-6: Credit Officers may approve with justification
- Score Bands 3-4: Requires Senior Credit Manager approval
- Score Bands 1-2: Requires Credit Committee approval

4. SPECIAL CONSIDERATIONS
- Existing customers 24+ months good standing: upgrade 1 band
- Government employees: upgrade 1 band for stability
- Self-employed < 2 years: downgrade 1 band unless collateralized$$, 
'Risk Management');

-- Procedure to chunk and embed documents
CREATE OR REPLACE PROCEDURE APP_ZONE.CORTEX.PROCESS_POLICY_DOCUMENTS()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Delete existing chunks
    DELETE FROM APP_ZONE.CORTEX.CREDIT_POLICIES WHERE CHUNK_ID IS NOT NULL;
    
    -- Create chunks and embeddings
    INSERT INTO APP_ZONE.CORTEX.CREDIT_POLICIES 
    (POLICY_ID, DOCUMENT_NAME, DOCUMENT_TYPE, CATEGORY, CHUNK_ID, CHUNK_TEXT, CHUNK_EMBEDDING, IS_ACTIVE)
    SELECT 
        cp.POLICY_ID,
        cp.DOCUMENT_NAME,
        cp.DOCUMENT_TYPE,
        cp.CATEGORY,
        ROW_NUMBER() OVER (PARTITION BY cp.POLICY_ID ORDER BY seq.SEQ) AS CHUNK_ID,
        TRIM(seq.VALUE::VARCHAR) AS CHUNK_TEXT,
        SNOWFLAKE.CORTEX.EMBED_TEXT_1024('snowflake-arctic-embed-l-v2.0', TRIM(seq.VALUE::VARCHAR)) AS CHUNK_EMBEDDING,
        TRUE AS IS_ACTIVE
    FROM APP_ZONE.CORTEX.CREDIT_POLICIES cp,
    LATERAL SPLIT_TO_TABLE(cp.FULL_TEXT, '\n\n') seq
    WHERE cp.CHUNK_ID IS NULL 
    AND cp.FULL_TEXT IS NOT NULL
    AND LENGTH(TRIM(seq.VALUE::VARCHAR)) > 50;
    
    RETURN 'Documents processed and embedded';
END;
$$;

-- Execute document processing
CALL APP_ZONE.CORTEX.PROCESS_POLICY_DOCUMENTS();

-- Create Cortex Search Service
CREATE OR REPLACE CORTEX SEARCH SERVICE APP_ZONE.CORTEX.POLICY_SEARCH_SERVICE
  ON CHUNK_TEXT
  ATTRIBUTES DOCUMENT_NAME, DOCUMENT_TYPE, CATEGORY, EFFECTIVE_DATE
  WAREHOUSE = APP_WH
  TARGET_LAG = '1 hour'
AS (
    SELECT 
        POLICY_ID,
        DOCUMENT_NAME,
        DOCUMENT_TYPE,
        CATEGORY,
        CHUNK_ID,
        CHUNK_TEXT,
        EFFECTIVE_DATE
    FROM APP_ZONE.CORTEX.CREDIT_POLICIES
    WHERE IS_ACTIVE = TRUE
    AND CHUNK_TEXT IS NOT NULL
);

-- Function to search policies
CREATE OR REPLACE FUNCTION APP_ZONE.CORTEX.SEARCH_CREDIT_POLICIES(
    query_text VARCHAR,
    num_results INTEGER DEFAULT 5
)
RETURNS TABLE (
    DOCUMENT_NAME VARCHAR,
    CATEGORY VARCHAR,
    CHUNK_TEXT VARCHAR,
    RELEVANCE_SCORE FLOAT
)
AS
$$
SELECT 
    DOCUMENT_NAME,
    CATEGORY,
    CHUNK_TEXT,
    SCORE AS RELEVANCE_SCORE
FROM TABLE(
    APP_ZONE.CORTEX.POLICY_SEARCH_SERVICE!SEARCH(
        query_text,
        OBJECT_CONSTRUCT('LIMIT', num_results)
    )
)
$$;
```

---

## Feature 4: Cortex Agent - AI Credit Analyst

### Purpose
AI-powered credit analyst that evaluates applications using ML scores, customer data, and bank policies.

### Implementation

```sql
-- ============================================
-- CORTEX AGENT: CREDIT DECISIONING AGENT
-- ============================================

-- Agent configuration
CREATE OR REPLACE TABLE APP_ZONE.CORTEX.AGENT_CONFIG (
    AGENT_ID VARCHAR(50) PRIMARY KEY,
    AGENT_NAME VARCHAR(100),
    AGENT_DESCRIPTION TEXT,
    SYSTEM_PROMPT TEXT,
    AVAILABLE_TOOLS VARIANT,
    MODEL_ID VARCHAR(100),
    TEMPERATURE FLOAT DEFAULT 0.1,
    IS_ACTIVE BOOLEAN DEFAULT TRUE
);

INSERT INTO APP_ZONE.CORTEX.AGENT_CONFIG VALUES (
    'CREDIT_AGENT_V1',
    'Senior Credit Analyst Agent',
    'AI-powered credit analyst that evaluates loan applications',
    $$You are a Senior Credit Analyst at a major bank. Your role is to evaluate credit applications.

RESPONSIBILITIES:
1. Review customer financial profiles and credit history
2. Analyze the ML credit score and interpret what it means
3. Check bank policies to ensure compliance
4. Identify risk factors and mitigating factors
5. Make a recommendation (APPROVE, REFER, or DECLINE)
6. Provide clear justification

DECISION FRAMEWORK:
- Always get customer profile and ML credit score first
- Search relevant policies
- Consider DTI ratio, employment stability, payment history
- Check for delinquency or red flags
- Apply policy rules strictly but consider documented exceptions

OUTPUT FORMAT:
1. Customer Summary
2. ML Score Interpretation
3. Policy Compliance Check
4. Risk Factors
5. Mitigating Factors
6. Final Recommendation with Justification$$,
    PARSE_JSON('[
        "get_customer_profile",
        "get_ml_credit_score",
        "search_policies",
        "calculate_dti",
        "check_delinquency_history"
    ]'),
    'claude-3-5-sonnet',
    0.1,
    TRUE
);

-- Agent Tools

-- Tool 1: Get Customer Profile
CREATE OR REPLACE FUNCTION APP_ZONE.CORTEX.TOOL_GET_CUSTOMER_PROFILE(customer_id VARCHAR)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
SELECT OBJECT_CONSTRUCT(
    'customer_id', CUSTOMER_ID,
    'full_name', FULL_NAME,
    'age', AGE,
    'employment_status', EMPLOYMENT_STATUS,
    'verified_annual_income', VERIFIED_ANNUAL_INCOME,
    'risk_category', RISK_CATEGORY,
    'total_deposits', TOTAL_DEPOSITS,
    'total_loans_outstanding', TOTAL_LOANS_OUTSTANDING,
    'fraud_risk_level', FRAUD_RISK_LEVEL
)
FROM ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED
WHERE CUSTOMER_ID = customer_id
$$;

-- Tool 2: Get ML Credit Score
CREATE OR REPLACE FUNCTION APP_ZONE.CORTEX.TOOL_GET_ML_CREDIT_SCORE(customer_id VARCHAR)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
WITH features AS (
    SELECT * FROM ANALYTICS_ZONE.FEATURE_STORE.CREDIT_SCORING_FEATURES
    WHERE CUSTOMER_ID = customer_id
    LIMIT 1
),
prediction AS (
    SELECT ML_ZONE.INFERENCE.PREDICT_CREDIT_SCORE(
        F_AGE, F_YEARS_EMPLOYED, F_ANNUAL_INCOME, F_DEBT_TO_INCOME,
        F_CREDIT_SCORE, F_CREDIT_UTILIZATION, F_RELATIONSHIP_MONTHS,
        F_AVG_BALANCE_3M, F_TXN_COUNT_3M, F_FRAUD_RISK_SCORE,
        F_GENDER_ENCODED, F_MARITAL_STATUS_ENCODED,
        F_EMPLOYMENT_STATUS_ENCODED, F_PROPERTY_OWNER
    ) AS result
    FROM features
)
SELECT OBJECT_CONSTRUCT(
    'score_band', result:score_band::INTEGER,
    'credit_rating', result:credit_rating::VARCHAR,
    'recommended_decision', result:decision::VARCHAR,
    'max_credit_limit', result:max_credit_limit::NUMBER
)
FROM prediction
$$;

-- Tool 3: Search Policies
CREATE OR REPLACE FUNCTION APP_ZONE.CORTEX.TOOL_SEARCH_POLICIES(query VARCHAR)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
SELECT ARRAY_AGG(OBJECT_CONSTRUCT(
    'document_name', DOCUMENT_NAME,
    'category', CATEGORY,
    'text', CHUNK_TEXT,
    'relevance', RELEVANCE_SCORE
))
FROM TABLE(APP_ZONE.CORTEX.SEARCH_CREDIT_POLICIES(query, 5))
$$;

-- Tool 4: Calculate DTI
CREATE OR REPLACE FUNCTION APP_ZONE.CORTEX.TOOL_CALCULATE_DTI(
    customer_id VARCHAR,
    proposed_emi NUMBER
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
WITH income AS (
    SELECT VERIFIED_ANNUAL_INCOME / 12 AS monthly_income
    FROM ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED
    WHERE CUSTOMER_ID = customer_id
),
debt AS (
    SELECT COALESCE(SUM(MONTHLY_PAYMENT), 0) AS existing_emi
    FROM CURATED_ZONE.LOANS.FACT_LOANS
    WHERE CUSTOMER_ID = customer_id AND LOAN_STATUS NOT IN ('CLOSED')
)
SELECT OBJECT_CONSTRUCT(
    'monthly_income', i.monthly_income,
    'existing_debt', d.existing_emi,
    'proposed_emi', proposed_emi,
    'total_debt', d.existing_emi + proposed_emi,
    'current_dti', ROUND((d.existing_emi / i.monthly_income) * 100, 2),
    'proposed_dti', ROUND(((d.existing_emi + proposed_emi) / i.monthly_income) * 100, 2)
)
FROM income i, debt d
$$;

-- Main Agent Function
CREATE OR REPLACE FUNCTION APP_ZONE.CORTEX.CREDIT_AGENT_EVALUATE(
    application_id VARCHAR,
    customer_id VARCHAR,
    requested_amount NUMBER,
    requested_term INTEGER,
    product_type VARCHAR
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'evaluate'
AS
$$
import json
from snowflake.snowpark.context import get_active_session

def evaluate(app_id, cust_id, amount, term, product):
    session = get_active_session()
    
    # Calculate EMI
    rate = 0.08 / 12
    emi = (amount * rate * (1 + rate)**term) / ((1 + rate)**term - 1)
    
    # Gather data using tools
    profile = session.sql(f"SELECT APP_ZONE.CORTEX.TOOL_GET_CUSTOMER_PROFILE('{cust_id}')").collect()[0][0]
    score = session.sql(f"SELECT APP_ZONE.CORTEX.TOOL_GET_ML_CREDIT_SCORE('{cust_id}')").collect()[0][0]
    dti = session.sql(f"SELECT APP_ZONE.CORTEX.TOOL_CALCULATE_DTI('{cust_id}', {emi})").collect()[0][0]
    
    # Search policies
    policy_query = f"credit scoring for {product} DTI limits"
    policies = session.sql(f"SELECT APP_ZONE.CORTEX.TOOL_SEARCH_POLICIES('{policy_query}')").collect()[0][0]
    
    # Build agent prompt
    agent_config = session.sql("SELECT SYSTEM_PROMPT FROM APP_ZONE.CORTEX.AGENT_CONFIG WHERE AGENT_ID = 'CREDIT_AGENT_V1'").collect()[0][0]
    
    prompt = f"""{agent_config}

APPLICATION: {app_id}
Customer: {cust_id}
Product: {product}
Amount: ${amount:,.2f}
Term: {term} months
EMI: ${emi:,.2f}

CUSTOMER PROFILE:
{json.dumps(json.loads(profile) if isinstance(profile, str) else profile, indent=2)}

ML CREDIT SCORE:
{json.dumps(json.loads(score) if isinstance(score, str) else score, indent=2)}

DTI ANALYSIS:
{json.dumps(json.loads(dti) if isinstance(dti, str) else dti, indent=2)}

RELEVANT POLICIES:
{json.dumps(json.loads(policies) if isinstance(policies, str) else policies, indent=2)}

Provide your analysis and recommendation."""
    
    # Call LLM
    analysis = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-3-5-sonnet', '{prompt.replace("'", "''")}')
    """).collect()[0][0]
    
    # Determine decision
    decision = "REFER"
    if "APPROVE" in analysis.upper():
        decision = "APPROVE"
    elif "DECLINE" in analysis.upper():
        decision = "DECLINE"
    
    return {
        'application_id': app_id,
        'agent_analysis': analysis,
        'final_recommendation': decision,
        'data_gathered': {
            'profile': json.loads(profile) if isinstance(profile, str) else profile,
            'ml_score': json.loads(score) if isinstance(score, str) else score,
            'dti': json.loads(dti) if isinstance(dti, str) else dti
        }
    }
$$;
```

---

## Feature 5: Snowflake Intelligence

### Purpose
Natural language interface for different personas (Credit Officers, Risk Managers, etc.)

### Implementation

```sql
-- ============================================
-- SNOWFLAKE INTELLIGENCE CONFIGURATIONS
-- ============================================

CREATE OR REPLACE TABLE APP_ZONE.INTELLIGENCE.PERSONA_CONFIGS (
    PERSONA_ID VARCHAR(50) PRIMARY KEY,
    PERSONA_NAME VARCHAR(100),
    ROLE_DESCRIPTION TEXT,
    ALLOWED_DATA_DOMAINS VARIANT,
    SAMPLE_QUESTIONS VARIANT,
    IS_ACTIVE BOOLEAN DEFAULT TRUE
);

INSERT INTO APP_ZONE.INTELLIGENCE.PERSONA_CONFIGS VALUES
('CREDIT_OFFICER', 'Credit Officer', 
 'Front-line credit decision maker',
 PARSE_JSON('["CUSTOMER_360", "CREDIT_APPLICATIONS", "LOANS", "POLICIES"]'),
 PARSE_JSON('[
    "Show me pending applications in my queue",
    "What is the credit profile for customer CUS-123456?",
    "How many applications did I process this week?",
    "Show me high-risk applications that need review"
 ]'),
 TRUE),

('RISK_MANAGER', 'Risk Manager',
 'Senior risk professional monitoring portfolio health',
 PARSE_JSON('["CUSTOMER_360", "LOANS", "PORTFOLIO_METRICS", "ALL_DECISIONS"]'),
 PARSE_JSON('[
    "What is the current delinquency rate by product?",
    "Show portfolio concentration by risk band",
    "Which segments exceed risk appetite limits?",
    "What is the trend in 30+ DPD over last 6 months?"
 ]'),
 TRUE);

-- Semantic model view for Intelligence
CREATE OR REPLACE SECURE VIEW APP_ZONE.INTELLIGENCE.V_CREDIT_INTELLIGENCE AS
SELECT 
    a.APPLICATION_ID,
    a.APPLICATION_TYPE,
    a.REQUESTED_AMOUNT,
    a.STATUS AS APPLICATION_STATUS,
    d.FINAL_DECISION,
    d.ML_CREDIT_RATING,
    c.CUSTOMER_SEGMENT,
    c.RISK_CATEGORY,
    c.CREDIT_SCORE,
    DATEDIFF('HOUR', a.SUBMITTED_AT, d.DECISION_TIMESTAMP) AS HOURS_TO_DECISION
FROM APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS a
LEFT JOIN APP_ZONE.TRANSACTIONAL.CREDIT_DECISIONS d ON a.APPLICATION_ID = d.APPLICATION_ID
LEFT JOIN ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED c ON a.CUSTOMER_ID = c.CUSTOMER_ID;
```

---

## Feature 6: Data Masking & PII Detection

### Purpose
Automatic PII classification and role-based dynamic masking.

### Implementation

```sql
-- ============================================
-- PII DETECTION AND DATA MASKING
-- ============================================

-- Classification Tags
CREATE OR REPLACE TAG GOVERNANCE.TAGS.DATA_SENSITIVITY
  ALLOWED_VALUES = ('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'PII')
  COMMENT = 'Data sensitivity classification';

CREATE OR REPLACE TAG GOVERNANCE.TAGS.PII_TYPE
  ALLOWED_VALUES = ('NAME', 'EMAIL', 'PHONE', 'SSN', 'DOB', 'ADDRESS', 'INCOME', 'NONE')
  COMMENT = 'Type of PII';

-- Apply tags
ALTER TABLE ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED MODIFY COLUMN
  FULL_NAME SET TAG GOVERNANCE.TAGS.PII_TYPE = 'NAME',
  FULL_NAME SET TAG GOVERNANCE.TAGS.DATA_SENSITIVITY = 'PII';

ALTER TABLE ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED MODIFY COLUMN
  DATE_OF_BIRTH SET TAG GOVERNANCE.TAGS.PII_TYPE = 'DOB';

-- Masking Policies

-- Mask names
CREATE OR REPLACE MASKING POLICY GOVERNANCE.POLICIES.MASK_CUSTOMER_NAME AS
(val VARCHAR) RETURNS VARCHAR ->
  CASE
    WHEN IS_ROLE_IN_SESSION('ADMIN') THEN val
    WHEN IS_ROLE_IN_SESSION('CREDIT_OFFICER') THEN 
      CONCAT(LEFT(val, 1), '. ', SPLIT_PART(val, ' ', -1))
    ELSE '***MASKED***'
  END;

-- Mask DOB
CREATE OR REPLACE MASKING POLICY GOVERNANCE.POLICIES.MASK_DOB AS
(val DATE) RETURNS DATE ->
  CASE
    WHEN IS_ROLE_IN_SESSION('ADMIN') THEN val
    WHEN IS_ROLE_IN_SESSION('CREDIT_OFFICER') THEN DATE_FROM_PARTS(YEAR(val), 1, 1)
    ELSE NULL
  END;

-- Apply masking
ALTER TABLE ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED MODIFY COLUMN
  FULL_NAME SET MASKING POLICY GOVERNANCE.POLICIES.MASK_CUSTOMER_NAME;

ALTER TABLE ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED MODIFY COLUMN
  DATE_OF_BIRTH SET MASKING POLICY GOVERNANCE.POLICIES.MASK_DOB;

-- PII Detection Function
CREATE OR REPLACE FUNCTION GOVERNANCE.POLICIES.DETECT_PII(text_value VARCHAR)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
SELECT OBJECT_CONSTRUCT(
    'contains_email', REGEXP_LIKE(text_value, '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}'),
    'contains_phone', REGEXP_LIKE(text_value, '\\+?[0-9]{8,15}'),
    'contains_ssn', REGEXP_LIKE(text_value, '[0-9]{3}-[0-9]{2}-[0-9]{4}'),
    'pii_detected', (
        REGEXP_LIKE(text_value, '[A-Za-z0-9._%+-]+@') OR
        REGEXP_LIKE(text_value, '\\+?[0-9]{8,15}')
    )
)
$$;
```

---

## Feature 7: Apache Polaris Integration

### Purpose
Federated access to Databricks Iceberg tables via Polaris catalog.

### Implementation

```sql
-- ============================================
-- APACHE POLARIS CATALOG INTEGRATION
-- ============================================

-- Create External Volume
CREATE OR REPLACE EXTERNAL VOLUME DATABRICKS_ICEBERG_VOLUME
  STORAGE_LOCATIONS = (
    (
      NAME = 'databricks-iceberg-s3'
      STORAGE_PROVIDER = 'S3'
      STORAGE_BASE_URL = 's3://your-bank-datalake/iceberg/'
      STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789:role/snowflake-polaris'
      STORAGE_AWS_EXTERNAL_ID = 'snowflake_external_id'
    )
  );

-- Create Polaris Catalog Integration
CREATE OR REPLACE CATALOG INTEGRATION POLARIS_DATABRICKS_CATALOG
  CATALOG_SOURCE = POLARIS
  TABLE_FORMAT = ICEBERG
  CATALOG_NAMESPACE = 'credit_bureau_data'
  REST_CONFIG = (
    CATALOG_URI = 'https://polaris.databricks.cloud/api/catalog'
    WAREHOUSE = 'databricks_warehouse'
  )
  REST_AUTHENTICATION = (
    TYPE = OAUTH
    OAUTH_CLIENT_ID = 'polaris-client'
    OAUTH_CLIENT_SECRET = SECRET 'polaris_secret'
    OAUTH_TOKEN_URI = 'https://polaris.databricks.cloud/api/catalog/v1/oauth/tokens'
  )
  ENABLED = TRUE;

-- Create Iceberg Tables
CREATE OR REPLACE ICEBERG TABLE RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT
  CATALOG = 'POLARIS_DATABRICKS_CATALOG'
  EXTERNAL_VOLUME = 'DATABRICKS_ICEBERG_VOLUME'
  CATALOG_TABLE_NAME = 'credit_bureau.credit_bureau_report'
  AUTO_REFRESH = TRUE
  REFRESH_INTERVAL_SECONDS = 300;

CREATE OR REPLACE ICEBERG TABLE RAW_ZONE.DATABRICKS_SRC.INCOME_VERIFICATION
  CATALOG = 'POLARIS_DATABRICKS_CATALOG'
  EXTERNAL_VOLUME = 'DATABRICKS_ICEBERG_VOLUME'
  CATALOG_TABLE_NAME = 'credit_bureau.income_verification'
  AUTO_REFRESH = TRUE
  REFRESH_INTERVAL_SECONDS = 300;

-- Monitor sync status
CREATE OR REPLACE VIEW GOVERNANCE.AUDIT.POLARIS_SYNC_STATUS AS
SELECT 
    TABLE_NAME,
    LAST_REFRESH_TIME,
    REFRESH_STATUS,
    DATEDIFF('MINUTE', LAST_REFRESH_TIME, CURRENT_TIMESTAMP()) AS MINUTES_SINCE_REFRESH
FROM TABLE(INFORMATION_SCHEMA.ICEBERG_TABLE_REFRESH_HISTORY())
WHERE CATALOG_NAME = 'POLARIS_DATABRICKS_CATALOG';
```

---

## Feature 8: Snowflake Openflow

### Purpose
Real-time CDC from Oracle T24 and MySQL.

### Implementation

```sql
-- ============================================
-- SNOWFLAKE OPENFLOW CONNECTORS
-- ============================================

-- Oracle T24 Openflow Connector
CREATE OR REPLACE CONNECTOR ORACLE_T24_CONNECTOR
  TYPE = 'ORACLE'
  CONNECTION_STRING = 'jdbc:oracle:thin:@oracle-t24:1521:XE'
  CREDENTIALS = (
    USERNAME = 't24user'
    PASSWORD = SECRET 'oracle_t24_password'
  )
  CDC_MODE = 'LOG_BASED'
  DESTINATION_DATABASE = 'CREDIT_DECISIONING_DB'
  DESTINATION_SCHEMA = 'RAW_ZONE.ORACLE_T24_SRC'
  TABLES = (
    'T24_CUSTOMER',
    'T24_ACCOUNT',
    'T24_LOAN',
    'T24_TRANSACTION',
    'T24_PAYMENT_SCHEDULE',
    'T24_COLLATERAL'
  )
  REFRESH_INTERVAL = '1 MINUTE'
  ENABLED = TRUE;

-- MySQL Digital Banking Openflow Connector
CREATE OR REPLACE CONNECTOR MYSQL_DIGITAL_CONNECTOR
  TYPE = 'MYSQL'
  CONNECTION_STRING = 'jdbc:mysql://mysql-digital:3306/digital_banking'
  CREDENTIALS = (
    USERNAME = 'digitaluser'
    PASSWORD = SECRET 'mysql_digital_password'
  )
  CDC_MODE = 'LOG_BASED'
  DESTINATION_DATABASE = 'CREDIT_DECISIONING_DB'
  DESTINATION_SCHEMA = 'RAW_ZONE.MYSQL_SRC'
  TABLES = (
    'DIGITAL_CUSTOMER_PROFILE',
    'DIGITAL_SESSION',
    'DIGITAL_EVENT',
    'DIGITAL_KYC_DOCUMENT'
  )
  REFRESH_INTERVAL = '30 SECONDS'
  ENABLED = TRUE;

-- Monitor connector status
CREATE OR REPLACE VIEW GOVERNANCE.AUDIT.OPENFLOW_STATUS AS
SELECT 
    CONNECTOR_NAME,
    STATUS,
    LAST_SYNC_TIME,
    RECORDS_PROCESSED,
    ERROR_COUNT
FROM TABLE(INFORMATION_SCHEMA.CONNECTOR_HISTORY())
WHERE CONNECTOR_NAME IN ('ORACLE_T24_CONNECTOR', 'MYSQL_DIGITAL_CONNECTOR');
```

---

## Feature 9: Snowpark ML Pipeline

### Purpose
XGBoost credit scoring model with real-time inference UDF.

### Implementation

```python
# credit_scoring_training.py - Snowflake Notebook

from snowflake.snowpark import Session
from snowflake.ml.modeling.preprocessing import StandardScaler
from snowflake.ml.modeling.xgboost import XGBClassifier
from snowflake.ml.registry import Registry

session = get_active_session()

# Load training data
training_df = session.table("ANALYTICS_ZONE.FEATURE_STORE.CREDIT_SCORING_FEATURES")

NUMERIC_FEATURES = [
    'F_AGE', 'F_ANNUAL_INCOME', 'F_DEBT_TO_INCOME',
    'F_CREDIT_SCORE', 'F_CREDIT_UTILIZATION', 'F_RELATIONSHIP_MONTHS'
]

CATEGORICAL_FEATURES = [
    'F_GENDER_ENCODED', 'F_EMPLOYMENT_STATUS_ENCODED', 'F_PROPERTY_OWNER'
]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = 'TARGET_CREDIT_SCORE_BAND'

# Train model
model = XGBClassifier(
    input_cols=ALL_FEATURES,
    label_cols=[TARGET],
    output_cols=['PREDICTED_SCORE_BAND'],
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1
)

model.fit(training_df)

# Register model
registry = Registry(session, database_name="ML_ZONE", schema_name="MODELS")
model_version = registry.log_model(
    model_name="CREDIT_SCORING_XGBOOST",
    version_name="v1",
    model=model
)
```

```sql
-- Real-time Inference UDF
CREATE OR REPLACE FUNCTION ML_ZONE.INFERENCE.PREDICT_CREDIT_SCORE(
    age INTEGER,
    annual_income FLOAT,
    debt_to_income FLOAT,
    credit_score INTEGER,
    credit_utilization FLOAT,
    relationship_months INTEGER,
    gender_encoded INTEGER,
    employment_encoded INTEGER,
    property_owner INTEGER
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('snowflake-ml-python', 'xgboost')
HANDLER = 'predict'
AS
$$
from snowflake.ml.registry import Registry

_model = None

def get_model(session):
    global _model
    if _model is None:
        registry = Registry(session, database_name="ML_ZONE", schema_name="MODELS")
        _model = registry.get_model("CREDIT_SCORING_XGBOOST").version("v1").load()
    return _model

def predict(age, income, dti, score, util, rel, gender, emp, prop):
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    
    model = get_model(session)
    input_df = session.create_dataframe([[
        age, income, dti, score, util, rel, gender, emp, prop
    ]], schema=['F_AGE', 'F_ANNUAL_INCOME', 'F_DEBT_TO_INCOME', 
                'F_CREDIT_SCORE', 'F_CREDIT_UTILIZATION', 'F_RELATIONSHIP_MONTHS',
                'F_GENDER_ENCODED', 'F_EMPLOYMENT_STATUS_ENCODED', 'F_PROPERTY_OWNER'])
    
    result = model.predict(input_df).collect()[0]
    score_band = result['PREDICTED_SCORE_BAND']
    
    return {
        'score_band': int(score_band),
        'credit_rating': ['F', 'E', 'D', 'C-', 'C', 'C+', 'B', 'B+', 'A', 'A+'][score_band],
        'decision': 'APPROVE' if score_band >= 5 else 'DECLINE',
        'max_credit_limit': int(income * [0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0][score_band])
    }
$$;
```

---

## Feature 10: Dynamic Tables

### Purpose
Declarative data pipelines for Customer 360 and Feature Store.

### Implementation

```sql
-- ============================================
-- DYNAMIC TABLES FOR DATA PIPELINES
-- ============================================

-- Customer 360 Dynamic Table
CREATE OR REPLACE DYNAMIC TABLE ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED
  TARGET_LAG = '5 minutes'
  WAREHOUSE = ETL_WH
AS
SELECT 
    c.CUSTOMER_ID,
    c.NAME_1 AS FULL_NAME,
    c.DATE_OF_BIRTH,
    DATEDIFF('YEAR', c.DATE_OF_BIRTH, CURRENT_DATE()) AS AGE,
    -- ... (see full definition in Data Model section)
FROM RAW_ZONE.ORACLE_T24_SRC.T24_CUSTOMER c
-- ... (joins to other sources)
;

-- Feature Store Dynamic Table
CREATE OR REPLACE DYNAMIC TABLE ANALYTICS_ZONE.FEATURE_STORE.CREDIT_SCORING_FEATURES
  TARGET_LAG = '15 minutes'
  WAREHOUSE = ML_WH
AS
SELECT 
    c.CUSTOMER_ID,
    CURRENT_DATE() AS FEATURE_DATE,
    c.AGE AS F_AGE,
    c.VERIFIED_ANNUAL_INCOME AS F_ANNUAL_INCOME,
    c.DEBT_TO_INCOME_RATIO AS F_DEBT_TO_INCOME,
    c.CREDIT_SCORE AS F_CREDIT_SCORE,
    -- ... (compute all features)
FROM ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED c;
```

---

## Streamlit Application

### Application Structure

```
streamlit/
├── main.py
├── requirements.txt
├── .streamlit/config.toml
│
├── pages/
│   ├── 1_🏠_Executive_Dashboard.py
│   ├── 2_📝_Application_Portal.py
│   ├── 3_📋_Application_Queue.py
│   ├── 4_🤖_AI_Credit_Agent.py
│   ├── 5_💬_Intelligence_Chat.py
│   ├── 6_👥_Customer_360.py
│   ├── 7_📊_Portfolio_Analytics.py
│   ├── 8_📚_Policy_Manager.py
│   ├── 9_🔒_Governance_Center.py
│   └── 10_⚙️_Admin_Console.py
│
├── components/
│   ├── agent_chat.py
│   ├── application_form.py
│   ├── customer_profile_card.py
│   └── lineage_graph.py
│
└── utils/
    ├── agent.py
    ├── database.py
    └── ml_inference.py
```

### requirements.txt

```
streamlit>=1.30.0
snowflake-snowpark-python>=1.11.0
pandas>=2.0.0
plotly>=5.18.0
altair>=5.2.0
```

### Sample Application Page

See detailed code samples in the architecture sections above.

---

## Implementation Phases

### Phase 1: Foundation
- Set up Docker containers for Oracle and MySQL
- Create database schemas in external sources
- Generate 100K customers of sample data
- Set up Snowflake account and database structure

### Phase 2: Data Connectivity 
- Configure Openflow connectors for Oracle and MySQL
- Set up Databricks with Iceberg tables
- Configure Polaris catalog integration
- Verify CDC streams are flowing

### Phase 3: Data Pipeline
- Create Dynamic Tables for bronze-to-silver-to-gold
- Build Customer 360 unified view
- Create Feature Store tables
- Test data refresh and lineage

### Phase 4: Governance
- Apply classification tags to all tables
- Create masking policies for PII
- Set up row access policies
- Configure audit logging

### Phase 5: SnowConvert Migration 
- Identify T24 procedures to migrate
- Run SnowConvert AI on PL/SQL code
- Test converted procedures
- Document migration

### Phase 6: Unistore Implementation
- Create Hybrid Tables for applications
- Build transactional procedures
- Test concurrent access and performance
- Create application queue views

### Phase 7: ML Pipeline 
- Prepare training dataset
- Train XGBoost model in Snowpark
- Register model in Model Registry
- Create real-time inference UDF
- Test predictions

### Phase 8: Cortex AI
- Upload and process policy documents
- Create Cortex Search service
- Build agent tools and orchestrator
- Configure agent system prompt
- Test agent recommendations

### Phase 9: Snowflake Intelligence 
- Create persona configurations
- Build semantic model views
- Configure sample questions
- Test natural language queries

### Phase 10: Streamlit Application 
- Set up application structure
- Build core pages (Dashboard, Agent, Queue)
- Integrate with all backend services
- Add governance and analytics pages

### Phase 11: Testing & Documentation 
- End-to-end testing
- Performance testing
- Security review
- Complete documentation
- Create demo script

---

## GitHub Repository Structure

```
snowflake-credit-decisioning/
├── README.md
├── LICENSE
├── .gitignore
│
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   ├── setup-guide.md
│   └── demo-script.md
│
├── infrastructure/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── oracle/init.sql
│   │   └── mysql/init.sql
│   └── databricks/
│       └── create_iceberg_tables.py
│
├── snowflake/
│   ├── 00_setup/
│   │   ├── 01_create_database.sql
│   │   ├── 02_create_schemas.sql
│   │   ├── 03_create_warehouses.sql
│   │   └── 04_create_roles.sql
│   │
│   ├── 01_connectors/
│   │   ├── oracle_openflow.sql
│   │   ├── mysql_openflow.sql
│   │   └── databricks_polaris.sql
│   │
│   ├── 02_raw_zone/
│   │   └── create_raw_tables.sql
│   │
│   ├── 03_curated_zone/
│   │   ├── tables/
│   │   ├── dynamic_tables/
│   │   └── t24_migrated/
│   │
│   ├── 04_analytics_zone/
│   │   ├── customer_360.sql
│   │   └── feature_store.sql
│   │
│   ├── 05_unistore/
│   │   ├── hybrid_tables.sql
│   │   └── transactional_procedures.sql
│   │
│   ├── 06_ml_zone/
│   │   ├── training_pipeline.py
│   │   └── inference_udf.sql
│   │
│   ├── 07_cortex/
│   │   ├── policy_documents.sql
│   │   ├── cortex_search.sql
│   │   ├── cortex_agent.sql
│   │   └── snowflake_intelligence.sql
│   │
│   └── 08_governance/
│       ├── tags.sql
│       ├── masking_policies.sql
│       └── row_access_policies.sql
│
├── streamlit/
│   ├── main.py
│   ├── requirements.txt
│   ├── pages/
│   ├── components/
│   └── utils/
│
├── data/
│   ├── generators/
│   │   ├── generate_t24_data.py
│   │   ├── generate_digital_data.py
│   │   └── generate_bureau_data.py
│   └── policies/
│       ├── credit_scoring_policy.txt
│       ├── dti_guidelines.txt
│       └── risk_appetite.txt
│
└── scripts/
    ├── deploy.sh
    ├── setup_local_dbs.sh
    └── load_sample_data.sh
```

---

## Sample Data Generation

### Data Volumes

| Table | Records | Notes |
|-------|---------|-------|
| T24_CUSTOMER | 100,000 | All customers |
| T24_ACCOUNT | 180,000 | 1.8 accounts per customer |
| T24_LOAN | 35,000 | 35% have loans |
| T24_TRANSACTION | 5,000,000 | 50 txns per account |
| DIGITAL_CUSTOMER_PROFILE | 75,000 | 75% digitally enrolled |
| CREDIT_BUREAU_REPORT | 100,000 | 1 per customer |

### Generation Strategy

```python
# generate_t24_data.py (excerpt)

import pandas as pd
from faker import Faker
import numpy as np

fake = Faker()

# Generate customers
customers = []
for i in range(100000):
    customers.append({
        'CUSTOMER_ID': f'CUS-{i:06d}',
        'NAME_1': fake.name(),
        'DATE_OF_BIRTH': fake.date_of_birth(minimum_age=18, maximum_age=80),
        'GENDER': np.random.choice(['M', 'F'], p=[0.5, 0.5]),
        'NATIONALITY': 'SGP',
        # Credit score follows beta distribution
        'CREDIT_SCORE': int(np.random.beta(2, 2) * 550 + 300),
        # ...
    })

df = pd.DataFrame(customers)
```

---

## Testing & Validation

### Test Plan

1. **Data Connectivity Tests**
   - Verify Openflow CDC latency < 1 minute
   - Verify Polaris sync working
   - Check data quality and completeness

2. **Performance Tests**
   - Hybrid Table: < 10ms read latency
   - ML Inference UDF: < 500ms response time
   - Cortex Search: < 300ms query time

3. **Functional Tests**
   - End-to-end application submission to decision
   - Agent makes appropriate recommendations
   - Data masking working by role
   - Lineage correctly tracked

4. **Security Tests**
   - PII properly masked
   - Row access policies enforced
   - Audit logs complete

---

## Conclusion

This implementation plan provides a complete blueprint for building a production-grade credit decisioning platform on Snowflake that showcases every major differentiating capability of the platform. The combination of real-time data integration, AI-powered decision making, transactional processing, and comprehensive governance creates a compelling demonstration of Snowflake as a unified enterprise data platform.

**Key Success Metrics:**
- 100,000 customers with full history
- < 10 second end-to-end decision time
- 90%+ agent decision accuracy
- Full data lineage coverage
- Zero PII leaks in testing

**Estimated Total Implementation Time:** 8 weeks (1 developer)

---

*End of Implementation Plan*
