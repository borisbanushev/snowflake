# 🔄 MySQL to Snowflake Data Migration Guide

## Current Situation

✅ **MySQL Database Ready**
- 100,000 customer profiles
- 1,000,000 sessions  
- 5,000,000 events
- Running locally in Docker at `localhost:3306`

⚠️ **Network Challenge**
- Snowflake Openflow requires network access to MySQL
- Cannot connect to `localhost` from Snowflake cloud
- Need alternative approach for demo

---

## 🎯 Recommended Solution: Export & Upload

Since your MySQL is running locally, the fastest path is to:
1. Export MySQL data to CSV files
2. Upload CSV files to Snowflake
3. Load into Snowflake tables

**Time:** 5-10 minutes

---

## 🚀 Quick Start (One Command)

```bash
cd /Users/boris/Desktop/snowflake
./scripts/export_mysql_to_snowflake.sh
```

This will:
1. ✅ Export all MySQL tables to CSV
2. ✅ Create Snowflake upload scripts
3. ✅ Prepare Python automation

Then run:

```bash
cd data/mysql_export
python3 upload_via_python.py
```

This will automatically upload and load all data to Snowflake!

---

## 📋 Step-by-Step Process

### Step 1: Export MySQL Data

```bash
cd /Users/boris/Desktop/snowflake
./scripts/export_mysql_to_snowflake.sh
```

**What it does:**
- Exports 3 CSV files from MySQL
- Creates Snowflake SQL scripts
- Prepares Python upload script

**Output location:** `data/mysql_export/`

**Expected files:**
```
digital_customer_profile.csv  (~15 MB)
digital_session.csv           (~150 MB)
digital_event.csv             (~750 MB)
upload_to_snowflake.sql
upload_via_python.py
```

---

### Step 2: Upload to Snowflake

**Option A: Python Script (EASIEST)**

```bash
cd data/mysql_export
python3 upload_via_python.py
```

This will:
1. Connect to Snowflake
2. Create schema `RAW_ZONE.MYSQL_SRC`
3. Create 3 tables
4. Upload CSV files to Snowflake stage
5. Load data into tables
6. Verify row counts

**Time:** 3-5 minutes

---

**Option B: Manual Upload via Snowflake UI**

1. **Run SQL Setup:**
   - Log into Snowflake: https://app.snowflake.com
   - Navigate to Worksheets
   - Open and run: `data/mysql_export/upload_to_snowflake.sql`
   - This creates the tables and stage

2. **Upload CSV Files:**
   ```sql
   -- In Snowflake worksheet:
   USE SCHEMA RAW_ZONE.MYSQL_SRC;
   
   -- Upload files (replace with your local path)
   PUT file:///Users/boris/Desktop/snowflake/data/mysql_export/digital_customer_profile.csv 
       @MYSQL_UPLOAD_STAGE AUTO_COMPRESS=TRUE;
   
   PUT file:///Users/boris/Desktop/snowflake/data/mysql_export/digital_session.csv 
       @MYSQL_UPLOAD_STAGE AUTO_COMPRESS=TRUE;
   
   PUT file:///Users/boris/Desktop/snowflake/data/mysql_export/digital_event.csv 
       @MYSQL_UPLOAD_STAGE AUTO_COMPRESS=TRUE;
   ```

3. **Load Data:**
   ```sql
   -- Copy data from stage to tables
   COPY INTO DIGITAL_CUSTOMER_PROFILE 
   FROM @MYSQL_UPLOAD_STAGE/digital_customer_profile.csv.gz
   ON_ERROR='CONTINUE';
   
   COPY INTO DIGITAL_SESSION 
   FROM @MYSQL_UPLOAD_STAGE/digital_session.csv.gz
   ON_ERROR='CONTINUE';
   
   COPY INTO DIGITAL_EVENT 
   FROM @MYSQL_UPLOAD_STAGE/digital_event.csv.gz
   ON_ERROR='CONTINUE';
   ```

4. **Verify:**
   ```sql
   SELECT COUNT(*) FROM DIGITAL_CUSTOMER_PROFILE; -- Expected: 100,000
   SELECT COUNT(*) FROM DIGITAL_SESSION;          -- Expected: 1,000,000
   SELECT COUNT(*) FROM DIGITAL_EVENT;            -- Expected: 5,000,000
   ```

---

## ✅ Verification Queries

After loading, run these in Snowflake:

```sql
USE SCHEMA RAW_ZONE.MYSQL_SRC;

-- Check row counts
SELECT 
    'DIGITAL_CUSTOMER_PROFILE' AS table_name, 
    COUNT(*) AS row_count 
FROM DIGITAL_CUSTOMER_PROFILE
UNION ALL
SELECT 'DIGITAL_SESSION', COUNT(*) FROM DIGITAL_SESSION
UNION ALL
SELECT 'DIGITAL_EVENT', COUNT(*) FROM DIGITAL_EVENT;

-- Sample customer profiles
SELECT * FROM DIGITAL_CUSTOMER_PROFILE LIMIT 10;

-- Recent sessions
SELECT 
    CUSTOMER_ID,
    DEVICE_TYPE,
    SESSION_START,
    PAGES_VIEWED,
    TRANSACTIONS_COMPLETED
FROM DIGITAL_SESSION
ORDER BY SESSION_START DESC
LIMIT 10;

-- Event statistics
SELECT 
    EVENT_TYPE,
    COUNT(*) as event_count,
    AVG(RESPONSE_TIME_MS) as avg_response_time,
    SUM(CASE WHEN SUCCESS THEN 1 ELSE 0 END) as success_count
FROM DIGITAL_EVENT
GROUP BY EVENT_TYPE
ORDER BY event_count DESC;
```

