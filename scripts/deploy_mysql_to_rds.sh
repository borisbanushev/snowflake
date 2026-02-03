#!/bin/bash
# ============================================
# Deploy MySQL to AWS RDS for Snowflake Openflow
# ============================================

set -e

echo "======================================================================"
echo "MySQL to AWS RDS Deployment"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
AWS_REGION="ap-southeast-1"  # Singapore (same as Snowflake)
DB_INSTANCE_ID="snowflake-credit-demo-mysql"
DB_NAME="digital_banking"
DB_USERNAME="digitaluser"
DB_PASSWORD="DigitalPass123!"  # Stronger password for RDS
DB_INSTANCE_CLASS="db.t3.small"  # $0.034/hour (~$25/month)
ALLOCATED_STORAGE=20  # GB
ENGINE_VERSION="8.0.44"  # Latest available in ap-southeast-1

echo "Configuration:"
echo "  Region:          $AWS_REGION"
echo "  Instance ID:     $DB_INSTANCE_ID"
echo "  Database:        $DB_NAME"
echo "  Instance Class:  $DB_INSTANCE_CLASS"
echo "  Storage:         ${ALLOCATED_STORAGE}GB"
echo ""

# Check AWS CLI
echo -e "${YELLOW}[1/5] Checking AWS CLI...${NC}"
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found${NC}"
    echo "Install: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI configured${NC}"
echo ""

# Create RDS instance
echo -e "${YELLOW}[2/5] Creating RDS MySQL instance...${NC}"
echo "This will take 10-15 minutes..."
echo ""

# Check if instance already exists
if aws rds describe-db-instances \
    --db-instance-identifier "$DB_INSTANCE_ID" \
    --region "$AWS_REGION" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Instance $DB_INSTANCE_ID already exists${NC}"
    echo "Skipping creation..."
else
    # Create DB subnet group (if not exists)
    echo "Creating DB subnet group..."
    DEFAULT_VPC=$(aws ec2 describe-vpcs \
        --filters "Name=is-default,Values=true" \
        --region "$AWS_REGION" \
        --query 'Vpcs[0].VpcId' \
        --output text)
    
    SUBNET_IDS=$(aws ec2 describe-subnets \
        --filters "Name=vpc-id,Values=$DEFAULT_VPC" \
        --region "$AWS_REGION" \
        --query 'Subnets[*].SubnetId' \
        --output text)
    
    SUBNET_ARRAY=($SUBNET_IDS)
    
    aws rds create-db-subnet-group \
        --db-subnet-group-name "snowflake-demo-subnet-group" \
        --db-subnet-group-description "Subnet group for Snowflake demo" \
        --subnet-ids ${SUBNET_ARRAY[@]} \
        --region "$AWS_REGION" 2>/dev/null || echo "Subnet group exists"
    
    # Create security group
    echo "Creating security group..."
    SG_ID=$(aws ec2 create-security-group \
        --group-name "snowflake-mysql-sg" \
        --description "Security group for Snowflake MySQL access" \
        --vpc-id "$DEFAULT_VPC" \
        --region "$AWS_REGION" \
        --query 'GroupId' \
        --output text 2>/dev/null || \
        aws ec2 describe-security-groups \
            --filters "Name=group-name,Values=snowflake-mysql-sg" \
            --region "$AWS_REGION" \
            --query 'SecurityGroups[0].GroupId' \
            --output text)
    
    # Allow MySQL access from anywhere (for demo - restrict in production)
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 3306 \
        --cidr 0.0.0.0/0 \
        --region "$AWS_REGION" 2>/dev/null || echo "Ingress rule exists"
    
    # Create RDS instance
    echo "Creating RDS instance..."
    aws rds create-db-instance \
        --db-instance-identifier "$DB_INSTANCE_ID" \
        --db-instance-class "$DB_INSTANCE_CLASS" \
        --engine mysql \
        --engine-version "$ENGINE_VERSION" \
        --master-username "$DB_USERNAME" \
        --master-user-password "$DB_PASSWORD" \
        --allocated-storage "$ALLOCATED_STORAGE" \
        --storage-type gp2 \
        --vpc-security-group-ids "$SG_ID" \
        --db-subnet-group-name "snowflake-demo-subnet-group" \
        --publicly-accessible \
        --backup-retention-period 7 \
        --preferred-backup-window "03:00-04:00" \
        --preferred-maintenance-window "mon:04:00-mon:05:00" \
        --enable-cloudwatch-logs-exports '["error","general","slowquery"]' \
        --region "$AWS_REGION" \
        --tags Key=Project,Value=SnowflakeDemo Key=Purpose,Value=OpenflowSource
    
    echo ""
    echo "⏳ Waiting for RDS instance to be available..."
    echo "   This typically takes 10-15 minutes"
    echo ""
    
    aws rds wait db-instance-available \
        --db-instance-identifier "$DB_INSTANCE_ID" \
        --region "$AWS_REGION"
fi

echo -e "${GREEN}✅ RDS instance ready${NC}"
echo ""

# Get endpoint
echo -e "${YELLOW}[3/5] Getting RDS endpoint...${NC}"
RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier "$DB_INSTANCE_ID" \
    --region "$AWS_REGION" \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

RDS_PORT=$(aws rds describe-db-instances \
    --db-instance-identifier "$DB_INSTANCE_ID" \
    --region "$AWS_REGION" \
    --query 'DBInstances[0].Endpoint.Port' \
    --output text)

echo "Endpoint: $RDS_ENDPOINT:$RDS_PORT"
echo ""

