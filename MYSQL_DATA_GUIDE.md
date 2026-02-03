# 🐬 MySQL Digital Banking Data - Setup Guide

## Status

✅ **MySQL Schema Created** - Tables defined in `infrastructure/docker/mysql/init.sql`
✅ **Data Generator Created** - `data/generators/generate_mysql_data.py`
✅ **Setup Script Ready** - `scripts/setup_mysql_data.sh`

---

## 🚀 Quick Setup (One Command)

```bash
cd /Users/boris/Desktop/snowflake
./scripts/setup_mysql_data.sh
```

This will:
1. ✅ Start MySQL Docker container (if not running)
2. ✅ Install Python dependencies
3. ✅ Generate 100K customer profiles
4. ✅ Generate 1M sessions
5. ✅ Generate 5M events
6. ✅ Load all data to MySQL

**Time:** ~10-15 minutes

---

## 📋 What Gets Created

### MySQL Database: `digital_banking`

**4 Tables with realistic data:**

1. **DIGITAL_CUSTOMER_PROFILE** (100,000 rows)
   - Customer IDs matching T24 (CUS-000000 to CUS-099999)
   - Email, mobile, username
   - Login history, MFA settings
   - eKYC status, preferences

2. **DIGITAL_SESSION** (1,000,000 rows)
   - Session tracking
   - Device information
   - IP address, location
   - Session duration and outcome

3. **DIGITAL_EVENT** (5,000,000 rows)
   - User interactions
   - Page views, clicks, transactions
   - Response times
   - Error tracking

4. **DIGITAL_KYC_DOCUMENT** (not populated yet)
   - Document uploads
   - Verification status

---

## 🔧 Manual Setup (Step by Step)

### Step 1: Start MySQL Container

```bash
cd /Users/boris/Desktop/snowflake/infrastructure/docker
docker-compose up -d mysql-digital
```

Wait 30 seconds for MySQL to initialize.

### Step 2: Verify MySQL is Running

```bash
# Check container status
docker ps | grep mysql-digital

# Test connection
docker exec -it mysql-digital mysql -udigitaluser -pDigitalPass! -e "SELECT 'MySQL is ready!' AS status;"
```

### Step 3: Install Python Dependencies

```bash
cd /Users/boris/Desktop/snowflake/data/generators
pip install mysql-connector-python faker pandas numpy tqdm python-dotenv
```

### Step 4: Generate and Load Data

```bash
# Use Anaconda Python (has all packages)
/opt/anaconda3/bin/python3 generate_mysql_data.py

# Or regular Python (if dependencies installed)
python3 generate_mysql_data.py
```

---

## 📊 Expected Output

```
======================================================================
MySQL Digital Banking Data Generator
======================================================================
Host: localhost:3306
Database: digital_banking
======================================================================

✅ Connected to MySQL database
   MySQL Connected!

🎲 Generating sample data...

👥 Generating 100,000 digital customer profiles...
100%|████████████████████████████████████| 100000/100000

🔐 Generating 1,000,000 sessions...
100%|████████████████████████████████████| 1000000/1000000

📱 Generating 5,000,000 digital events...
   This may take a few minutes...
100%|████████████████████████████████████| 50/50

📤 Loading data to MySQL...

📥 Inserting 100,000 rows into DIGITAL_CUSTOMER_PROFILE...
100%|████████████████████████████████████| 100/100
✅ Inserted 100,000 rows

📥 Inserting 1,000,000 rows into DIGITAL_SESSION...
100%|████████████████████████████████████| 1000/1000
✅ Inserted 1,000,000 rows

📥 Inserting 5,000,000 rows into DIGITAL_EVENT...
100%|████████████████████████████████████| 5000/5000
✅ Inserted 5,000,000 rows

======================================================================
🎉 MySQL Data Load Complete!
======================================================================
Customer Profiles: 100,000
Sessions:          1,000,000
Events:            5,000,000

✅ MySQL is ready for Snowflake Openflow CDC ingestion!
```

