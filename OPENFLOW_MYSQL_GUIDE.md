# 🔄 Snowflake Openflow for MySQL - Complete Guide

## Overview

This guide walks you through deploying MySQL to AWS RDS and configuring Snowflake Openflow for **real-time CDC (Change Data Capture)** from MySQL to Snowflake.

**Result:** Near real-time sync of MySQL data to Snowflake (every 30 seconds)

---

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   MySQL RDS     │         │  Snowflake       │         │   Snowflake     │
│  (AWS ap-se-1)  │  CDC    │  Openflow        │  Load   │   Tables        │
│                 │ ──────> │  Connector       │ ──────> │  RAW_ZONE.      │
│ • Binlog=ROW    │         │  (Managed)       │         │  MYSQL_SRC      │
│ • Public access │         │                  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

**Benefits:**
- ✅ Real-time data sync (30-second intervals)
- ✅ Full change history (inserts, updates, deletes)
- ✅ Managed by Snowflake (no infrastructure)
- ✅ Production-ready for demos

**Cost:** ~$25/month for db.t3.small RDS instance

---

## 📋 Prerequisites

Before starting, ensure you have:

1. ✅ **AWS CLI installed and configured**
   ```bash
   aws --version
   aws configure  # Enter your AWS credentials
   ```

2. ✅ **MySQL client installed**
   ```bash
   mysql --version
   ```

3. ✅ **Local MySQL data populated** (100K profiles, 1M sessions, 5M events)
   ```bash
   docker exec -it mysql-digital mysql -udigitaluser -pDigitalPass! \
       -e "SELECT COUNT(*) FROM digital_banking.DIGITAL_CUSTOMER_PROFILE;"
   ```

4. ✅ **Snowflake credentials** (in `.env` file)

---

## 🚀 Step-by-Step Setup

### Step 1: Deploy MySQL to AWS RDS

This script creates an RDS MySQL instance in Singapore (same region as your Snowflake):

```bash
cd /Users/boris/Desktop/snowflake
./scripts/deploy_mysql_to_rds.sh
```

**What it does:**
1. Creates RDS MySQL instance (db.t3.small, 20GB storage)
2. Configures binary logging for CDC (binlog_format=ROW)
3. Creates security group for Snowflake access
4. Exports your local MySQL data
5. Imports data to RDS

**Time:** 15-20 minutes (RDS provisioning takes ~10 minutes)

**Output:**
```
RDS Details:
  Endpoint:       snowflake-credit-demo-mysql.abc123.ap-southeast-1.rds.amazonaws.com
  Port:           3306
  Database:       digital_banking
  Username:       digitaluser
  Password:       DigitalPass123!

Connection String:
  jdbc:mysql://snowflake-credit-demo-mysql.abc123.ap-southeast-1.rds.amazonaws.com:3306/digital_banking
```

**Save the endpoint - you'll need it for Snowflake!**

---

### Step 2: Configure Snowflake Openflow Connector

1. **Open the SQL script:**
   ```bash
   open snowflake/01_connectors/mysql_openflow_rds.sql
   ```

2. **Update the RDS endpoint** (line 28):
   ```sql
   CREATE OR REPLACE CONNECTOR RAW_ZONE.MYSQL_DIGITAL_OPENFLOW_CONNECTOR
     TYPE = 'MYSQL'
     CONNECTION_STRING = 'jdbc:mysql://<RDS_ENDPOINT>:3306/digital_banking'  -- ⚠️ UPDATE THIS
     ...
   ```

   Replace `<RDS_ENDPOINT>` with your actual endpoint from Step 1.

3. **Run the script in Snowflake:**
   - Log into Snowflake: https://app.snowflake.com
   - Navigate to **Worksheets**
   - Copy and paste the updated script
   - Execute all statements

**What it does:**
1. Creates secret for MySQL credentials
2. Creates Openflow connector
3. Configures CDC with 30-second refresh
4. Sets up monitoring views

---

### Step 3: Monitor Initial Sync

The initial sync will take **5-15 minutes** to load 6.1M rows.

**Check status:**

```sql
-- Run this in Snowflake every 2-3 minutes
SELECT * FROM GOVERNANCE.AUDIT.OPENFLOW_MYSQL_STATUS;
```