---

## 📊 Expected Results

| Table | Rows | Size (approx) |
|-------|------|---------------|
| DIGITAL_CUSTOMER_PROFILE | 100,000 | 15 MB |
| DIGITAL_SESSION | 1,000,000 | 150 MB |
| DIGITAL_EVENT | 5,000,000 | 750 MB |
| **Total** | **6,100,000** | **~1 GB** |

---

## 🔍 Catalog Structure in Snowflake

After loading, your data will appear in:

```
CREDIT_DECISIONING_DB
└── RAW_ZONE
    ├── MYSQL_SRC (NEW)
    │   ├── DIGITAL_CUSTOMER_PROFILE
    │   ├── DIGITAL_SESSION
    │   └── DIGITAL_EVENT
    ├── ORACLE_SRC
    └── DATABRICKS_SRC
```

This integrates with your existing architecture and will be visible in:
- Snowflake catalog queries
- Data lineage tracking
- Governance policies

---

## 🔄 Alternative: Deploy MySQL to AWS RDS (For True CDC)

If you want real-time CDC with Openflow, you can:

### 1. Deploy MySQL to AWS RDS

```bash
# Create RDS MySQL instance in same region as Snowflake (ap-southeast-1)
aws rds create-db-instance \
    --db-instance-identifier credit-demo-mysql \
    --db-instance-class db.t3.small \
    --engine mysql \
    --master-username digitaluser \
    --master-user-password DigitalPass! \
    --allocated-storage 20 \
    --publicly-accessible \
    --region ap-southeast-1
```

### 2. Export Local MySQL to RDS

```bash
# Dump from local MySQL
docker exec mysql-digital mysqldump -udigitaluser -pDigitalPass! digital_banking > dump.sql

# Import to RDS
mysql -h your-rds-endpoint.ap-southeast-1.rds.amazonaws.com \
      -udigitaluser -pDigitalPass! digital_banking < dump.sql
```

### 3. Configure Openflow

Update `snowflake/01_connectors/mysql_openflow.sql`:

```sql
CONNECTION_STRING = 'jdbc:mysql://your-rds-endpoint.ap-southeast-1.rds.amazonaws.com:3306/digital_banking'
```

Then run the Openflow connector script in Snowflake.

**Pros:** Real-time CDC, automatic sync every 30 seconds  
**Cons:** AWS costs ($20-50/month), setup complexity  

---

## 🚨 Troubleshooting

### "File not found" during export

```bash
# Ensure MySQL container is running
docker ps | grep mysql-digital

# Check if data exists
docker exec -it mysql-digital mysql -udigitaluser -pDigitalPass! digital_banking -e "SELECT COUNT(*) FROM DIGITAL_CUSTOMER_PROFILE;"
```

### "Permission denied" on export

MySQL might not have permission to write to `/tmp`. Try:

```bash
# Give MySQL write permissions
docker exec -u root mysql-digital chmod 777 /tmp
```

### Python upload fails

```bash
# Install dependencies
pip install snowflake-connector-python python-dotenv

# Check .env file has Snowflake credentials
cat /Users/boris/Desktop/snowflake/.env | grep SNOWFLAKE
```

### "Stage not found"

Run the setup SQL first:

```sql
USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
CREATE SCHEMA IF NOT EXISTS RAW_ZONE.MYSQL_SRC;
-- Then run upload script again
```

---

## 📈 Next Steps

After MySQL data is in Snowflake:

1. ✅ **Verify Data Quality**
   ```sql
   -- Check for duplicates
   SELECT CUSTOMER_ID, COUNT(*) 
   FROM DIGITAL_CUSTOMER_PROFILE 
   GROUP BY CUSTOMER_ID 
   HAVING COUNT(*) > 1;
   
   -- Check for nulls
   SELECT COUNT(*) FROM DIGITAL_SESSION WHERE SESSION_END IS NULL;
   ```

2. ✅ **Apply Governance**
   ```sql
   -- Tag sensitive columns
   ALTER TABLE DIGITAL_CUSTOMER_PROFILE 
   MODIFY COLUMN EMAIL SET TAG GOVERNANCE.TAGS.PII_TYPE = 'EMAIL';
   
   -- Apply masking
   ALTER TABLE DIGITAL_CUSTOMER_PROFILE 
   MODIFY COLUMN EMAIL SET MASKING POLICY GOVERNANCE.POLICIES.MASK_EMAIL;
   ```

3. ✅ **Create Dynamic Tables**
   - Run transformation scripts: `snowflake/03_bronze_layer/*.sql`
   - These will process MySQL data into curated tables

4. ✅ **Test Streamlit App**
   - The app will now have access to digital banking data
   - Run: `cd streamlit && streamlit run main.py`

---

## 💡 Summary

**Current Status:**
- ✅ MySQL local database: 6.1M rows
- ⏳ Snowflake: Waiting for data

**Recommended Action:**
```bash
# 1. Export MySQL data
./scripts/export_mysql_to_snowflake.sh

# 2. Upload to Snowflake (choose one)
cd data/mysql_export && python3 upload_via_python.py
```

**Time:** 10 minutes total  
**Result:** All MySQL data in Snowflake, ready for transformations

---

**Questions?** Check the troubleshooting section or re-run the export script! 🚀
