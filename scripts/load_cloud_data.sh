#!/bin/bash
# ============================================
# Load Data to Oracle Cloud and Databricks
# ============================================

set -e

echo "======================================================================"
echo "Cloud Data Loader - Oracle Cloud + Databricks"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo ""
    echo "Please create .env file from .env.example:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your credentials"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Found .env configuration${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}[1/4] Installing Python dependencies...${NC}"
cd data/cloud_loaders
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Load Oracle Cloud
echo -e "${YELLOW}[2/4] Loading data to Oracle Cloud...${NC}"
echo "This will create tables and load 100K customers"
echo ""
python3 load_oracle_cloud.py
echo ""

# Load Databricks
echo -e "${YELLOW}[3/4] Loading data to Databricks...${NC}"
echo "This will create Iceberg tables in Unity Catalog"
echo ""
python3 load_databricks.py
echo ""

# Summary
echo -e "${YELLOW}[4/4] Summary${NC}"
echo "======================================================================"
echo -e "${GREEN}✅ All data loaded successfully!${NC}"
echo "======================================================================"
echo ""
echo "Next Steps:"
echo "  1. Update Snowflake connector configs:"
echo "     - snowflake/01_connectors/oracle_openflow.sql"
echo "     - snowflake/01_connectors/databricks_polaris.sql"
echo ""
echo "  2. Run connectors in Snowflake to start CDC:"
echo "     snowsql -f snowflake/01_connectors/oracle_openflow.sql"
echo "     snowsql -f snowflake/01_connectors/databricks_polaris.sql"
echo ""
echo "  3. Verify data flow:"
echo "     SELECT COUNT(*) FROM RAW_ZONE.ORACLE_T24_SRC.T24_CUSTOMER;"
echo "     SELECT COUNT(*) FROM RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT;"
echo ""

cd ../..