**Expected output:**
```
CONNECTOR_NAME                      | STATUS  | HEALTH_STATUS | RECORDS_PROCESSED
------------------------------------|---------|---------------|-------------------
MYSQL_DIGITAL_OPENFLOW_CONNECTOR    | RUNNING | 🟢 HEALTHY    | 6,100,000
```

**Status indicators:**
- 🟢 **HEALTHY** - Syncing normally (< 2 min lag)
- 🟡 **LAGGING** - Slight delay (2-10 min lag)
- 🟠 **DELAYED** - Significant delay (> 10 min lag)
- 🔴 **ERROR** - Sync failed

---

### Step 4: Verify Data in Snowflake

Once the initial sync completes:

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
```

**Expected:**
```
DIGITAL_CUSTOMER_PROFILE  | 100,000
DIGITAL_SESSION           | 1,000,000
DIGITAL_EVENT             | 5,000,000
```

**Sample data:**
```sql
-- Recent customer profiles
SELECT * FROM DIGITAL_CUSTOMER_PROFILE LIMIT 10;

-- Recent sessions
SELECT * FROM DIGITAL_SESSION ORDER BY SESSION_START DESC LIMIT 10;

-- Recent events
SELECT * FROM DIGITAL_EVENT ORDER BY EVENT_TIMESTAMP DESC LIMIT 10;
```

---

### Step 5: Test CDC (Change Data Capture)

Now let's test real-time sync!

**A. Make a change in MySQL RDS:**

```bash
# Connect to RDS
mysql -h <YOUR_RDS_ENDPOINT> \
      -u digitaluser \
      -pDigitalPass123! \
      digital_banking

# Update a customer's login count
UPDATE DIGITAL_CUSTOMER_PROFILE 
SET LOGIN_COUNT = LOGIN_COUNT + 100,
    LAST_LOGIN = NOW()
WHERE CUSTOMER_ID = 'CUS-000001';

# Exit
exit
```

**B. Wait 30-60 seconds** (for next CDC cycle)

**C. Check in Snowflake:**

```sql
SELECT 
    CUSTOMER_ID,
    USERNAME,
    LOGIN_COUNT,
    LAST_LOGIN
FROM RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE 
WHERE CUSTOMER_ID = 'CUS-000001';
```

**You should see the updated `LOGIN_COUNT` and `LAST_LOGIN`!** 🎉

---

### Step 6: Query Change History

Openflow creates **journal tables** that track every change (insert, update, delete).

```sql
-- List journal tables
SHOW TABLES IN RAW_ZONE.MYSQL_SRC LIKE '%JOURNAL%';

-- Query change history for a customer
SELECT 
    _OPERATION_TYPE,       -- INSERT, UPDATE, DELETE
    _OPERATION_TIMESTAMP,  -- When change occurred
    CUSTOMER_ID,
    LOGIN_COUNT,
    LAST_LOGIN
FROM RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE_JOURNAL
WHERE CUSTOMER_ID = 'CUS-000001'
ORDER BY _OPERATION_TIMESTAMP DESC
LIMIT 20;
```

**Example output:**
```
_OPERATION_TYPE | _OPERATION_TIMESTAMP      | CUSTOMER_ID | LOGIN_COUNT
----------------|---------------------------|-------------|--------------
UPDATE          | 2026-01-31 14:23:45       | CUS-000001  | 142
UPDATE          | 2026-01-31 14:20:12       | CUS-000001  | 42
INSERT          | 2026-01-25 10:15:30       | CUS-000001  | 42
```

---

## 📊 Snowflake Catalog Structure

After Openflow completes, your data appears in:

```
CREDIT_DECISIONING_DB
├── RAW_ZONE
│   ├── MYSQL_SRC ✅ NEW
│   │   ├── DIGITAL_CUSTOMER_PROFILE (100K rows)
│   │   ├── DIGITAL_SESSION (1M rows)
│   │   ├── DIGITAL_EVENT (5M rows)
│   │   ├── DIGITAL_CUSTOMER_PROFILE_JOURNAL (CDC history)
│   │   ├── DIGITAL_SESSION_JOURNAL (CDC history)
│   │   └── DIGITAL_EVENT_JOURNAL (CDC history)
│   ├── ORACLE_SRC (from T24)
│   └── DATABRICKS_SRC (from credit bureau)
```

**All sources visible in one catalog with full lineage!**

---

## 🔍 Monitoring & Maintenance

### Health Check Dashboard

```sql
-- Overall connector health
SELECT * FROM GOVERNANCE.AUDIT.OPENFLOW_MYSQL_STATUS;

