# Snowflake Credit Decisioning Platform

A comprehensive end-to-end credit decisioning platform demonstrating Snowflake's capabilities as a unified enterprise data platform for financial services.

## Features Demonstrated

- **Snowflake Openflow**: Real-time CDC from Oracle T24 and MySQL
- **Apache Polaris Catalog**: Federated access to Databricks Iceberg tables
- **Cortex Agents**: AI-powered credit analyst
- **Cortex Search**: RAG-based policy document retrieval
- **Cortex Analyst**: Natural language to SQL queries
- **Snowflake Intelligence**: Persona-based conversational analytics
- **Unistore (Hybrid Tables)**: OLTP credit application processing
- **Snowpark ML**: XGBoost model training and real-time inference
- **Dynamic Tables**: Declarative data pipelines
- **SnowConvert AI**: T24 PL/SQL to Snowflake migration
- **Horizon Catalog**: Data lineage, classification, and governance
- **Data Masking**: Role-based dynamic PII masking

## Architecture

```
External Sources (Oracle, MySQL, Databricks) 
  → Snowflake (Openflow CDC + Polaris)
    → Data Pipeline (Dynamic Tables)
      → ML (Snowpark)
        → AI Agent (Cortex)
          → Streamlit App
```

## Prerequisites

- Docker Desktop
- Snowflake Enterprise Account (AWS Singapore recommended)
- Python 3.10+
- Databricks workspace (optional, for Polaris demo)

## Quick Start

### 1. Start Local Databases

```bash
cd infrastructure/docker
docker-compose up -d
```

### 2. Generate Sample Data

```bash
pip install -r data/generators/requirements.txt
python data/generators/generate_t24_data.py
python data/generators/generate_digital_data.py
```

### 3. Set Up Snowflake

```bash
# Update snowflake/00_setup/config.sql with your credentials
snowsql -f snowflake/00_setup/01_create_database.sql
snowsql -f snowflake/00_setup/02_create_schemas.sql
# ... run all setup scripts in order
```

### 4. Run Streamlit App

```bash
cd streamlit
pip install -r requirements.txt
streamlit run main.py
```

## Project Structure

```
snowflake-credit-decisioning/
├── infrastructure/        # Docker and Databricks setup
├── snowflake/            # SQL scripts for all Snowflake objects
├── streamlit/            # Streamlit application
├── data/                 # Data generation and policy documents
└── scripts/              # Helper scripts
```

## Implementation Guide

See [implementationplan.md](implementationplan.md) for detailed implementation guide.

## Data Model

- **100,000 customers** across all systems
- **180,000 accounts** in T24 core banking
- **35,000 loans** with payment history
- **5M transactions** for behavior analysis
- **75,000 digital users** with session data

## Demo Script

1. Show data flowing from Oracle/MySQL via Openflow
2. Demonstrate Polaris integration with Databricks
3. Show Customer 360 view with full lineage
4. Submit credit application through Streamlit
5. Watch AI agent evaluate using policies
6. Show ML model real-time scoring
7. Explore natural language queries
8. Demonstrate data masking by role

## License

MIT License - See LICENSE file

## Support

For issues or questions, please open a GitHub issue.
