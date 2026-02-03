#!/bin/bash
# ============================================
# Migrate Data from MySQL to PostgreSQL (Simple)
# Uses python with proper libraries
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
echo "MySQL to PostgreSQL Data Migration"
echo "======================================================================"
echo ""

# Get PostgreSQL endpoint
echo "[1/4] Getting PostgreSQL endpoint..."
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

# Drop and recreate database
echo "[2/4] Recreating PostgreSQL database..."
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d postgres -c "DROP DATABASE IF EXISTS $PG_DB;"
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d postgres -c "CREATE DATABASE $PG_DB;"
echo "✅ Database ready"
echo ""

# Create schema
echo "[3/4] Creating PostgreSQL schema..."
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

echo "✅ Schema created"
echo ""

# Migrate using Python (handles all data types properly)
echo "[4/4] Migrating data (10-15 minutes)..."

# Install Python libraries if needed
echo "Installing Python dependencies..."
pip3 install --break-system-packages --quiet mysql-connector-python psycopg2-binary tqdm || {
    echo "⚠️  Pip install failed, trying without --quiet..."
    pip3 install --break-system-packages mysql-connector-python psycopg2-binary tqdm
}

python3 << PYTHON_SCRIPT
import mysql.connector
import psycopg2
import psycopg2.extras
from tqdm import tqdm
import sys

try:
    # MySQL connection
    print("  Connecting to MySQL...")
    mysql_conn = mysql.connector.connect(
        host="$MYSQL_HOST",
        port=$MYSQL_PORT,
        user="$MYSQL_USER",
        password="$MYSQL_PASS",
        database="$MYSQL_DB"
    )

    # PostgreSQL connection
    print("  Connecting to PostgreSQL...")
    pg_conn = psycopg2.connect(
        host="$PG_ENDPOINT",
        port=$PG_PORT,
        user="$PG_USER",
        password="$PG_PASS",
        database="$PG_DB"
    )
    pg_conn.autocommit = False
    
    # Migrate customers
    print("\n  Migrating customers...")
    mysql_cur = mysql_conn.cursor()
    pg_cur = pg_conn.cursor()
    
    mysql_cur.execute("SELECT COUNT(*) FROM DIGITAL_CUSTOMER_PROFILE")
    total = mysql_cur.fetchone()[0]
    
    mysql_cur.execute("SELECT * FROM DIGITAL_CUSTOMER_PROFILE")
    batch = []
    for row in tqdm(mysql_cur, total=total, desc="Customers"):
        # Convert MySQL integers to PostgreSQL booleans
        row_list = list(row)
        # Indices for boolean fields: mfa_enabled(9), biometric_enabled(13), push_notifications(14), email_verified(15), mobile_verified(16)
        for idx in [9, 13, 14, 15, 16]:
            if row_list[idx] is not None:
                row_list[idx] = bool(row_list[idx])
        batch.append(tuple(row_list))
        if len(batch) >= 5000:
            psycopg2.extras.execute_batch(pg_cur,
                "INSERT INTO digital_customer_profile VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                batch)
            pg_conn.commit()
            batch = []
    
    if batch:
        psycopg2.extras.execute_batch(pg_cur,
            "INSERT INTO digital_customer_profile VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
            batch)
        pg_conn.commit()
    
    # Migrate sessions
    print("\n  Migrating sessions...")
    mysql_cur.execute("SELECT COUNT(*) FROM DIGITAL_SESSION")
    total = mysql_cur.fetchone()[0]
    
    mysql_cur.execute("SELECT * FROM DIGITAL_SESSION")
    batch = []
    for row in tqdm(mysql_cur, total=total, desc="Sessions"):
        batch.append(row)
        if len(batch) >= 5000:
            psycopg2.extras.execute_batch(pg_cur,
                "INSERT INTO digital_session VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                batch)
            pg_conn.commit()
            batch = []
    
    if batch:
        psycopg2.extras.execute_batch(pg_cur,
            "INSERT INTO digital_session VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
            batch)
        pg_conn.commit()
    
    # Migrate events
    print("\n  Migrating events...")
    mysql_cur.execute("SELECT COUNT(*) FROM DIGITAL_EVENT")
    total = mysql_cur.fetchone()[0]
    
    mysql_cur.execute("SELECT * FROM DIGITAL_EVENT")
    batch = []
    for row in tqdm(mysql_cur, total=total, desc="Events"):
        # Convert MySQL integer to PostgreSQL boolean for 'success' field (index 11)
        row_list = list(row)
        if row_list[11] is not None:
            row_list[11] = bool(row_list[11])
        batch.append(tuple(row_list))
        if len(batch) >= 5000:
            psycopg2.extras.execute_batch(pg_cur,
                "INSERT INTO digital_event VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                batch)
            pg_conn.commit()
            batch = []
    
    if batch:
        psycopg2.extras.execute_batch(pg_cur,
            "INSERT INTO digital_event VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
            batch)
        pg_conn.commit()
    
    mysql_conn.close()
    pg_conn.close()
    
    print("\n✅ All data migrated successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT

# Verify
echo ""
echo "Verifying data..."
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
echo "PostgreSQL RDS Details:"
echo "  Endpoint: $PG_ENDPOINT"
echo "  Port: $PG_PORT"
echo "  Database: $PG_DB"
echo "  Username: $PG_USER"
echo "  Password: $PG_PASS"
echo ""
echo "JDBC URL for Snowflake Openflow:"
echo "  jdbc:postgresql://$PG_ENDPOINT:$PG_PORT/$PG_DB"
echo ""
