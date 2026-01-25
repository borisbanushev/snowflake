#!/bin/bash
# ============================================
# Snowflake Credit Decisioning Platform Setup
# ============================================

set -e  # Exit on error

echo "============================================"
echo "Snowflake Credit Decisioning Platform Setup"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
echo -e "${YELLOW}[1/8] Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker Desktop${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Start Docker containers
echo -e "${YELLOW}[2/8] Starting Oracle and MySQL containers...${NC}"
cd infrastructure/docker
docker-compose up -d
echo -e "${GREEN}✓ Containers started${NC}"
echo ""

# Wait for databases to be ready
echo -e "${YELLOW}[3/8] Waiting for databases to initialize (60 seconds)...${NC}"
sleep 60
echo -e "${GREEN}✓ Databases should be ready${NC}"
echo ""

# Install Python dependencies for data generation
echo -e "${YELLOW}[4/8] Installing Python dependencies...${NC}"
cd ../../data/generators
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Generate sample data
echo -e "${YELLOW}[5/8] Generating sample data...${NC}"
echo "This will take several minutes..."
python3 generate_t24_data.py
echo -e "${GREEN}✓ Sample data generated${NC}"
echo ""

# Note about Snowflake setup
echo -e "${YELLOW}[6/8] Snowflake Setup Required${NC}"
echo "Please run the following SQL scripts in your Snowflake account:"
echo "  1. snowflake/00_setup/01_create_database.sql"
echo "  2. snowflake/00_setup/02_create_schemas.sql"
echo "  3. snowflake/00_setup/03_create_warehouses.sql"
echo "  4. snowflake/00_setup/04_create_roles.sql"
echo ""
echo "Then configure connectors:"
echo "  5. snowflake/01_connectors/oracle_openflow.sql"
echo "  6. snowflake/01_connectors/mysql_openflow.sql"
echo "  7. snowflake/01_connectors/databricks_polaris.sql (if using Databricks)"
echo ""
read -p "Press enter when Snowflake setup is complete..."
echo ""

# Install Streamlit dependencies
echo -e "${YELLOW}[7/8] Installing Streamlit dependencies...${NC}"
cd ../../streamlit
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Streamlit dependencies installed${NC}"
echo ""

# Summary
echo -e "${YELLOW}[8/8] Setup Complete!${NC}"
echo ""
echo "============================================"
echo "✓ All Setup Steps Completed"
echo "============================================"
echo ""
echo "Next Steps:"
echo "  1. Configure Snowflake connection in Streamlit"
echo "  2. Run: cd streamlit && streamlit run main.py"
echo "  3. Open browser to http://localhost:8501"
echo ""
echo "Docker Services:"
echo "  - Oracle T24: localhost:1521 (user: t24user, pass: T24UserPass!)"
echo "  - MySQL Digital: localhost:3306 (user: digitaluser, pass: DigitalPass!)"
echo ""
echo "To stop services: cd infrastructure/docker && docker-compose down"
echo ""
