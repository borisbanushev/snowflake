#!/bin/bash
# ============================================
# Migrate Data from MySQL to PostgreSQL
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

# PostgreSQL destination (will be filled after deployment)
AWS_REGION="ap-southeast-1"
PG_INSTANCE_ID="snowflake-credit-demo-postgres"

echo "======================================================================"
echo "MySQL to PostgreSQL Data Migration"
echo "======================================================================"
echo ""

# Get PostgreSQL endpoint
echo "[1/5] Getting PostgreSQL endpoint..."
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

# Create database
echo "[2/5] Creating PostgreSQL database..."
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d postgres -c "CREATE DATABASE $PG_DB;" 2>/dev/null || echo "Database already exists"
echo "✅ Database ready"
echo ""

# Export MySQL schema and convert to PostgreSQL
echo "[3/5] Exporting MySQL schema..."
mkdir -p /tmp/mysql_to_pg

# Create PostgreSQL schema
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" << 'EOF'
-- Digital Customer Profile
CREATE TABLE IF NOT EXISTS digital_customer_profile (
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

-- Digital Session
CREATE TABLE IF NOT EXISTS digital_session (
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

-- Digital Event
CREATE TABLE IF NOT EXISTS digital_event (
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

# Migrate data using pg_dump/restore or CSV
echo "[4/5] Migrating data (this may take 10-15 minutes)..."

# Export from MySQL to CSV
echo "  Exporting DIGITAL_CUSTOMER_PROFILE..."
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASS" "$MYSQL_DB" \
    -e "SELECT * FROM DIGITAL_CUSTOMER_PROFILE" \
    | sed 's/\t/,/g' | sed 's/NULL//g' > /tmp/mysql_to_pg/customers.csv

echo "  Exporting DIGITAL_SESSION..."
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASS" "$MYSQL_DB" \
    -e "SELECT * FROM DIGITAL_SESSION" \
    | sed 's/\t/,/g' | sed 's/NULL//g' > /tmp/mysql_to_pg/sessions.csv

echo "  Exporting DIGITAL_EVENT..."  
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASS" "$MYSQL_DB" \
    -e "SELECT * FROM DIGITAL_EVENT" \
    | sed 's/\t/,/g' | sed 's/NULL//g' > /tmp/mysql_to_pg/events.csv

echo "✅ Data exported to CSV"
echo ""

# Import to PostgreSQL
echo "[5/5] Importing to PostgreSQL..."

echo "  Importing customers..."
tail -n +2 /tmp/mysql_to_pg/customers.csv | \
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
    -c "\COPY digital_customer_profile FROM STDIN WITH (FORMAT CSV, DELIMITER ',', NULL '')"

echo "  Importing sessions..."
tail -n +2 /tmp/mysql_to_pg/sessions.csv | \
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
    -c "\COPY digital_session FROM STDIN WITH (FORMAT CSV, DELIMITER ',', NULL '')"

echo "  Importing events..."
tail -n +2 /tmp/mysql_to_pg/events.csv | \
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
    -c "\COPY digital_event FROM STDIN WITH (FORMAT CSV, DELIMITER ',', NULL '')"

echo "✅ Data imported"
echo ""

# Verify
echo "Verifying data..."
PGPASSWORD="$PG_PASS" psql -h "$PG_ENDPOINT" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" << 'EOF'
SELECT 'DIGITAL_CUSTOMER_PROFILE' AS table_name, COUNT(*) AS row_count FROM digital_customer_profile
UNION ALL
SELECT 'DIGITAL_SESSION', COUNT(*) FROM digital_session
UNION ALL
SELECT 'DIGITAL_EVENT', COUNT(*) FROM digital_event;
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
