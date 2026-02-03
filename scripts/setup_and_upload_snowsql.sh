#!/bin/bash
# SnowSQL Setup and CSV Upload Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 SnowSQL Setup and Upload Script"
echo "===================================="
echo ""

# Find SnowSQL binary
SNOWSQL_BIN=""
if command -v snowsql &> /dev/null; then
    SNOWSQL_BIN="snowsql"
elif [ -f "/Applications/SnowSQL.app/Contents/MacOS/snowsql" ]; then
    SNOWSQL_BIN="/Applications/SnowSQL.app/Contents/MacOS/snowsql"
else
    echo -e "${YELLOW}⚠️  SnowSQL not found. Installing...${NC}"
    echo "This will require your password for sudo."
    echo ""
    
    # Install via Homebrew
    brew install snowflake-snowsql
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Installation failed. Please install manually:${NC}"
        echo "   brew install snowflake-snowsql"
        exit 1
    fi
    
    # Try to find it after installation
    if [ -f "/Applications/SnowSQL.app/Contents/MacOS/snowsql" ]; then
        SNOWSQL_BIN="/Applications/SnowSQL.app/Contents/MacOS/snowsql"
    elif command -v snowsql &> /dev/null; then
        SNOWSQL_BIN="snowsql"
    else
        echo -e "${RED}❌ SnowSQL installed but binary not found. Please add to PATH.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Using SnowSQL: $SNOWSQL_BIN${NC}"
echo ""

# Credentials from .env
SNOWFLAKE_ACCOUNT="MZHGUVK-BC67154"
SNOWFLAKE_USER="ACCOUNTADMIN"
SNOWFLAKE_PASSWORD="L@lolo87Snowflake"
SNOWFLAKE_DATABASE="CREDIT_DECISIONING_DB"
SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
SNOWFLAKE_STAGE="CSV_DATA_STAGE"

# CSV directory
CSV_DIR="/Users/boris/Desktop/snowflake/data/generated_csv"

echo "📋 Configuration:"
echo "   Account: $SNOWFLAKE_ACCOUNT"
echo "   User: $SNOWFLAKE_USER"
echo "   Database: $SNOWFLAKE_DATABASE"
echo "   Warehouse: $SNOWFLAKE_WAREHOUSE"
echo "   Stage: $SNOWFLAKE_STAGE"
echo ""

# Check CSV directory exists
if [ ! -d "$CSV_DIR" ]; then
    echo -e "${RED}❌ CSV directory not found: $CSV_DIR${NC}"
    exit 1
fi

CSV_COUNT=$(find "$CSV_DIR" -name "*.csv" | wc -l | tr -d ' ')
echo "📁 Found $CSV_COUNT CSV files in $CSV_DIR"
echo ""

# Upload all CSV files
echo "📤 Uploading CSV files to Snowflake stage..."
echo ""

cd "$CSV_DIR"

# Upload all CSV files using SnowSQL
# Using external browser authentication for MFA
echo "⚠️  A browser window will open for MFA authentication..."

$SNOWSQL_BIN \
  -a "$SNOWFLAKE_ACCOUNT" \
  -u BORISBB \
  --authenticator externalbrowser \
  -d "$SNOWFLAKE_DATABASE" \
  -w "$SNOWFLAKE_WAREHOUSE" \
  -q "PUT file://*.csv @$SNOWFLAKE_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All CSV files uploaded successfully!${NC}"
    echo ""
    echo "📋 Next step: Run 04_load_all_data.sql in Snowflake UI to load data into tables"
else
    echo ""
    echo -e "${RED}❌ Upload failed. Please check the error above.${NC}"
    exit 1
fi
