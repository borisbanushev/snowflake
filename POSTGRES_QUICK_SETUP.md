# 🚀 PostgreSQL Openflow - Quick Setup Card

## 3-Step Process

### Step 1: Deploy PostgreSQL RDS (15 min)
```bash
cd /Users/boris/Desktop/snowflake
./scripts/deploy_postgres_rds.sh
```
**Save the endpoint URL that appears at the end!**

---

### Step 2: Migrate Data (15 min)
```bash
./scripts/migrate_mysql_to_postgres.sh
```

---

### Step 3: Configure Openflow (5 min)

#### A. Run Snowflake SQL
Execute: `snowflake/01_connectors/postgres_openflow_rds.sql`

#### B. Configure in Openflow UI

**PostgreSQL Source:**
```
Connection URL: jdbc:postgresql://[YOUR-ENDPOINT]:5432/digital_banking
Username: digitaluser
Password: DigitalPass123!
Driver Class: org.postgresql.Driver
Driver Location: [LEAVE BLANK] ✅
```

**Snowflake Destination:**
```
Database: CREDIT_DECISIONING_DB
Schema: POSTGRESQL_SRC
Role: BORIS8B_OPENFLOW_ROLE
Warehouse: COMPUTE_WH
Auth: SNOWFLAKE_MANAGED_TOKEN
```

**Tables to Ingest:**
```
public.digital_customer_profile,public.digital_session,public.digital_event
```

#### C. Enable Controller Services
1. PostgreSQL Connection Pool → **Enable**
2. Snowflake Connection Service → Should auto-enable

#### D. Start Connector
Click **Start** ▶️

---

## 🎯 Copy-Paste Values

### PostgreSQL JDBC URL Template
```
jdbc:postgresql://YOUR-ENDPOINT-HERE:5432/digital_banking
```

### Included Table Names (exact format)
```
public.digital_customer_profile,public.digital_session,public.digital_event
```

---

## ✅ Success Check

After ~10 minutes, run in Snowflake:
```sql
USE DATABASE CREDIT_DECISIONING_DB;
USE SCHEMA POSTGRESQL_SRC;

SELECT COUNT(*) FROM digital_customer_profile; -- 100,000
SELECT COUNT(*) FROM digital_session;          -- 1,000,000
SELECT COUNT(*) FROM digital_event;            -- 5,000,000
```

---

**📚 For detailed settings, see:** `POSTGRES_OPENFLOW_SETTINGS.md`

**🚀 Start now:**
```bash
./scripts/deploy_postgres_rds.sh
```