-- Detailed sync history
SELECT 
    CONNECTOR_NAME,
    STATUS,
    LAST_SYNC_TIME,
    RECORDS_PROCESSED,
    ERROR_COUNT,
    TIMESTAMPDIFF('MINUTE', LAST_SYNC_TIME, CURRENT_TIMESTAMP()) AS MINUTES_AGO
FROM TABLE(INFORMATION_SCHEMA.CONNECTOR_HISTORY())
WHERE CONNECTOR_NAME = 'MYSQL_DIGITAL_OPENFLOW_CONNECTOR'
ORDER BY LAST_SYNC_TIME DESC
LIMIT 10;
```

### View Logs

```sql
-- Recent connector logs
SELECT 
    EVENT_TIMESTAMP,
    EVENT_TYPE,
    EVENT_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.CONNECTOR_LOGS())
WHERE CONNECTOR_NAME = 'MYSQL_DIGITAL_OPENFLOW_CONNECTOR'
ORDER BY EVENT_TIMESTAMP DESC
LIMIT 50;
```

### Pause/Resume Connector

```sql
-- Pause (stop syncing)
ALTER CONNECTOR RAW_ZONE.MYSQL_DIGITAL_OPENFLOW_CONNECTOR SET ENABLED = FALSE;

-- Resume
ALTER CONNECTOR RAW_ZONE.MYSQL_DIGITAL_OPENFLOW_CONNECTOR SET ENABLED = TRUE;
```

### Adjust Sync Frequency

```sql
-- Change from 30 seconds to 5 minutes
ALTER CONNECTOR RAW_ZONE.MYSQL_DIGITAL_OPENFLOW_CONNECTOR 
SET REFRESH_INTERVAL = '5 MINUTES';

-- Change to 10 seconds (more frequent, higher cost)
ALTER CONNECTOR RAW_ZONE.MYSQL_DIGITAL_OPENFLOW_CONNECTOR 
SET REFRESH_INTERVAL = '10 SECONDS';
```

---

## 🚨 Troubleshooting

### Issue: "Connection timeout"

**Cause:** Snowflake can't reach RDS  
**Fix:** Check security group

```bash
# Get security group ID
SG_ID=$(aws rds describe-db-instances \
    --db-instance-identifier snowflake-credit-demo-mysql \
    --region ap-southeast-1 \
    --query 'DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId' \
    --output text)

# Verify MySQL port (3306) is open
aws ec2 describe-security-groups \
    --group-ids $SG_ID \
    --region ap-southeast-1 \
    --query 'SecurityGroups[0].IpPermissions'

# If not open, add rule:
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 3306 \
    --cidr 0.0.0.0/0 \
    --region ap-southeast-1
```

### Issue: "Authentication failed"

**Cause:** Wrong username/password  
**Fix:** Verify credentials

```bash
# Test connection
mysql -h <RDS_ENDPOINT> -u digitaluser -pDigitalPass123! -e "SELECT 'OK' AS status;"
```

### Issue: "Binlog not enabled"

**Cause:** Binary logging not configured  
**Fix:** Check RDS parameters

```bash
# Check binlog format in MySQL
mysql -h <RDS_ENDPOINT> -u digitaluser -pDigitalPass123! \
    -e "SHOW VARIABLES LIKE 'binlog_format';"

# Should show: binlog_format | ROW
```

If not ROW, re-run deployment script or manually configure parameter group.

### Issue: "Tables not syncing"

**Causes:**
1. Table doesn't have PRIMARY KEY
2. Table name typo (case-sensitive)
3. Unsupported data types

**Fix:** Check table structure

```sql
-- In MySQL:
DESCRIBE DIGITAL_CUSTOMER_PROFILE;

