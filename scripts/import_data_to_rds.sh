#!/bin/bash
# ============================================
# Import MySQL Data to RDS
# ============================================

set -e

RDS_ENDPOINT="snowflake-credit-demo-mysql.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com"
RDS_PORT="3306"
DB_NAME="digital_banking"
DB_USERNAME="digitaluser"
DB_PASSWORD="DigitalPass123!"
DUMP_FILE="/tmp/digital_banking_dump.sql"

echo "======================================================================"
echo "Importing Data to RDS MySQL"
echo "======================================================================"
echo ""
echo "RDS Endpoint: $RDS_ENDPOINT:$RDS_PORT"
echo ""

# Step 1: Create database
echo "[1/4] Creating database on RDS..."
mysql -h "$RDS_ENDPOINT" \
      -P "$RDS_PORT" \
      -u "$DB_USERNAME" \
      -p"$DB_PASSWORD" \
      -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;" 2>&1 | grep -v "Using a password"

echo "✅ Database created"
echo ""

# Step 2: Dump from local MySQL
echo "[2/4] Exporting data from local MySQL..."
docker exec mysql-digital mysqldump \
    -udigitaluser \
    -pDigitalPass! \
    --single-transaction \
    --routines \
    --triggers \
    digital_banking > "$DUMP_FILE" 2>&1

FILE_SIZE=$(ls -lh "$DUMP_FILE" | awk '{print $5}')
echo "✅ Dump created: $FILE_SIZE"
echo ""

# Step 3: Import to RDS
echo "[3/4] Importing data to RDS..."
echo "This may take 5-10 minutes for 6.1M rows..."
echo ""

mysql -h "$RDS_ENDPOINT" \
      -P "$RDS_PORT" \
      -u "$DB_USERNAME" \
      -p"$DB_PASSWORD" \
      "$DB_NAME" < "$DUMP_FILE" 2>&1 | grep -v "Using a password"

echo "✅ Data imported"
echo ""

# Step 4: Verify
echo "[4/4] Verifying data..."
echo ""

PROFILE_COUNT=$(mysql -h "$RDS_ENDPOINT" \
    -P "$RDS_PORT" \
    -u "$DB_USERNAME" \
    -p"$DB_PASSWORD" \
    -N -e "SELECT COUNT(*) FROM digital_banking.DIGITAL_CUSTOMER_PROFILE;" 2>&1 | grep -v "Using a password")

SESSION_COUNT=$(mysql -h "$RDS_ENDPOINT" \
    -P "$RDS_PORT" \
    -u "$DB_USERNAME" \
    -p"$DB_PASSWORD" \
    -N -e "SELECT COUNT(*) FROM digital_banking.DIGITAL_SESSION;" 2>&1 | grep -v "Using a password")

EVENT_COUNT=$(mysql -h "$RDS_ENDPOINT" \
    -P "$RDS_PORT" \
    -u "$DB_USERNAME" \
    -p"$DB_PASSWORD" \
    -N -e "SELECT COUNT(*) FROM digital_banking.DIGITAL_EVENT;" 2>&1 | grep -v "Using a password")

# Check binlog status
BINLOG_FORMAT=$(mysql -h "$RDS_ENDPOINT" \
    -P "$RDS_PORT" \
    -u "$DB_USERNAME" \
    -p"$DB_PASSWORD" \
    -N -e "SHOW VARIABLES LIKE 'binlog_format';" 2>&1 | grep -v "Using a password" | awk '{print $2}')

echo "======================================================================"
echo "🎉 Data Import Complete!"
echo "======================================================================"
echo ""
echo "RDS MySQL Details:"
echo "  Endpoint:       $RDS_ENDPOINT"
echo "  Port:           $RDS_PORT"
echo "  Database:       $DB_NAME"
echo "  Username:       $DB_USERNAME"
echo "  Password:       $DB_PASSWORD"
echo ""
echo "Data Verification:"
echo "  Customer Profiles: ${PROFILE_COUNT:-0}"
echo "  Sessions:          ${SESSION_COUNT:-0}"
echo "  Events:            ${EVENT_COUNT:-0}"
echo ""
echo "CDC Configuration:"
echo "  Binlog Format:     ${BINLOG_FORMAT:-UNKNOWN}"
echo "  Status:            $([ "$BINLOG_FORMAT" = "ROW" ] && echo "✅ Ready for CDC" || echo "⚠️  Needs configuration")"
echo ""
echo "JDBC Connection String:"
echo "  jdbc:mysql://$RDS_ENDPOINT:$RDS_PORT/$DB_NAME"
echo ""
echo "Next Steps:"
echo "  1. Update Snowflake Openflow connector:"
echo "     - Edit: snowflake/01_connectors/mysql_openflow_rds.sql"
echo "     - Replace <RDS_ENDPOINT> with: $RDS_ENDPOINT"
echo "  2. Run the SQL script in Snowflake"
echo "  3. Monitor sync status"
echo ""
