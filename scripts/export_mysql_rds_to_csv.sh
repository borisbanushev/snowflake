#!/bin/bash
# ============================================
# Export MySQL RDS Data to CSV for Snowflake
# ============================================

set -e

RDS_ENDPOINT="snowflake-credit-demo-mysql.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com"
RDS_PORT="3306"
DB_NAME="digital_banking"
DB_USERNAME="digitaluser"
DB_PASSWORD="DigitalPass123!"
EXPORT_DIR="$(pwd)/data/mysql_rds_export"

echo "======================================================================"
echo "Export MySQL RDS Data to CSV"
echo "======================================================================"
echo ""

# Create export directory
mkdir -p "$EXPORT_DIR"

echo "Exporting to: $EXPORT_DIR"
echo ""

# Export tables
echo "[1/3] Exporting DIGITAL_CUSTOMER_PROFILE (100K rows)..."
mysql -h "$RDS_ENDPOINT" \
      -P "$RDS_PORT" \
      -u "$DB_USERNAME" \
      -p"$DB_PASSWORD" \
      "$DB_NAME" \
      -e "SELECT * FROM DIGITAL_CUSTOMER_PROFILE" \
      | sed 's/\t/,/g' > "$EXPORT_DIR/digital_customer_profile.csv"
      
echo "✅ $(wc -l < "$EXPORT_DIR/digital_customer_profile.csv") rows exported"

echo ""
echo "[2/3] Exporting DIGITAL_SESSION (1M rows)..."
mysql -h "$RDS_ENDPOINT" \
      -P "$RDS_PORT" \
      -u "$DB_USERNAME" \
      -p"$DB_PASSWORD" \
      "$DB_NAME" \
      -e "SELECT * FROM DIGITAL_SESSION" \
      | sed 's/\t/,/g' > "$EXPORT_DIR/digital_session.csv"
      
echo "✅ $(wc -l < "$EXPORT_DIR/digital_session.csv") rows exported"

echo ""
echo "[3/3] Exporting DIGITAL_EVENT (5M rows - may take 2-3 minutes)..."
mysql -h "$RDS_ENDPOINT" \
      -P "$RDS_PORT" \
      -u "$DB_USERNAME" \
      -p"$DB_PASSWORD" \
      "$DB_NAME" \
      -e "SELECT * FROM DIGITAL_EVENT" \
      | sed 's/\t/,/g' > "$EXPORT_DIR/digital_event.csv"
      
echo "✅ $(wc -l < "$EXPORT_DIR/digital_event.csv") rows exported"

echo ""
echo "======================================================================"
echo "🎉 Export Complete!"
echo "======================================================================"
echo ""
echo "Files:"
ls -lh "$EXPORT_DIR"/*.csv
echo ""
echo "Next Steps:"
echo "  1. Run in Snowflake: snowflake/01_connectors/mysql_manual_load.sql"
echo "     (This creates tables and stage)"
echo ""
echo "  2. Upload CSV files via Snowflake UI:"
echo "     - Go to: Data > CREDIT_DECISIONING_DB > RAW_ZONE > MYSQL_SRC > Stages"
echo "     - Click: mysql_upload_stage"
echo "     - Upload: All 3 CSV files"
echo ""
echo "  3. Run COPY INTO commands (in the SQL script)"
echo ""
echo "  OR use the Python upload script (automated):"
echo "  cd $EXPORT_DIR/../.."
echo "  python3 scripts/upload_mysql_to_snowflake.py"
echo ""
