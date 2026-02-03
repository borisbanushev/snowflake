# 🚀 Complete Snowflake Data Load Guide

## ✅ CSV Files Generated Successfully!

All CSV files are ready in: `/Users/boris/Desktop/snowflake/data/generated_csv/`

**Total: 170,341 records across 19 tables**

---

## 📋 Quick Setup Steps

### Step 1: Run Setup SQL Scripts in Snowflake UI

Open Snowflake UI and run these scripts in order:

1. **`01_create_schemas.sql`** - Creates 4 schemas
2. **`02_create_tables.sql`** - Creates all 19 tables  
3. **`03_create_stage.sql`** - Creates CSV upload stage

---

### Step 2: Upload CSV Files to Snowflake Stage

#### Option A: Using Snowflake Web UI (Easiest)

**Method 1: Via Top Navigation Menu**
1. In Snowflake UI, click **"Data"** in the top navigation bar
2. Select **"Databases"** from the dropdown
3. Click on **CREDIT_DECISIONING_DB** database
4. In the database details page, look for tabs/sections: **"Database Details"**, **"Schemas"**, **"Stages"**, etc.
5. Click on the **"Stages"** tab
6. You should see **CSV_DATA_STAGE** listed
7. Click on **CSV_DATA_STAGE**
8. Click the **"+ Files"** or **"Upload"** button
9. Select all 19 CSV files from `/Users/boris/Desktop/snowflake/data/generated_csv/`
10. Click **Upload**

**Method 2: Via Database Explorer (Where You Are Now)**
1. In the Database Explorer (left sidebar), you're already viewing **CREDIT_DECISIONING_DB**
2. In the main content area, look for tabs at the top: **"Database Details"**, **"Schemas"**, **"Stages"**, etc.
3. Click on the **"Stages"** tab (next to "Database Details" and "Schemas")
4. You should see **CSV_DATA_STAGE** listed
5. Click on **CSV_DATA_STAGE** to open it
6. Click the **"+ Files"** or **"Upload"** button
7. Select all 19 CSV files from `/Users/boris/Desktop/snowflake/data/generated_csv/`
8. Click **Upload**

**Method 3: Verify Stage Exists First (Troubleshooting)**
If you still can't find Stages, verify it exists:
1. Open a SQL worksheet in Snowflake
2. Run: `SHOW STAGES IN DATABASE CREDIT_DECISIONING_DB;`
3. You should see `CSV_DATA_STAGE` in the results
4. If it exists but you can't see it in UI, use Option B (SnowSQL) below

#### Option B: Using Python Script (Fastest - Recommended!)

I've created a simple Python script that uploads all files automatically:

```bash
cd /Users/boris/Desktop/snowflake
python3 scripts/upload_csvs_to_stage.py
```

This will:
- ✅ Connect to Snowflake automatically
- ✅ Upload all 19 CSV files to `CSV_DATA_STAGE`
- ✅ Show progress bar
- ✅ Complete in seconds!

**Note:** If you get authentication errors, use Option A (UI) instead - it's more reliable for first-time setup.

#### Option C: Using SnowSQL CLI (Command Line Only - NOT Web UI!)

⚠️ **IMPORTANT:** The `PUT` command with `file:///` paths **ONLY works from command line** (SnowSQL CLI), **NOT from the Snowflake Web UI**. If you try it in the web UI, you'll get "Unsupported feature" error.

**To use this option:**

1. **Install SnowSQL** (if not installed):
   ```bash
   brew install snowflake-snowsql  # Requires your password
   ```

2. **Configure connection** (first time only):
   ```bash
   snowsql -a MZHGUVK-BC67154 -u ACCOUNTADMIN
   # Enter password when prompted, then type: !exit
   ```

3. **Upload files from terminal**:
   ```bash
   cd /Users/boris/Desktop/snowflake/data/generated_csv
   snowsql -a MZHGUVK-BC67154 -u ACCOUNTADMIN -d CREDIT_DECISIONING_DB -w COMPUTE_WH \
     -q "PUT file:///*.csv @CSV_DATA_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
   ```

**Recommendation:** Use **Option A (Web UI)** - it's simpler and doesn't require CLI installation!

---

### Step 3: Load Data into Tables

Run this SQL script in Snowflake UI:

