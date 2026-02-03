# 📤 Upload CSV Files to Databricks

## ✅ Files Ready!

Location: `/Users/boris/Desktop/snowflake/databricks_csv_data/`

- ✅ `credit_bureau_report.csv` (100,000 rows)
- ✅ `income_verification.csv` (100,000 rows)

---

## 🚀 Upload Steps (5 minutes)

### Step 1: Create Tables in Databricks SQL

1. **Go to Databricks SQL Editor:**
   - URL: https://dbc-6730e836-5587.cloud.databricks.com/sql/editor

2. **Run this SQL to create tables:**

```sql
-- Use your catalog and schema
USE CATALOG sowcatalog;
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

SELECT 'Tables created successfully!' AS status;
```

3. **Verify tables exist:**
```sql
SHOW TABLES IN sowcatalog.credit_bureau;
```

---

### Step 2: Upload CSV Files

#### **Option A: Using Databricks UI (Easiest)**

1. **Go to Data Explorer:**
   - URL: https://dbc-6730e836-5587.cloud.databricks.com/explore/data

2. **Navigate to your table:**
   - Click `sowcatalog` → `credit_bureau` → `CREDIT_BUREAU_REPORT`

3. **Upload CSV:**
   - Click **"Upload Data"** button (top right)
   - Or click **"Create"** → **"Upload Data into this Table"**
   - Select file: `databricks_csv_data/credit_bureau_report.csv`
   - Click **"Upload"**
   - Wait for upload to complete (~1-2 minutes)

4. **Repeat for second table:**
   - Go to `INCOME_VERIFICATION` table
   - Upload `databricks_csv_data/income_verification.csv`

#### **Option B: Using SQL COPY INTO**

1. **First, upload files to DBFS:**
   - Go to: Data → DBFS → Upload
   - Upload both CSV files to `/FileStore/csv/`

2. **Then load with SQL:**

```sql
-- Load Credit Bureau Report
COPY INTO sowcatalog.credit_bureau.CREDIT_BUREAU_REPORT
FROM '/FileStore/csv/credit_bureau_report.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true');

-- Load Income Verification
COPY INTO sowcatalog.credit_bureau.INCOME_VERIFICATION
FROM '/FileStore/csv/income_verification.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true');
```

---

### Step 3: Verify Data

Run these queries in Databricks SQL:

```sql
-- Check row counts
SELECT COUNT(*) as credit_report_count 
FROM sowcatalog.credit_bureau.CREDIT_BUREAU_REPORT;
-- Expected: 100,000

SELECT COUNT(*) as income_verification_count 
FROM sowcatalog.credit_bureau.INCOME_VERIFICATION;
-- Expected: 100,000

-- Sample data
SELECT * FROM sowcatalog.credit_bureau.CREDIT_BUREAU_REPORT LIMIT 10;

-- Check credit score distribution
SELECT 
    CASE 
        WHEN CREDIT_SCORE >= 800 THEN '800+ (Excellent)'
        WHEN CREDIT_SCORE >= 740 THEN '740-799 (Very Good)'
        WHEN CREDIT_SCORE >= 670 THEN '670-739 (Good)'
        WHEN CREDIT_SCORE >= 580 THEN '580-669 (Fair)'
        ELSE 'Below 580 (Poor)'
    END AS score_range,
    COUNT(*) as customer_count,
    ROUND(AVG(CREDIT_SCORE), 0) as avg_score
FROM sowcatalog.credit_bureau.CREDIT_BUREAU_REPORT
GROUP BY score_range
ORDER BY avg_score DESC;

-- Check income verification stats
SELECT 
    VERIFICATION_TYPE,
    COUNT(*) as count,
    ROUND(AVG(ANNUAL_INCOME), 0) as avg_income,
    ROUND(MIN(ANNUAL_INCOME), 0) as min_income,
    ROUND(MAX(ANNUAL_INCOME), 0) as max_income
FROM sowcatalog.credit_bureau.INCOME_VERIFICATION
GROUP BY VERIFICATION_TYPE;
```

---

## 📊 What's in the Data

### CREDIT_BUREAU_REPORT (100K rows)
- **Credit Scores:** 300-850 (realistic distribution)
- **Bureau Names:** Experian, Equifax, TransUnion
- **Account History:** Total accounts, open/closed, delinquencies
- **Public Records:** Bankruptcies, judgments, collections
- **Credit Utilization:** Actual balance vs. limit ratios
- **Inquiry History:** 6-month and 12-month lookbacks
- **Customer IDs:** CUS-000000 to CUS-099999

### INCOME_VERIFICATION (100K rows)
- **Annual Income:** $30K - $500K (varied distribution)
- **Employment Types:** Full-time, Part-time, Contract, Self-employed
- **Sectors:** Tech, Finance, Healthcare, Retail, Manufacturing
- **Verification Status:** Verified (85%), Pending (10%), Failed (5%)
- **Verification Methods:** Pay stubs, tax returns, bank statements
- **Customer IDs:** Matching credit bureau data (CUS-000000 to CUS-099999)

---

## ⏱️ Expected Time

- **Create tables:** 30 seconds
- **Upload credit_bureau_report.csv:** 1-2 minutes
- **Upload income_verification.csv:** 1-2 minutes
- **Verify data:** 30 seconds

**Total: 4-5 minutes**

---

## 🎯 Next: Connect to Snowflake

Once data is in Databricks, configure Snowflake to read it:

1. Update `snowflake/01_connectors/databricks_polaris.sql`:
   - Set catalog: `sowcatalog`
   - Set schema: `credit_bureau`
   - Add your Databricks workspace URL

2. Run connector in Snowflake

3. Query from Snowflake:
   ```sql
   SELECT COUNT(*) FROM RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT;
   ```

---

## ✅ Success Criteria

- ✅ Tables show 100,000 rows each
- ✅ Credit scores range from 300-850
- ✅ Income ranges from $30K-$500K
- ✅ Customer IDs match between tables (CUS-000000 to CUS-099999)
- ✅ No NULL values in key fields

---

## 🆘 Troubleshooting

**"Upload button is greyed out"**
- Make sure table is created first
- Check you have write permissions on the catalog

**"Type mismatch error"**
- Use Option B (COPY INTO) with `inferSchema = true`
- Or recreate table with all STRING columns, then cast later

**"File too large"**
- Files are ~30-40 MB each, should be fine
- If issues, split files into smaller chunks

**"Permission denied"**
- Check you have USE CATALOG and MODIFY permissions
- May need admin to grant: `GRANT MODIFY ON CATALOG sowcatalog TO `your_user`;`

---

Ready to upload! The files are in: `/Users/boris/Desktop/snowflake/databricks_csv_data/`

Just drag and drop them into Databricks! 🚀