-- Verify PRIMARY KEY exists
SHOW CREATE TABLE DIGITAL_CUSTOMER_PROFILE;
```

### Issue: "Slow initial sync"

**Cause:** Large dataset (6M+ rows)  
**Normal:** Initial sync takes 5-15 minutes  
**Fix (if too slow):**
- Increase Openflow runtime size in Snowflake
- Check network bandwidth

---

## 💰 Cost Breakdown

| Component | Configuration | Monthly Cost |
|-----------|---------------|--------------|
| RDS MySQL | db.t3.small | ~$24 |
| Storage | 20 GB gp2 | ~$2 |
| Backup | 7-day retention | ~$1 |
| Data transfer | < 100 GB/month | Free |
| **Total** | | **~$27/month** |

**Snowflake Costs:**
- Openflow connector: Included (no extra cost)
- ETL_WH usage: ~$0.50/hour when running
- Storage: Standard Snowflake rates

**To minimize costs:**
- Stop RDS when not demoing
- Or delete RDS after demo

---

## 🗑️ Cleanup (When Done)

### Delete RDS Instance

```bash
# Delete RDS instance (no snapshot)
aws rds delete-db-instance \
    --db-instance-identifier snowflake-credit-demo-mysql \
    --skip-final-snapshot \
    --region ap-southeast-1

# Delete security group (wait 5 minutes after RDS deletion)
aws ec2 delete-security-group \
    --group-name snowflake-mysql-sg \
    --region ap-southeast-1

# Delete parameter group
aws rds delete-db-parameter-group \
    --db-parameter-group-name snowflake-mysql-cdc-params \
    --region ap-southeast-1
```

### Remove Connector in Snowflake

```sql
DROP CONNECTOR RAW_ZONE.MYSQL_DIGITAL_OPENFLOW_CONNECTOR;
```

### Keep Data (Optional)

If you want to keep the MySQL data in Snowflake but remove the connector:

```sql
-- Disable connector (stops syncing, keeps data)
ALTER CONNECTOR RAW_ZONE.MYSQL_DIGITAL_OPENFLOW_CONNECTOR SET ENABLED = FALSE;

-- Tables remain in RAW_ZONE.MYSQL_SRC
-- You can query them but they won't update
```

---

## 📈 Next Steps

After MySQL data is syncing to Snowflake:

1. ✅ **Apply Governance**
   ```bash
   snowsql -f snowflake/08_governance/01_tags.sql
   snowsql -f snowflake/08_governance/02_masking_policies.sql
   ```

2. ✅ **Create Bronze/Silver/Gold Transformations**
   ```bash
   snowsql -f snowflake/03_bronze_layer/01_oracle_bronze.sql
   snowsql -f snowflake/03_bronze_layer/02_mysql_bronze.sql
   ```

3. ✅ **Build ML Model**
   ```bash
   cd ml && python train_credit_model.py
   ```

4. ✅ **Launch Streamlit App**
   ```bash
   cd streamlit && streamlit run main.py
   ```

---

## 🎯 Summary

**What You Built:**
- ✅ AWS RDS MySQL with binary logging
- ✅ Snowflake Openflow CDC connector
- ✅ Real-time data sync (every 30 seconds)
- ✅ Full change history tracking
- ✅ 6.1M rows replicated

**Architecture:**
```
MySQL RDS → Openflow CDC → Snowflake RAW_ZONE → Bronze/Silver/Gold → ML/Streamlit
```

**Time:** 20-25 minutes total  
**Cost:** ~$27/month (RDS only)  
**Result:** Production-ready CDC pipeline! 🚀

---

## 📚 References

- [Snowflake Openflow MySQL Connector](https://docs.snowflake.com/en/user-guide/data-integration/openflow/connectors/mysql/about)
- [AWS RDS MySQL Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [MySQL Binary Logging](https://dev.mysql.com/doc/refman/8.0/en/binary-log.html)

---

Ready to deploy? Run:

```bash
./scripts/deploy_mysql_to_rds.sh
```

Let me know when it's complete and I'll help you configure the Openflow connector! 🎯