# Enable binary logging for CDC
echo -e "${YELLOW}[4/5] Configuring binary logging for CDC...${NC}"

# Create parameter group if not exists
PARAM_GROUP_NAME="snowflake-mysql-cdc-params"

if ! aws rds describe-db-parameter-groups \
    --db-parameter-group-name "$PARAM_GROUP_NAME" \
    --region "$AWS_REGION" &> /dev/null; then
    
    echo "Creating parameter group..."
    aws rds create-db-parameter-group \
        --db-parameter-group-name "$PARAM_GROUP_NAME" \
        --db-parameter-group-family mysql8.0 \
        --description "Parameter group for Snowflake Openflow CDC" \
        --region "$AWS_REGION"
    
    # Configure binlog parameters
    aws rds modify-db-parameter-group \
        --db-parameter-group-name "$PARAM_GROUP_NAME" \
        --parameters \
            "ParameterName=binlog_format,ParameterValue=ROW,ApplyMethod=immediate" \
            "ParameterName=binlog_row_image,ParameterValue=FULL,ApplyMethod=immediate" \
            "ParameterName=log_bin_trust_function_creators,ParameterValue=1,ApplyMethod=immediate" \
        --region "$AWS_REGION"
    
    # Apply parameter group to instance
    aws rds modify-db-instance \
        --db-instance-identifier "$DB_INSTANCE_ID" \
        --db-parameter-group-name "$PARAM_GROUP_NAME" \
        --apply-immediately \
        --region "$AWS_REGION"
    
    echo "⏳ Waiting for parameter group to apply..."
    sleep 30
    
    # Reboot to apply changes
    echo "Rebooting instance to apply changes..."
    aws rds reboot-db-instance \
        --db-instance-identifier "$DB_INSTANCE_ID" \
        --region "$AWS_REGION"
    
    aws rds wait db-instance-available \
        --db-instance-identifier "$DB_INSTANCE_ID" \
        --region "$AWS_REGION"
fi

echo -e "${GREEN}✅ Binary logging configured${NC}"
echo ""

# Export local MySQL data to RDS
echo -e "${YELLOW}[5/5] Exporting local MySQL data to RDS...${NC}"
echo ""

# Dump from local MySQL
DUMP_FILE="/tmp/digital_banking_dump.sql"
echo "Creating database dump from local MySQL..."
docker exec mysql-digital mysqldump \
    -udigitaluser \
    -pDigitalPass! \
    --single-transaction \
    --routines \
    --triggers \
    digital_banking > "$DUMP_FILE"

FILE_SIZE=$(ls -lh "$DUMP_FILE" | awk '{print $5}')
echo "✅ Dump created: $FILE_SIZE"
echo ""

# Create database on RDS
echo "Creating database on RDS..."
mysql -h "$RDS_ENDPOINT" \
      -P "$RDS_PORT" \
      -u "$DB_USERNAME" \
      -p"$DB_PASSWORD" \
      -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"

# Import to RDS
echo "Importing data to RDS..."
echo "This may take 5-10 minutes..."
mysql -h "$RDS_ENDPOINT" \
      -P "$RDS_PORT" \
      -u "$DB_USERNAME" \
      -p"$DB_PASSWORD" \
      "$DB_NAME" < "$DUMP_FILE"

echo -e "${GREEN}✅ Data imported to RDS${NC}"
echo ""

# Verify
echo "Verifying data..."
PROFILE_COUNT=$(mysql -h "$RDS_ENDPOINT" -P "$RDS_PORT" -u "$DB_USERNAME" -p"$DB_PASSWORD" -N -e "SELECT COUNT(*) FROM digital_banking.DIGITAL_CUSTOMER_PROFILE;")
SESSION_COUNT=$(mysql -h "$RDS_ENDPOINT" -P "$RDS_PORT" -u "$DB_USERNAME" -p"$DB_PASSWORD" -N -e "SELECT COUNT(*) FROM digital_banking.DIGITAL_SESSION;")
EVENT_COUNT=$(mysql -h "$RDS_ENDPOINT" -P "$RDS_PORT" -u "$DB_USERNAME" -p"$DB_PASSWORD" -N -e "SELECT COUNT(*) FROM digital_banking.DIGITAL_EVENT;")

echo ""
echo "======================================================================"
echo -e "${GREEN}🎉 MySQL RDS Deployment Complete!${NC}"
echo "======================================================================"
echo ""
echo "RDS Details:"
echo "  Endpoint:       $RDS_ENDPOINT"
echo "  Port:           $RDS_PORT"
echo "  Database:       $DB_NAME"
echo "  Username:       $DB_USERNAME"
echo "  Password:       $DB_PASSWORD"
echo ""
echo "Data Verification:"
echo "  Customer Profiles: $PROFILE_COUNT"
echo "  Sessions:          $SESSION_COUNT"
echo "  Events:            $EVENT_COUNT"
echo ""
echo "Connection String:"
echo "  jdbc:mysql://$RDS_ENDPOINT:$RDS_PORT/$DB_NAME"
echo ""
echo "Next Steps:"
echo "  1. Update Snowflake Openflow connector configuration"
echo "  2. Run: snowflake/01_connectors/mysql_openflow_rds.sql"
echo ""
echo "Monthly Cost: ~\$25 USD (db.t3.small + 20GB storage)"
echo ""
echo "To delete when done:"
echo "  aws rds delete-db-instance --db-instance-identifier $DB_INSTANCE_ID --skip-final-snapshot --region $AWS_REGION"
echo ""
