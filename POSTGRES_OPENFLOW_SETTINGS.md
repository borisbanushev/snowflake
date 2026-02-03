# 🐘 PostgreSQL Openflow Connector - Complete Settings

## 📋 Step-by-Step Configuration

### ✅ Prerequisites
1. Run `./scripts/deploy_postgres_rds.sh` (get PostgreSQL endpoint)
2. Run `./scripts/migrate_mysql_to_postgres.sh` (migrate data)
3. Run SQL in `snowflake/01_connectors/postgres_openflow_rds.sql` (prepare Snowflake)

---

## 🎯 Openflow UI Configuration

### Step 1: Add PostgreSQL Connector
1. In Snowflake Openflow UI, click **"Add Connector"**
2. Search for **"PostgreSQL"**
3. Click **"Install"** (if not already installed)
4. Click **"Configure"**

---

## 📝 All Configuration Parameters

### **SECTION 1: PostgreSQL Source Connection**

Navigate to: **Configure → Parameters → PostgreSQL Connection**

```
Parameter: PostgreSQL Connection URL
Value: jdbc:postgresql://[YOUR-ENDPOINT]:5432/digital_banking
Example: jdbc:postgresql://snowflake-credit-demo-postgres.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com:5432/digital_banking
Note: Replace [YOUR-ENDPOINT] with output from deploy_postgres_rds.sh
```

```
Parameter: PostgreSQL Username
Value: digitaluser
```

```
Parameter: PostgreSQL Password
Value: DigitalPass123!
```

```
Parameter: PostgreSQL Driver Class Name
Value: org.postgresql.Driver
Note: Pre-installed, no upload needed! ✅
```

```
Parameter: Database Driver Location(s)
Value: [LEAVE BLANK]
Note: PostgreSQL JDBC driver is already included in Openflow
```

---

### **SECTION 2: Snowflake Destination**

Navigate to: **Configure → Parameters → Snowflake Connection**

```
Parameter: Snowflake Account
Value: [Auto-filled by Openflow]
```

```
Parameter: Snowflake Database
Value: CREDIT_DECISIONING_DB
```

```
Parameter: Snowflake Schema
Value: POSTGRESQL_SRC
```

```
Parameter: Snowflake Role
Value: BORIS8B_OPENFLOW_ROLE
⚠️ IMPORTANT: Use your specific Openflow role (NOT ACCOUNTADMIN)
Find it: Openflow UI → View Details → Runtime Role
```

```
Parameter: Snowflake Warehouse
Value: COMPUTE_WH
```

```
Parameter: Snowflake Authentication Strategy
Value: SNOWFLAKE_MANAGED_TOKEN
```

---

### **SECTION 3: Ingestion Parameters**

Navigate to: **Configure → Parameters → Ingestion**

```
Parameter: Included Table Names
Value: public.digital_customer_profile,public.digital_session,public.digital_event
Note: PostgreSQL default schema is "public"
```

```
Parameter: Excluded Table Names
Value: [LEAVE BLANK]
```

```
Parameter: Table Name Pattern
Value: .*
(Default regex pattern to match all tables)
```

```
Parameter: Schema Name Pattern
Value: public
```

```
Parameter: Catalog Name Pattern
Value: [LEAVE BLANK]
```

```
Parameter: Initial Load Method
Value: SNAPSHOT
(Full initial load of all data)
```

```
Parameter: CDC Mode
Value: STREAMING
(Enable real-time change data capture)
```

```
Parameter: Merge Task Schedule CRON
Value: * * * * * ?
(Run continuously)
```

```
Parameter: Object Identifier Resolution
Value: CASE_INSENSITIVE_RECOMMENDED
```

```
Parameter: Maximum Table Count
Value: 100
(Default - more than enough for 3 tables)
```

---

### **SECTION 4: Controller Services**

Navigate to: **Controller Services**

#### PostgreSQL Connection Pool

```
Service Name: PostgreSQLConnectionPool
Status: ✅ Enable this service
```

**Connection Properties:**

```
Parameter: Database Connection URL
Value: jdbc:postgresql://[YOUR-ENDPOINT]:5432/digital_banking
```

```
Parameter: Database Driver Class Name
Value: org.postgresql.Driver
```

```
Parameter: Database Driver Location(s)
Value: [LEAVE BLANK - Pre-installed]
```

```
Parameter: Database User
Value: digitaluser
```

```
Parameter: Password
Value: DigitalPass123!
```

```
Parameter: Max Wait Time
Value: 500 millis
```

```
Parameter: Max Total Connections
Value: 8
```

```
Parameter: Validation Query
Value: SELECT 1
```

---

### **SECTION 5: Snowflake Connection Service**

```
Service Name: SnowflakeConnectionService
Status: Should be auto-enabled
```

**Properties:**

```
Parameter: Snowflake URL
Value: [Auto-filled]
```

```
Parameter: Snowflake User
Value: [Auto-filled from managed token]
```

```
Parameter: Snowflake Role
Value: BORIS8B_OPENFLOW_ROLE
```