---

## ✅ Verify Data

### Option 1: MySQL Command Line

```bash
docker exec -it mysql-digital mysql -udigitaluser -pDigitalPass! digital_banking
```

Then run:

```sql
-- Check row counts
SELECT 'DIGITAL_CUSTOMER_PROFILE' AS table_name, COUNT(*) AS rows FROM DIGITAL_CUSTOMER_PROFILE
UNION ALL
SELECT 'DIGITAL_SESSION', COUNT(*) FROM DIGITAL_SESSION
UNION ALL
SELECT 'DIGITAL_EVENT', COUNT(*) FROM DIGITAL_EVENT;

-- Sample customer profiles
SELECT * FROM DIGITAL_CUSTOMER_PROFILE LIMIT 5;

-- Check recent sessions
SELECT 
    CUSTOMER_ID,
    SESSION_TYPE,
    DEVICE_TYPE,
    START_TIME,
    DURATION_SECONDS,
    SESSION_OUTCOME
FROM DIGITAL_SESSION
ORDER BY START_TIME DESC
LIMIT 10;

-- Event statistics
SELECT 
    EVENT_TYPE,
    COUNT(*) as event_count,
    AVG(RESPONSE_TIME_MS) as avg_response_time
FROM DIGITAL_EVENT
GROUP BY EVENT_TYPE
ORDER BY event_count DESC;
```

### Option 2: Quick Query Script

```bash
docker exec -it mysql-digital mysql -udigitaluser -pDigitalPass! digital_banking -e "
SELECT 
    'Customer Profiles' as table_name, 
    COUNT(*) as row_count 
FROM DIGITAL_CUSTOMER_PROFILE
UNION ALL
SELECT 'Sessions', COUNT(*) FROM DIGITAL_SESSION
UNION ALL
SELECT 'Events', COUNT(*) FROM DIGITAL_EVENT;
"
```

---

## 🔗 Connect to Snowflake

After data is loaded, configure Snowflake Openflow connector:

### Update Connection String

Edit: `snowflake/01_connectors/mysql_openflow.sql`

```sql
-- Update with your MySQL endpoint
CONNECTION_STRING = 'jdbc:mysql://localhost:3306/digital_banking'

-- For Docker:
CONNECTION_STRING = 'jdbc:mysql://host.docker.internal:3306/digital_banking'

-- For Cloud MySQL:
CONNECTION_STRING = 'jdbc:mysql://your-mysql-host:3306/digital_banking'
```

### Run in Snowflake

```sql
-- Create connector
!source snowflake/01_connectors/mysql_openflow.sql

-- Verify sync
SELECT * FROM GOVERNANCE.AUDIT.OPENFLOW_CONNECTOR_STATUS
WHERE CONNECTOR_NAME = 'MYSQL_DIGITAL_OPENFLOW_CONNECTOR';

-- Check data in Snowflake
SELECT COUNT(*) FROM RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE;
-- Expected: 100,000
```

---

## 📊 Data Details

### DIGITAL_CUSTOMER_PROFILE (100K)
- **Customer IDs:** CUS-000000 to CUS-099999 (matches T24 data)
- **Email:** Realistic fake emails
- **Mobile:** Phone numbers
- **Username:** Unique usernames
- **Login Activity:** Last 90 days for active users
- **MFA:** 50% enabled
- **eKYC:** 80% verified, 15% pending, 5% failed
- **Languages:** EN, ZH, MS, TA

### DIGITAL_SESSION (1M)
- **Sessions per Customer:** Average 10
- **Time Range:** Last 180 days
- **Device Types:** iOS, Android, Web, Desktop
- **Duration:** 1-30 minutes
- **Outcomes:** 80% success, 5% failed, 15% abandoned
- **Locations:** Singapore, Malaysia, Indonesia, Thailand

