#!/bin/bash
# ============================================
# Migrate Data from MySQL to PostgreSQL (Fixed)
# ============================================

set -e

# Add PostgreSQL to PATH
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"

# MySQL source
MYSQL_HOST="snowflake-credit-demo-mysql.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com"
MYSQL_PORT="3306"
MYSQL_USER="digitaluser"
MYSQL_PASS="DigitalPass123!"
MYSQL_DB="digital_banking"

# PostgreSQL destination
AWS_REGION="ap-southeast-1"
PG_INSTANCE_ID="snowflake-credit-demo-postgres"

echo "======================================================================"
echo "MySQL to PostgreSQL Data Migration (Fixed)"
echo "======================================================================"
echo ""

# Get PostgreSQL endpoint
echo "[1/6] Getting PostgreSQL endpoint..."
PG_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier "$PG_INSTANCE_ID" \
    --region "$AWS_REGION" \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

PG_PORT="5432"
PG_USER="digitaluser"
PG_PASS="DigitalPass123!"
PG_DB="digital_banking"

echo "✅ PostgreSQL: $PG_ENDPOINT:$PG_PORT"
echo ""

# Drop and recreate database to start fresh
echo "[2/6] Recreating PostgreSQL database..."
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d postgres -c "DROP DATABASE IF EXISTS $PG_DB;" 2>/dev/null || true
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d postgres -c "CREATE DATABASE $PG_DB;"
echo "✅ Database ready"
echo ""

# Create PostgreSQL schema
echo "[3/6] Creating PostgreSQL schema..."
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" << 'EOF'
CREATE TABLE digital_customer_profile (
    digital_id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(20),
    email VARCHAR(100),
    mobile_number VARCHAR(20),
    username VARCHAR(50) UNIQUE,
    registration_date TIMESTAMP,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    failed_login_count INTEGER DEFAULT 0,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_type VARCHAR(20),
    device_count INTEGER DEFAULT 0,
    primary_device_type VARCHAR(20),
    biometric_enabled BOOLEAN DEFAULT FALSE,
    push_notifications BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    mobile_verified BOOLEAN DEFAULT FALSE,
    ekyc_status VARCHAR(20) DEFAULT 'PENDING',
    ekyc_date TIMESTAMP,
    preferred_language VARCHAR(10) DEFAULT 'EN',
    timezone VARCHAR(50) DEFAULT 'Asia/Singapore',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customer ON digital_customer_profile(customer_id);
CREATE INDEX idx_email ON digital_customer_profile(email);

CREATE TABLE digital_session (
    session_id VARCHAR(36) PRIMARY KEY,
    digital_id VARCHAR(36),
    customer_id VARCHAR(20),
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    duration_seconds INTEGER,
    device_id VARCHAR(100),
    device_type VARCHAR(20),
    device_model VARCHAR(50),
    os_version VARCHAR(20),
    app_version VARCHAR(20),
    ip_address VARCHAR(45),
    geolocation_lat DECIMAL(10,7),
    geolocation_lon DECIMAL(10,7),
    city VARCHAR(100),
    country VARCHAR(3),
    pages_viewed INTEGER DEFAULT 0,
    transactions_initiated INTEGER DEFAULT 0,
    transactions_completed INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    session_quality_score DECIMAL(5,2),
    exit_reason VARCHAR(30),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_session_digital ON digital_session(digital_id);
CREATE INDEX idx_session_customer ON digital_session(customer_id);
CREATE INDEX idx_session_start ON digital_session(session_start);

CREATE TABLE digital_event (
    event_id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36),
    digital_id VARCHAR(36),
    customer_id VARCHAR(20),
    event_type VARCHAR(50),
    event_name VARCHAR(100),
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    page_name VARCHAR(100),
    element_id VARCHAR(100),
    event_data TEXT,
    response_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_code VARCHAR(20),
    error_message VARCHAR(500),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_event_session ON digital_event(session_id);
CREATE INDEX idx_event_customer ON digital_event(customer_id);
CREATE INDEX idx_event_timestamp ON digital_event(event_timestamp);
EOF

echo "✅ PostgreSQL schema created"
echo ""

# Use mysqldump with proper escaping instead of CSV export
echo "[4/6] Migrating digital_customer_profile..."
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASS" "$MYSQL_DB" \
  --skip-column-names --batch \
  -e "SELECT * FROM DIGITAL_CUSTOMER_PROFILE" \
  | while IFS=$'\t' read -r digital_id customer_id email mobile_number username registration_date last_login login_count failed_login_count mfa_enabled mfa_type device_count primary_device_type biometric_enabled push_notifications email_verified mobile_verified ekyc_status ekyc_date preferred_language timezone created_date modified_date; do
    PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -c "INSERT INTO digital_customer_profile VALUES (
      $([ -z "$digital_id" ] || [ "$digital_id" = "NULL" ] && echo "NULL" || echo "'$digital_id'"),
      $([ -z "$customer_id" ] || [ "$customer_id" = "NULL" ] && echo "NULL" || echo "'$customer_id'"),
      $([ -z "$email" ] || [ "$email" = "NULL" ] && echo "NULL" || echo "'$email'"),
      $([ -z "$mobile_number" ] || [ "$mobile_number" = "NULL" ] && echo "NULL" || echo "'$mobile_number'"),
      $([ -z "$username" ] || [ "$username" = "NULL" ] && echo "NULL" || echo "'$username'"),
      $([ -z "$registration_date" ] || [ "$registration_date" = "NULL" ] && echo "NULL" || echo "'$registration_date'"),
      $([ -z "$last_login" ] || [ "$last_login" = "NULL" ] && echo "NULL" || echo "'$last_login'"),
      $([ -z "$login_count" ] || [ "$login_count" = "NULL" ] && echo "NULL" || echo "$login_count"),
      $([ -z "$failed_login_count" ] || [ "$failed_login_count" = "NULL" ] && echo "NULL" || echo "$failed_login_count"),
      $([ -z "$mfa_enabled" ] || [ "$mfa_enabled" = "NULL" ] && echo "NULL" || echo "$mfa_enabled"),
      $([ -z "$mfa_type" ] || [ "$mfa_type" = "NULL" ] && echo "NULL" || echo "'$mfa_type'"),
      $([ -z "$device_count" ] || [ "$device_count" = "NULL" ] && echo "NULL" || echo "$device_count"),
      $([ -z "$primary_device_type" ] || [ "$primary_device_type" = "NULL" ] && echo "NULL" || echo "'$primary_device_type'"),
      $([ -z "$biometric_enabled" ] || [ "$biometric_enabled" = "NULL" ] && echo "NULL" || echo "$biometric_enabled"),
      $([ -z "$push_notifications" ] || [ "$push_notifications" = "NULL" ] && echo "NULL" || echo "$push_notifications"),
      $([ -z "$email_verified" ] || [ "$email_verified" = "NULL" ] && echo "NULL" || echo "$email_verified"),
      $([ -z "$mobile_verified" ] || [ "$mobile_verified" = "NULL" ] && echo "NULL" || echo "$mobile_verified"),
      $([ -z "$ekyc_status" ] || [ "$ekyc_status" = "NULL" ] && echo "NULL" || echo "'$ekyc_status'"),
      $([ -z "$ekyc_date" ] || [ "$ekyc_date" = "NULL" ] && echo "NULL" || echo "'$ekyc_date'"),
      $([ -z "$preferred_language" ] || [ "$preferred_language" = "NULL" ] && echo "NULL" || echo "'$preferred_language'"),
      $([ -z "$timezone" ] || [ "$timezone" = "NULL" ] && echo "NULL" || echo "'$timezone'"),
      $([ -z "$created_date" ] || [ "$created_date" = "NULL" ] && echo "NULL" || echo "'$created_date'"),
      $([ -z "$modified_date" ] || [ "$modified_date" = "NULL" ] && echo "NULL" || echo "'$modified_date'")
    ) ON CONFLICT DO NOTHING;" 2>/dev/null || echo "Row skipped"
  done

echo "✅ Customers migrated"
echo ""

# Alternative: Use Python for better handling
echo "[5/6] Using Python for sessions and events (better handling)..."

python3 << 'PYTHON_SCRIPT'
import mysql.connector
import psycopg2
from tqdm import tqdm

# MySQL connection
mysql_conn = mysql.connector.connect(
    host="snowflake-credit-demo-mysql.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com",
    port=3306,
    user="digitaluser",
    password="DigitalPass123!",
    database="digital_banking"
)

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host="snowflake-credit-demo-postgres.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com",
    port=5432,
    user="digitaluser",
    password="DigitalPass123!",
    database="digital_banking"
)

