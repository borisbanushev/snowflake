#!/bin/bash
# ============================================
# Deploy All Snowflake Objects
# Run this script after databases are created
# ============================================

set -e

echo "============================================"
echo "Deploying All Snowflake Objects"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SNOWFLAKE_DIR="../snowflake"

# Function to run SQL file
run_sql() {
    echo -e "${YELLOW}Running: $1${NC}"
    snowsql -f "$1"
    echo -e "${GREEN}✓ Completed: $1${NC}"
    echo ""
}

# Setup
echo "Step 1: Database Setup"
run_sql "$SNOWFLAKE_DIR/00_setup/01_create_database.sql"
run_sql "$SNOWFLAKE_DIR/00_setup/02_create_schemas.sql"
run_sql "$SNOWFLAKE_DIR/00_setup/03_create_warehouses.sql"
run_sql "$SNOWFLAKE_DIR/00_setup/04_create_roles.sql"

# Connectors
echo "Step 2: Data Connectors"
echo "⚠️  Update connection strings in connector files before running"
read -p "Press enter to continue or Ctrl+C to cancel..."
run_sql "$SNOWFLAKE_DIR/01_connectors/oracle_openflow.sql"
run_sql "$SNOWFLAKE_DIR/01_connectors/mysql_openflow.sql"
# run_sql "$SNOWFLAKE_DIR/01_connectors/databricks_polaris.sql"  # Uncomment if using Databricks

# Unistore
echo "Step 3: Hybrid Tables (Unistore)"
run_sql "$SNOWFLAKE_DIR/05_unistore/hybrid_tables.sql"

# Governance
echo "Step 4: Governance"
run_sql "$SNOWFLAKE_DIR/08_governance/01_tags.sql"
run_sql "$SNOWFLAKE_DIR/08_governance/02_masking_policies.sql"

echo ""
echo "============================================"
echo "✓ Deployment Complete!"
echo "============================================"
echo ""
echo "Next Steps:"
echo "1. Wait for data to sync via Openflow connectors"
echo "2. Run ML training scripts"
echo "3. Deploy Cortex AI components"
echo "4. Launch Streamlit application"
echo ""