### DIGITAL_EVENT (5M)
- **Events per Session:** Average 5
- **Event Types:** 
  - PAGE_VIEW
  - BUTTON_CLICK
  - BALANCE_CHECK
  - TRANSACTION_INIT/CONFIRM
  - PAYMENT, TRANSFER
  - And more...
- **Response Times:** 50-2000ms
- **Success Rate:** 95%
- **Error Rate:** 5%

---

## 🐳 Docker Container Details

**Container Name:** mysql-digital  
**Port:** 3306  
**Database:** digital_banking  
**User:** digitaluser  
**Password:** DigitalPass!

### Useful Docker Commands

```bash
# Start container
docker-compose up -d mysql-digital

# Stop container
docker-compose stop mysql-digital

# View logs
docker logs mysql-digital

# Connect to MySQL
docker exec -it mysql-digital mysql -udigitaluser -pDigitalPass! digital_banking

# Check container status
docker ps | grep mysql-digital

# Restart container
docker-compose restart mysql-digital
```

---

## 🔄 CDC Configuration

### Binary Logging

MySQL is configured for CDC with:
```yaml
command: --binlog-format=ROW --log-bin=mysql-bin
```

This enables Snowflake Openflow to capture changes in real-time.

### Verify Binlog

```sql
-- Check binlog status
SHOW BINARY LOGS;

-- Check binlog format
SHOW VARIABLES LIKE 'binlog_format';
-- Should be: ROW
```

---

## 🚨 Troubleshooting

### "Can't connect to MySQL server"
```bash
# Check if container is running
docker ps | grep mysql-digital

# If not running, start it
cd infrastructure/docker
docker-compose up -d mysql-digital
sleep 30
```

### "Access denied for user"
```bash
# Check credentials in docker-compose.yml
# Default: digitaluser / DigitalPass!

# Reset if needed
docker-compose down
docker volume rm docker_mysql-data
docker-compose up -d mysql-digital
```

### "Table doesn't exist"
```bash
# Check if init.sql ran
docker logs mysql-digital | grep "mysql.user"

# If not, recreate container
docker-compose down
docker volume rm docker_mysql-data
docker-compose up -d mysql-digital
sleep 30
```

### "Python connection fails"
```bash
# Install mysql-connector-python
pip install mysql-connector-python

# Test connection
python3 -c "import mysql.connector; print('✅ Module installed')"
```

### "Data generation is slow"
This is normal! Generating 5M+ records takes time:
- Profiles: 30 seconds
- Sessions: 2-3 minutes
- Events: 5-8 minutes
- Insert: 5-10 minutes

**Total: 10-15 minutes**

---

## 📈 Next Steps

After MySQL data is loaded:

1. ✅ **Verify row counts** (should be 100K, 1M, 5M)

2. ✅ **Configure Snowflake Openflow:**
   - Edit `mysql_openflow.sql` with connection string
   - Run in Snowflake
   - Wait for initial sync

3. ✅ **Check Snowflake:**
   ```sql
   SELECT COUNT(*) FROM RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE;
   SELECT COUNT(*) FROM RAW_ZONE.MYSQL_SRC.DIGITAL_SESSION;
   SELECT COUNT(*) FROM RAW_ZONE.MYSQL_SRC.DIGITAL_EVENT;
   ```

4. ✅ **Monitor CDC:**
   ```sql
   SELECT * FROM GOVERNANCE.AUDIT.OPENFLOW_CONNECTOR_STATUS;
   ```

---

## 🎯 Summary

**Status:**
- ✅ MySQL container configured
- ✅ Schema created (4 tables)
- ✅ Data generator ready
- ✅ Setup script automated

**To Load Data:**
```bash
./scripts/setup_mysql_data.sh
```

**Expected Result:**
- 100,000 customer profiles
- 1,000,000 sessions
- 5,000,000 events
- Ready for Snowflake CDC

**Time:** 10-15 minutes

Ready to go! 🚀
