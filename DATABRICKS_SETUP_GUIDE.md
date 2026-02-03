# 🔧 Databricks Storage Configuration Guide

## Issue Diagnosed

Your Databricks Unity Catalog needs storage credentials configured to create managed tables.

**Error:** `PERMISSION_DENIED: Access denied. Cause: 403 Forbidden error from cloud storage provider`

---

## Solution Options

### Option 1: Configure Storage Credentials (Recommended - 10 minutes)

You need Databricks Workspace Admin or Account Admin access.

#### Steps:

1. **Go to Databricks Admin Console:**
   - URL: https://dbc-6730e836-5587.cloud.databricks.com
   - Click on your profile (top right) → "Admin Settings"

2. **Configure Storage Credentials:**
   - Go to: **Catalog** → **External Data** → **Storage Credentials**
   - Click **"Create Credential"**
   
3. **Create AWS Credential:**
   ```
   Name: default_storage_credential
   Type: AWS IAM Role
   ARN: arn:aws:iam::YOUR_ACCOUNT:role/databricks-unity-catalog-role
   ```
   
   Or if using Access Keys:
   ```
   Name: default_storage_credential  
   Type: AWS Access Keys
   Access Key: AKIA...
   Secret Key: ...
   ```

4. **Set as Default:**
   - Check "Set as default credential for the metastore"
   - Click "Create"

5. **Test:**
   - Run our script again: `./scripts/load_databricks_only.sh`
   - Should work now! ✅

---

### Option 2: Use Databricks SQL Editor (Manual - 5 minutes)

Create tables directly in Databricks SQL Editor (no storage credentials needed for SQL editor):

1. **Go to SQL Editor:**
   - URL: https://dbc-6730e836-5587.cloud.databricks.com/sql/editor

2. **Run this SQL:**

```sql
-- Create schema
USE CATALOG sowcatalog;
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

SELECT 'Tables created successfully!' AS status;
```

3. **Then load data via CSV:**
   - I'll generate CSV files for you
   - Upload via Databricks UI: Data → Import Data

---

### Option 3: Generate CSV Files (Easiest - Right Now!)

Let me generate CSV files you can upload directly:

```bash
cd /Users/boris/Desktop/snowflake
python3 -c "
import sys
sys.path.insert(0, 'data/cloud_loaders')
exec(open('data/cloud_loaders/generate_csv_data.py').read())
"
```

This will create:
- `credit_bureau_report.csv` (100K rows)
- `income_verification.csv` (100K rows)

Then:
1. Go to Databricks → Data → sowcatalog → credit_bureau
2. Click "Upload Data"
3. Select CSV files
4. Done! ✅

---

## Quick Fix Script

I'll create a script that generates CSV files. Want me to do that now?

---

## Why This Happens

Unity Catalog requires configured storage credentials because:
1. All managed tables need a storage location
2. Databricks needs permission to write to that storage
3. This is a one-time setup per metastore

**After configuration:** All future table creations will work automatically!

---

## Need Help?

Let me know which option you prefer:
1. ✅ I'll help configure storage credentials (most powerful)
2. ✅ I'll generate CSV files you can upload (quickest)
3. ✅ Create tables manually in SQL Editor then load data

Which would you like to do?