```sql
USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;

-- DIGITAL_BANKING schema
USE SCHEMA DIGITAL_BANKING;

COPY INTO DIGITAL_CUSTOMER_PROFILE FROM @CSV_DATA_STAGE/digital_customer_profile.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO DIGITAL_SESSION FROM @CSV_DATA_STAGE/digital_session.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO DIGITAL_EVENT FROM @CSV_DATA_STAGE/digital_event.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO DIGITAL_KYC_DOCUMENT FROM @CSV_DATA_STAGE/digital_kyc_document.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

-- CORE_BANKING schema
USE SCHEMA CORE_BANKING;

COPY INTO T24_CUSTOMER FROM @CSV_DATA_STAGE/t24_customer.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO T24_ACCOUNT FROM @CSV_DATA_STAGE/t24_account.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO T24_LOAN FROM @CSV_DATA_STAGE/t24_loan.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO T24_TRANSACTION FROM @CSV_DATA_STAGE/t24_transaction.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO T24_PAYMENT_SCHEDULE FROM @CSV_DATA_STAGE/t24_payment_schedule.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO T24_COLLATERAL FROM @CSV_DATA_STAGE/t24_collateral.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

-- CREDIT_BUREAU schema
USE SCHEMA CREDIT_BUREAU;

COPY INTO CREDIT_SCORE FROM @CSV_DATA_STAGE/credit_score.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO CREDIT_INQUIRY FROM @CSV_DATA_STAGE/credit_inquiry.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO TRADELINE FROM @CSV_DATA_STAGE/tradeline.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO PUBLIC_RECORD FROM @CSV_DATA_STAGE/public_record.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

-- REFERENCE_DATA schema
USE SCHEMA REFERENCE_DATA;

COPY INTO COUNTRY_CODE FROM @CSV_DATA_STAGE/country_code.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO CURRENCY_CODE FROM @CSV_DATA_STAGE/currency_code.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO PRODUCT_CATALOG FROM @CSV_DATA_STAGE/product_catalog.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO BRANCH_DIRECTORY FROM @CSV_DATA_STAGE/branch_directory.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

COPY INTO RELATIONSHIP_MANAGER FROM @CSV_DATA_STAGE/relationship_manager.csv
FILE_FORMAT = (TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');
```

---

### Step 4: Validate Data Load

```sql
-- Validate all tables
SELECT 'DIGITAL_CUSTOMER_PROFILE' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM DIGITAL_BANKING.DIGITAL_CUSTOMER_PROFILE
UNION ALL
SELECT 'DIGITAL_SESSION', COUNT(*) FROM DIGITAL_BANKING.DIGITAL_SESSION
UNION ALL
SELECT 'DIGITAL_EVENT', COUNT(*) FROM DIGITAL_BANKING.DIGITAL_EVENT
UNION ALL
SELECT 'DIGITAL_KYC_DOCUMENT', COUNT(*) FROM DIGITAL_BANKING.DIGITAL_KYC_DOCUMENT
UNION ALL
SELECT 'T24_CUSTOMER', COUNT(*) FROM CORE_BANKING.T24_CUSTOMER
UNION ALL
SELECT 'T24_ACCOUNT', COUNT(*) FROM CORE_BANKING.T24_ACCOUNT
UNION ALL
SELECT 'T24_LOAN', COUNT(*) FROM CORE_BANKING.T24_LOAN
UNION ALL
SELECT 'T24_TRANSACTION', COUNT(*) FROM CORE_BANKING.T24_TRANSACTION
UNION ALL
SELECT 'T24_PAYMENT_SCHEDULE', COUNT(*) FROM CORE_BANKING.T24_PAYMENT_SCHEDULE
UNION ALL
SELECT 'T24_COLLATERAL', COUNT(*) FROM CORE_BANKING.T24_COLLATERAL
UNION ALL
SELECT 'CREDIT_SCORE', COUNT(*) FROM CREDIT_BUREAU.CREDIT_SCORE
UNION ALL
SELECT 'CREDIT_INQUIRY', COUNT(*) FROM CREDIT_BUREAU.CREDIT_INQUIRY
UNION ALL
SELECT 'TRADELINE', COUNT(*) FROM CREDIT_BUREAU.TRADELINE
UNION ALL
SELECT 'PUBLIC_RECORD', COUNT(*) FROM CREDIT_BUREAU.PUBLIC_RECORD
UNION ALL
SELECT 'COUNTRY_CODE', COUNT(*) FROM REFERENCE_DATA.COUNTRY_CODE
UNION ALL
SELECT 'CURRENCY_CODE', COUNT(*) FROM REFERENCE_DATA.CURRENCY_CODE
UNION ALL
SELECT 'PRODUCT_CATALOG', COUNT(*) FROM REFERENCE_DATA.PRODUCT_CATALOG
UNION ALL
SELECT 'BRANCH_DIRECTORY', COUNT(*) FROM REFERENCE_DATA.BRANCH_DIRECTORY
UNION ALL
SELECT 'RELATIONSHIP_MANAGER', COUNT(*) FROM REFERENCE_DATA.RELATIONSHIP_MANAGER
ORDER BY TABLE_NAME;
```

