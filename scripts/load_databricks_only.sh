#!/bin/bash
# ============================================
# Load Data to Databricks ONLY
# Standalone script for Databricks data loading
# ============================================

set -e

echo "======================================================================"
echo "Databricks Credit Bureau Data Loader"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo ""
    echo "Creating .env from your configuration..."
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo ""
fi

echo -e "${GREEN}✅ Found .env configuration${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}[1/3] Installing Python dependencies...${NC}"
cd data/cloud_loaders
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Load Databricks
echo -e "${YELLOW}[2/3] Loading data to Databricks Unity Catalog...${NC}"
echo "Workspace: https://dbc-6730e836-5587.cloud.databricks.com"
echo "Catalog: sowcatalog"
echo "Schema: credit_bureau"
echo ""
echo "This will create 4 managed tables and load 100K records..."
echo ""

# Use Anaconda Python (has all packages installed)
if [ -f "/opt/anaconda3/bin/python3" ]; then
    /opt/anaconda3/bin/python3 load_databricks.py
else
    python3 load_databricks.py
fi

echo ""

# Summary
echo -e "${YELLOW}[3/3] Summary${NC}"
echo "======================================================================"
echo -e "${GREEN}✅ Databricks data loaded successfully!${NC}"
echo "======================================================================"
echo ""
echo "Tables Created:"
echo "  ✅ sowcatalog.credit_bureau.CREDIT_BUREAU_REPORT"
echo "  ✅ sowcatalog.credit_bureau.INCOME_VERIFICATION"
echo "  ✅ sowcatalog.credit_bureau.ALTERNATIVE_DATA"
echo "  ✅ sowcatalog.credit_bureau.FRAUD_INDICATORS"
echo ""
echo "Next Steps:"
echo "  1. Verify in Databricks:"
echo "     - Go to Data → sowcatalog → credit_bureau"
echo "     - Check table counts"
echo ""
echo "  2. Configure Snowflake to read from Unity Catalog:"
echo "     - Update: snowflake/01_connectors/databricks_polaris.sql"
echo "     - Set CATALOG_NAME = 'sowcatalog'"
echo ""
echo "  3. Test query in Databricks:"
echo "     SELECT COUNT(*) FROM sowcatalog.credit_bureau.CREDIT_BUREAU_REPORT;"
echo ""

cd "$PROJECT_ROOT"