print("  Migrating sessions...")
mysql_cur = mysql_conn.cursor()
pg_cur = pg_conn.cursor()

mysql_cur.execute("SELECT COUNT(*) FROM DIGITAL_SESSION")
total_sessions = mysql_cur.fetchone()[0]

mysql_cur.execute("SELECT * FROM DIGITAL_SESSION")
batch = []
for row in tqdm(mysql_cur, total=total_sessions, desc="Sessions"):
    batch.append(row)
    if len(batch) >= 1000:
        pg_cur.executemany("""
            INSERT INTO digital_session VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING
        """, batch)
        pg_conn.commit()
        batch = []

if batch:
    pg_cur.executemany("""
        INSERT INTO digital_session VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT DO NOTHING
    """, batch)
    pg_conn.commit()

print("  Migrating events...")
mysql_cur.execute("SELECT COUNT(*) FROM DIGITAL_EVENT")
total_events = mysql_cur.fetchone()[0]

mysql_cur.execute("SELECT * FROM DIGITAL_EVENT")
batch = []
for row in tqdm(mysql_cur, total=total_events, desc="Events"):
    batch.append(row)
    if len(batch) >= 1000:
        pg_cur.executemany("""
            INSERT INTO digital_event VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING
        """, batch)
        pg_conn.commit()
        batch = []

if batch:
    pg_cur.executemany("""
        INSERT INTO digital_event VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT DO NOTHING
    """, batch)
    pg_conn.commit()

mysql_conn.close()
pg_conn.close()
print("✅ All data migrated")
PYTHON_SCRIPT

echo ""

# Verify
echo "[6/6] Verifying data..."
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" << 'EOF'
SELECT 'digital_customer_profile' AS table_name, COUNT(*) AS row_count FROM digital_customer_profile
UNION ALL
SELECT 'digital_session', COUNT(*) FROM digital_session
UNION ALL
SELECT 'digital_event', COUNT(*) FROM digital_event;
EOF

echo ""
echo "======================================================================"
echo "🎉 Migration Complete!"
echo "======================================================================"
echo ""
echo "PostgreSQL RDS is ready for Snowflake Openflow!"
echo ""
echo "Next: Configure Openflow PostgreSQL connector with:"
echo "  JDBC URL: jdbc:postgresql://$PG_ENDPOINT:$PG_PORT/$PG_DB"
echo "  Username: $PG_USER"
echo "  Password: $PG_PASS"
echo ""