```
Parameter: Snowflake Database
Value: CREDIT_DECISIONING_DB
```

```
Parameter: Snowflake Schema
Value: POSTGRESQL_SRC
```

```
Parameter: Snowflake Warehouse
Value: COMPUTE_WH
```

---

## ✅ Configuration Checklist

Before clicking "Start":

- [ ] PostgreSQL RDS deployed (`deploy_postgres_rds.sh` completed)
- [ ] Data migrated to PostgreSQL (`migrate_mysql_to_postgres.sh` completed)
- [ ] Snowflake schemas created (`postgres_openflow_rds.sql` executed)
- [ ] PostgreSQL endpoint in Connection URL
- [ ] Username: `digitaluser`
- [ ] Password: `DigitalPass123!`
- [ ] Driver Class: `org.postgresql.Driver`
- [ ] Driver Location: **BLANK** ✅
- [ ] Snowflake Database: `CREDIT_DECISIONING_DB`
- [ ] Snowflake Schema: `POSTGRESQL_SRC`
- [ ] Snowflake Role: `BORIS8B_OPENFLOW_ROLE` (your specific role)
- [ ] Snowflake Warehouse: `COMPUTE_WH`
- [ ] Included Tables: `public.digital_customer_profile,public.digital_session,public.digital_event`
- [ ] PostgreSQL Connection Pool: **ENABLED** ✅
- [ ] Snowflake Connection Service: **ENABLED** ✅

---

## 🚀 Start the Connector

1. Click **"Apply"** to save all settings
2. Click **"Enable"** on all controller services
3. Return to main connector view
4. Click **"Start"** ▶️
5. Monitor the flow - you should see:
   - ✅ Green checkmarks on all processors
   - ✅ Queued rows incrementing
   - ✅ Data flowing to Snowflake

---

## 📊 Expected Data Flow

```
PostgreSQL RDS (AWS)
  ↓
[QueryDatabaseTable] - Initial snapshot load
  ↓
[Snapshot Load] - Full table load (100K + 1M + 5M rows)
  ↓
[CDC Streaming] - Real-time changes
  ↓
Snowflake (CREDIT_DECISIONING_DB.POSTGRESQL_SRC)
```

---

## ✅ Verify in Snowflake

After connector starts successfully:

```sql
USE DATABASE CREDIT_DECISIONING_DB;
USE SCHEMA POSTGRESQL_SRC;

-- Check tables created
SHOW TABLES;

-- Check row counts (should match PostgreSQL)
SELECT COUNT(*) FROM digital_customer_profile; -- 100,000
SELECT COUNT(*) FROM digital_session;          -- 1,000,000  
SELECT COUNT(*) FROM digital_event;            -- 5,000,000

-- Sample data
SELECT * FROM digital_customer_profile LIMIT 10;
```

---

## 🎯 Key Differences from MySQL

| Setting | MySQL | PostgreSQL |
|---------|-------|------------|
| Driver Class | `org.mariadb.jdbc.Driver` | `org.postgresql.Driver` |
| Driver Location | ❌ Required JAR upload | ✅ BLANK (pre-installed) |
| Default Schema | `database_name.table` | `public.table` |
| Port | 3306 | 5432 |
| Setup Complexity | 🔴 High | 🟢 Low |

---

## 🚨 Troubleshooting

### If controller service won't enable:
- Check PostgreSQL endpoint is reachable
- Verify credentials are correct
- Ensure PostgreSQL RDS security group allows inbound on port 5432

### If no data flows:
- Check "Included Table Names" is set
- Verify `BORIS8B_OPENFLOW_ROLE` has correct grants
- Check PostgreSQL tables have data

### If authentication fails:
- Verify using `BORIS8B_OPENFLOW_ROLE` (not `ACCOUNTADMIN`)
- Check grants in Snowflake: `SHOW GRANTS TO ROLE BORIS8B_OPENFLOW_ROLE;`

---

## 📞 Quick Reference

**PostgreSQL RDS:**
- Endpoint: `[from deploy script]`
- Port: `5432`
- Database: `digital_banking`
- User: `digitaluser`
- Password: `DigitalPass123!`

**Snowflake:**
- Database: `CREDIT_DECISIONING_DB`
- Schema: `POSTGRESQL_SRC`
- Role: `BORIS8B_OPENFLOW_ROLE`
- Warehouse: `COMPUTE_WH`

**Tables to Ingest:**
- `public.digital_customer_profile` (100,000 rows)
- `public.digital_session` (1,000,000 rows)
- `public.digital_event` (5,000,000 rows)

---

## 🎉 Success Criteria

✅ All controller services: **Enabled**  
✅ Connector status: **Running**  
✅ Snapshot load: **Completed**  
✅ CDC streaming: **Active**  
✅ Snowflake tables: **3 tables with 6.1M total rows**  

---

**Ready to start? First run:**

```bash
cd /Users/boris/Desktop/snowflake
./scripts/deploy_postgres_rds.sh
```

Then come back to this guide for all the configuration values! 🚀
