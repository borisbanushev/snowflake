# 🐘 PostgreSQL + Snowflake Openflow Setup Guide

## Why PostgreSQL Instead of MySQL?

✅ **PostgreSQL JDBC driver** is often pre-installed in Openflow  
✅ **No JAR file upload** required  
✅ **Better Openflow support** and documentation  
✅ **Same CDC capabilities** as MySQL  

---

## 🚀 Quick Setup (3 Commands)

### Step 1: Deploy PostgreSQL RDS (15 minutes)
```bash
cd /Users/boris/Desktop/snowflake
./scripts/deploy_postgres_rds.sh
```

**What it does:**
- Creates PostgreSQL 16 RDS in Singapore
- Configures security groups
- Enables logical replication for CDC

**Time:** 10-15 minutes

### Step 2: Migrate Data from MySQL to PostgreSQL (10 minutes)
```bash
./scripts/migrate_mysql_to_postgres.sh
```

**What it does:**
- Exports 6.1M rows from MySQL RDS
- Creates PostgreSQL schema
- Imports all data to PostgreSQL
- Verifies row counts

**Time:** 10-15 minutes

### Step 3: Configure Openflow PostgreSQL Connector (5 minutes)

In Snowflake Openflow UI:
1. Add **"PostgreSQL"** connector from catalog
2. Configure parameters (see below)
3. Start the connector

---

## 📋 Openflow PostgreSQL Configuration

After deploying PostgreSQL, configure these parameters in Openflow:

### **PostgreSQL Source Parameters:**

```
PostgreSQL Connection URL:
jdbc:postgresql://snowflake-credit-demo-postgres.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com:5432/digital_banking

PostgreSQL Username:
digitaluser

PostgreSQL Password:
DigitalPass123!

Database Driver Class Name:
org.postgresql.Driver

Database Driver Location:
(Leave blank - driver is pre-installed in Openflow)
```

### **PostgreSQL Destination Parameters:**

```
Destination Database:
CREDIT_DECISIONING_DB

Snowflake Role:
BORIS8B_OPENFLOW_ROLE

Snowflake Warehouse:
COMPUTE_WH

Snowflake Authentication Strategy:
SNOWFLAKE_MANAGED_TOKEN
```

### **PostgreSQL Ingestion Parameters:**

```
Included Table Names:
public.digital_customer_profile,public.digital_session,public.digital_event

Merge Task Schedule CRON:
* * * * * ?

Object Identifier Resolution:
CASE_INSENSITIVE_RECOMMENDED
```

---

## ✅ Advantages Over MySQL

| Feature | MySQL | PostgreSQL |
|---------|-------|------------|
| JDBC Driver | ❌ Manual upload required | ✅ Pre-installed |
| Setup Complexity | ❌ Complex | ✅ Simple |
| Openflow Support | ⚠️ Good | ✅ Excellent |
| CDC Capability | ✅ Yes | ✅ Yes |
| Performance | ✅ Good | ✅ Good |

---

## 🎯 Complete Process

### Phase 1: Deploy PostgreSQL
```bash
./scripts/deploy_postgres_rds.sh
```
**Output:** PostgreSQL RDS endpoint

### Phase 2: Migrate Data
```bash
./scripts/migrate_mysql_to_postgres.sh
```
**Output:** 6.1M rows migrated

### Phase 3: Configure Openflow
1. In Openflow UI → Add connector → PostgreSQL
2. Fill in parameters (above)
3. No driver upload needed! ✅
4. Start connector

### Phase 4: Verify in Snowflake
```sql
USE DATABASE CREDIT_DECISIONING_DB;
USE SCHEMA POSTGRESQL_SRC;

SELECT COUNT(*) FROM digital_customer_profile; -- 100,000
SELECT COUNT(*) FROM digital_session;          -- 1,000,000
SELECT COUNT(*) FROM digital_event;            -- 5,000,000
```

---

## 💰 Cost

Same as MySQL RDS:
- **PostgreSQL RDS:** ~$27/month (db.t3.small)
- **Snowflake Openflow:** Included
- **Total:** ~$27/month

---

## 🔄 Comparison to MySQL Approach

**MySQL (Current Issue):**
- ❌ Stuck on JDBC driver upload
- ❌ Complex configuration
- ⏱️ Still troubleshooting

**PostgreSQL (New Approach):**
- ✅ No driver issues
- ✅ Simpler setup
- ⏱️ 30 minutes total

---

## 🚨 Prerequisites

Make sure you have:
- ✅ AWS CLI configured
- ✅ PostgreSQL client installed:
  ```bash
  brew install postgresql
  ```

---

## 📊 Expected Timeline

| Step | Time | Status |
|------|------|--------|
| Deploy PostgreSQL RDS | 15 min | ⏳ |
| Migrate MySQL → PostgreSQL | 15 min | ⏳ |
| Configure Openflow | 5 min | ⏳ |
| Initial CDC sync | 10 min | ⏳ |
| **Total** | **45 min** | Ready! |

---

## 🎯 Decision

**Recommendation:** Switch to PostgreSQL

**Reasons:**
1. ✅ No JDBC driver upload hassles
2. ✅ Better Openflow support
3. ✅ Faster setup
4. ✅ Same functionality as MySQL

---

## 🚀 Ready to Start?

Run the first command:

```bash
cd /Users/boris/Desktop/snowflake
./scripts/deploy_postgres_rds.sh
```

This will deploy PostgreSQL RDS and give you the endpoint for the next steps!

Let me know when it completes! 🚀
