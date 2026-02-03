#!/bin/bash
# ============================================
# Deploy PostgreSQL RDS for Snowflake Openflow
# ============================================

set -e

echo "======================================================================"
echo "PostgreSQL RDS Deployment for Snowflake Openflow"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
AWS_REGION="ap-southeast-1"  # Singapore
DB_INSTANCE_ID="snowflake-credit-demo-postgres"
DB_NAME="digital_banking"
DB_USERNAME="digitaluser"
DB_PASSWORD="DigitalPass123!"
DB_INSTANCE_CLASS="db.t3.small"
ALLOCATED_STORAGE=20
ENGINE_VERSION="16.11"  # PostgreSQL 16 (latest available in ap-southeast-1)

echo "Configuration:"
echo "  Region:          $AWS_REGION"
echo "  Instance ID:     $DB_INSTANCE_ID"
echo "  Database:        $DB_NAME"
echo "  Instance Class:  $DB_INSTANCE_CLASS"
echo "  Storage:         ${ALLOCATED_STORAGE}GB"
echo "  Engine:          PostgreSQL $ENGINE_VERSION"
echo ""

# Check AWS CLI
echo -e "${YELLOW}[1/4] Checking AWS CLI...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    exit 1
fi
echo -e "${GREEN}✅ AWS CLI configured${NC}"
echo ""

# Get security group from existing MySQL setup
echo -e "${YELLOW}[2/4] Checking existing security group...${NC}"
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=snowflake-mysql-sg" \
    --region "$AWS_REGION" \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "")

if [ -z "$SG_ID" ] || [ "$SG_ID" == "None" ]; then
    echo "Creating new security group..."
    DEFAULT_VPC=$(aws ec2 describe-vpcs \
        --filters "Name=is-default,Values=true" \
        --region "$AWS_REGION" \
        --query 'Vpcs[0].VpcId' \
        --output text)
    
    SG_ID=$(aws ec2 create-security-group \
        --group-name "snowflake-postgres-sg" \
        --description "Security group for Snowflake PostgreSQL access" \
        --vpc-id "$DEFAULT_VPC" \
        --region "$AWS_REGION" \
        --query 'GroupId' \
        --output text)
    
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 5432 \
        --cidr 0.0.0.0/0 \
        --region "$AWS_REGION"
fi

echo -e "${GREEN}✅ Security group ready: $SG_ID${NC}"
echo ""

# Check if instance already exists
echo -e "${YELLOW}[3/4] Creating PostgreSQL RDS instance...${NC}"
if aws rds describe-db-instances \
    --db-instance-identifier "$DB_INSTANCE_ID" \
    --region "$AWS_REGION" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Instance $DB_INSTANCE_ID already exists${NC}"
else
    echo "Creating RDS instance..."
    aws rds create-db-instance \
        --db-instance-identifier "$DB_INSTANCE_ID" \
        --db-instance-class "$DB_INSTANCE_CLASS" \
        --engine postgres \
        --engine-version "$ENGINE_VERSION" \
        --master-username "$DB_USERNAME" \
        --master-user-password "$DB_PASSWORD" \
        --allocated-storage "$ALLOCATED_STORAGE" \
        --storage-type gp2 \
        --vpc-security-group-ids "$SG_ID" \
        --publicly-accessible \
        --backup-retention-period 7 \
        --region "$AWS_REGION" \
        --tags Key=Project,Value=SnowflakeDemo Key=Purpose,Value=OpenflowSource
    
    echo ""
    echo "⏳ Waiting for PostgreSQL RDS to be available (10-15 minutes)..."
    aws rds wait db-instance-available \
        --db-instance-identifier "$DB_INSTANCE_ID" \
        --region "$AWS_REGION"
fi

echo -e "${GREEN}✅ PostgreSQL RDS ready${NC}"
echo ""

# Get endpoint
echo -e "${YELLOW}[4/4] Getting PostgreSQL endpoint...${NC}"
POSTGRES_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier "$DB_INSTANCE_ID" \
    --region "$AWS_REGION" \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

POSTGRES_PORT=$(aws rds describe-db-instances \
    --db-instance-identifier "$DB_INSTANCE_ID" \
    --region "$AWS_REGION" \
    --query 'DBInstances[0].Endpoint.Port' \
    --output text)

echo "Endpoint: $POSTGRES_ENDPOINT:$POSTGRES_PORT"
echo ""

echo "======================================================================"
echo -e "${GREEN}🎉 PostgreSQL RDS Deployment Complete!${NC}"
echo "======================================================================"
echo ""
echo "PostgreSQL RDS Details:"
echo "  Endpoint:       $POSTGRES_ENDPOINT"
echo "  Port:           $POSTGRES_PORT"
echo "  Database:       $DB_NAME"
echo "  Username:       $DB_USERNAME"
echo "  Password:       $DB_PASSWORD"
echo ""
echo "JDBC Connection String:"
echo "  jdbc:postgresql://$POSTGRES_ENDPOINT:$POSTGRES_PORT/$DB_NAME"
echo ""
echo "Next Steps:"
echo "  1. Run: ./scripts/migrate_mysql_to_postgres.sh"
echo "     (Migrates data from MySQL to PostgreSQL)"
echo ""
echo "  2. Configure Snowflake Openflow PostgreSQL connector"
echo ""