---

## 📊 Expected Row Counts

| Table | Expected Rows |
|-------|--------------|
| DIGITAL_CUSTOMER_PROFILE | 3,000 |
| DIGITAL_SESSION | 15,000 |
| DIGITAL_EVENT | 60,000 |
| DIGITAL_KYC_DOCUMENT | 3,000 |
| T24_CUSTOMER | 3,000 |
| T24_ACCOUNT | 5,400 |
| T24_LOAN | 1,200 |
| T24_TRANSACTION | 30,000 |
| T24_PAYMENT_SCHEDULE | 15,000 |
| T24_COLLATERAL | 921 |
| CREDIT_SCORE | 3,000 |
| CREDIT_INQUIRY | 12,000 |
| TRADELINE | 18,000 |
| PUBLIC_RECORD | 300 |
| COUNTRY_CODE | 250 |
| CURRENCY_CODE | 150 |
| PRODUCT_CATALOG | 50 |
| BRANCH_DIRECTORY | 20 |
| RELATIONSHIP_MANAGER | 50 |
| **TOTAL** | **170,341** |

---

## 🎯 What's Next?

After loading the data, you can:

1. **Build Analytics Views** - Join tables for customer 360 view
2. **Create ML Features** - Prepare features for credit scoring
3. **Deploy Streamlit App** - Build interactive dashboards
4. **Set up Cortex AI** - Add AI-powered insights

---

## 🔍 Sample Queries to Test Data

```sql
-- Customer 360 view
SELECT 
    c.CUSTOMER_ID,
    c.SHORT_NAME,
    c.RISK_CATEGORY,
    cs.SCORE AS CREDIT_SCORE,
    COUNT(DISTINCT a.ACCOUNT_ID) AS NUM_ACCOUNTS,
    COUNT(DISTINCT l.LOAN_ID) AS NUM_LOANS,
    SUM(a.WORKING_BALANCE) AS TOTAL_BALANCE
FROM CORE_BANKING.T24_CUSTOMER c
LEFT JOIN CREDIT_BUREAU.CREDIT_SCORE cs ON c.CUSTOMER_ID = cs.CUSTOMER_ID
LEFT JOIN CORE_BANKING.T24_ACCOUNT a ON c.CUSTOMER_ID = a.CUSTOMER_ID
LEFT JOIN CORE_BANKING.T24_LOAN l ON c.CUSTOMER_ID = l.CUSTOMER_ID
GROUP BY 1,2,3,4
LIMIT 100;

-- Digital engagement metrics
SELECT 
    d.CUSTOMER_ID,
    COUNT(DISTINCT s.SESSION_ID) AS NUM_SESSIONS,
    COUNT(DISTINCT e.EVENT_ID) AS NUM_EVENTS,
    d.EKYC_STATUS
FROM DIGITAL_BANKING.DIGITAL_CUSTOMER_PROFILE d
LEFT JOIN DIGITAL_BANKING.DIGITAL_SESSION s ON d.DIGITAL_ID = s.DIGITAL_ID
LEFT JOIN DIGITAL_BANKING.DIGITAL_EVENT e ON s.SESSION_ID = e.SESSION_ID
GROUP BY 1,4
LIMIT 100;
```

---

## ✅ Done!

All your data is ready for the credit decisioning platform demo! 🚀
