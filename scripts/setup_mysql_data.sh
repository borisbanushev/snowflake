#!/bin/bash
# ============================================
# Setup MySQL Digital Banking Data
# ============================================

set -e

echo "======================================================================"
echo "MySQL Digital Banking Data Setup"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if Docker is running
echo -e "${YELLOW}[1/4] Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Check if MySQL container is running
echo -e "${YELLOW}[2/4] Checking MySQL container...${NC}"
if ! docker ps | grep -q mysql-digital; then
    echo -e "${YELLOW}   Starting MySQL container...${NC}"
    cd infrastructure/docker
    docker-compose up -d mysql-digital
    cd ../..
    echo -e "${YELLOW}   Waiting 30 seconds for MySQL to initialize...${NC}"
    sleep 30
fi
echo -e "${GREEN}✅ MySQL container is running${NC}"
echo ""

# Install Python dependencies
echo -e "${YELLOW}[3/4] Installing Python dependencies...${NC}"
cd data/generators
pip install -q mysql-connector-python faker pandas numpy tqdm python-dotenv
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Generate and load data
echo -e "${YELLOW}[4/4] Generating and loading MySQL data...${NC}"
echo "This will take several minutes..."
echo ""

# Use Anaconda Python if available
if [ -f "/opt/anaconda3/bin/python3" ]; then
    /opt/anaconda3/bin/python3 generate_mysql_data.py
else
    python3 generate_mysql_data.py
fi

echo ""
echo "======================================================================"
echo -e "${GREEN}✅ MySQL Data Setup Complete!${NC}"
echo "======================================================================"
echo ""
echo "Database: digital_banking"
echo "Host: localhost:3306"
echo "User: digitaluser"
echo ""
echo "Next Steps:"
echo "  1. Verify data:"
echo "     docker exec -it mysql-digital mysql -udigitaluser -pDigitalPass! digital_banking"
echo "     mysql> SELECT COUNT(*) FROM DIGITAL_CUSTOMER_PROFILE;"
echo ""
echo "  2. Configure Snowflake Openflow connector:"
echo "     snowflake/01_connectors/mysql_openflow.sql"
echo ""

cd ../..
