# 🔧 Quick Fix: Use `main` Catalog

The `sowcatalog` needs storage credentials. Let's use `main` catalog instead (it works!).

---

## ✅ Use These Updated SQL Commands:

### Step 1: Create Tables in `main` Catalog

Go to Databricks SQL: https://dbc-6730e836-5587.cloud.databricks.com/sql/editor

```sql
-- Use main catalog (has storage configured)
USE CATALOG main;

-- Create credit_bureau schema
CREATE SCHEMA IF NOT EXISTS credit_bureau;
USE SCHEMA credit_bureau;

-- Create Credit Bureau Report table
CREATE OR REPLACE TABLE CREDIT_BUREAU_REPORT (
    REPORT_ID STRING,
    CUSTOMER_ID STRING,
    BUREAU_NAME STRING,
    REPORT_DATE DATE,
    CREDIT_SCORE INT,
    CREDIT_SCORE_VERSION STRING,
    SCORE_FACTORS STRING,
    CREDIT_LIMIT_UTILIZATION DECIMAL(5,4),
    TOTAL_ACCOUNTS INT,
    OPEN_ACCOUNTS INT,
    CLOSED_ACCOUNTS INT,
    DELINQUENT_ACCOUNTS INT,
    PUBLIC_RECORDS INT,
    BANKRUPTCIES INT,
    TAX_LIENS INT,
    JUDGMENTS INT,
    COLLECTIONS INT,
    INQUIRIES_LAST_6M INT,
    INQUIRIES_LAST_12M INT,
    OLDEST_ACCOUNT_DATE DATE,
    NEWEST_ACCOUNT_DATE DATE,
    AVERAGE_ACCOUNT_AGE_MONTHS INT,
    TOTAL_BALANCE DECIMAL(18,2),
    TOTAL_CREDIT_LIMIT DECIMAL(18,2),
    TOTAL_MONTHLY_PAYMENT DECIMAL(18,2),
    DELINQUENCY_30_DAYS INT,
    DELINQUENCY_60_DAYS INT,
    DELINQUENCY_90_DAYS INT,
    CREATED_TIMESTAMP TIMESTAMP,
    MODIFIED_TIMESTAMP TIMESTAMP
);

-- Create Income Verification table
CREATE OR REPLACE TABLE INCOME_VERIFICATION (
    VERIFICATION_ID STRING,
    CUSTOMER_ID STRING,
    VERIFICATION_TYPE STRING,
    VERIFICATION_DATE DATE,
    EMPLOYER_NAME STRING,
    EMPLOYMENT_STATUS STRING,
    JOB_TITLE STRING,
    EMPLOYMENT_START_DATE DATE,
    EMPLOYMENT_SECTOR STRING,
    ANNUAL_INCOME DECIMAL(18,2),
    MONTHLY_INCOME DECIMAL(18,2),
    INCOME_SOURCE STRING,
    INCOME_STABILITY_SCORE INT,
    VERIFICATION_METHOD STRING,
    VERIFIED_BY STRING,
    VERIFICATION_STATUS STRING,
    DOCUMENTS_PROVIDED STRING,
    CONFIDENCE_LEVEL STRING,
    NOTES STRING,
    CREATED_TIMESTAMP TIMESTAMP
);

-- Verify tables created
SHOW TABLES IN main.credit_bureau;
```

This should work! ✅

---

### Step 2: Upload CSV Files

1. Go to **Data Explorer**: https://dbc-6730e836-5587.cloud.databricks.com/explore/data

2. Navigate to: **`main`** → **`credit_bureau`** → **`CREDIT_BUREAU_REPORT`**

3. Click **"Upload Data"** button

4. Select file: `/Users/boris/Desktop/snowflake/databricks_csv_data/credit_bureau_report.csv`

5. Wait for upload (~1-2 minutes)

6. Repeat for **`INCOME_VERIFICATION`** table with `income_verification.csv`

---

### Step 3: Verify Data

```sql
-- Check counts
SELECT COUNT(*) FROM main.credit_bureau.CREDIT_BUREAU_REPORT;
-- Expected: 100,000

SELECT COUNT(*) FROM main.credit_bureau.INCOME_VERIFICATION;
-- Expected: 100,000

-- View sample
SELECT * FROM main.credit_bureau.CREDIT_BUREAU_REPORT LIMIT 10;
```

---

## 📝 Update Snowflake Config

Once data is loaded, update your Snowflake connector to point to `main.credit_bureau`:

In `snowflake/01_connectors/databricks_polaris.sql`:
- Change: `CATALOG_NAME = 'main'`
- Change: `SCHEMA_NAME = 'credit_bureau'`

---

## 💡 Why This Works

- `main` catalog has default storage credentials configured
- `sowcatalog` needs admin to configure storage credentials
- Both will work the same from Snowflake's perspective

---

## Ready!

Try the SQL above - it should work now! Let me know if you get any errors.
