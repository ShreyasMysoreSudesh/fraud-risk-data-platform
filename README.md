# Fraud Risk Data Platform

A portfolio-grade data engineering project that simulates a financial transaction platform for batch processing, streaming, fraud analytics, data quality, orchestration, and machine learning.

The project is being built incrementally to demonstrate production-style data engineering patterns across Python, Google Cloud, Apache Beam/Dataflow, BigQuery, Airflow, dbt, Great Expectations, Kafka, PySpark, Terraform, CI/CD, and BI.

---

## Project Objective

The goal of this project is to design and build an end-to-end data platform capable of processing large-scale synthetic financial transaction data.

The platform is designed to demonstrate:

* Batch data ingestion
* Streaming data ingestion
* Data validation and quality controls
* Dimensional modeling
* Incremental processing
* Infrastructure as Code
* Pipeline orchestration
* Fraud feature engineering
* Machine learning workflows
* Monitoring and observability
* Cloud data warehousing
* CI/CD

The project uses fully synthetic data and does not contain proprietary or employer data.

---

## Current Architecture

```text
                    Synthetic Data Generator
                              |
                  +-----------+-----------+
                  |                       |
                  v                       v
             Batch Pipeline          Streaming Pipeline
                  |                       |
                  v                       v
           Google Cloud Storage          Kafka
                  |                       |
                  v                       v
          Apache Beam / Dataflow        PySpark
                  |                       |
                  +-----------+-----------+
                              |
                              v
                           BigQuery
                              |
                     +--------+--------+
                     |                 |
                    dbt         Great Expectations
                     |
                     v
                Feature Tables
                     |
                     v
                 BigQuery ML
                     |
                     v
                  Power BI
```

Airflow will orchestrate batch workflows.

Terraform will manage Google Cloud infrastructure.

GitHub Actions will provide CI/CD.

---

## Technology Stack

### Programming

* Python
* SQL

### Data Engineering

* Apache Beam
* Google Cloud Dataflow
* Apache Kafka
* PySpark Structured Streaming
* Apache Airflow
* dbt
* Great Expectations

### Cloud

* Google Cloud Storage
* BigQuery
* GCP Dataflow

### Infrastructure & DevOps

* Terraform
* Git
* GitHub
* GitHub Actions
* Docker

### Data Formats

* JSONL
* Apache Parquet

### Machine Learning

* BigQuery ML
* Fraud feature engineering

### Visualization

* Power BI

---

## Project Status

### Phase 1 — Synthetic Data Platform

Completed.

Implemented:

* Pydantic data models
* Schema validation
* Business-rule validation
* Synthetic customer generation
* Synthetic merchant generation
* Synthetic device generation
* Synthetic financial transaction generation
* Deterministic random data generation
* Fraud probability simulation
* Batch-based transaction generation
* JSONL output
* Parquet output
* CLI-based dataset generation
* Unit testing with pytest
* Code quality checks with Ruff
* Large-scale performance benchmarking

### Phase 2 — Google Cloud Infrastructure

In progress.

Planned:

* Terraform-based GCP infrastructure
* Google Cloud Storage raw-data bucket
* BigQuery raw dataset
* Parquet upload to GCS
* BigQuery ingestion

### Phase 3 — Batch Pipeline

Planned:

* Apache Beam
* Google Cloud Dataflow
* Schema validation
* Dead-letter handling
* Batch ingestion into BigQuery

### Phase 4 — Analytics Engineering & Data Quality

Planned:

* dbt transformations
* Raw → Staging → Curated architecture
* Dimensional modeling
* SCD Type 2
* Great Expectations
* Data-quality monitoring

### Phase 5 — Orchestration

Planned:

* Apache Airflow
* DAG-based pipeline orchestration
* Retry logic
* Failure handling
* Pipeline monitoring

### Phase 6 — Streaming

Planned:

* Apache Kafka
* PySpark Structured Streaming
* Event-time processing
* Checkpointing
* Deduplication
* Late-arriving event handling

### Phase 7 — Machine Learning

Planned:

* Fraud feature engineering
* Feature tables
* BigQuery ML
* Fraud classification
* Model evaluation

### Phase 8 — Production Engineering

Planned:

* Docker
* GitHub Actions
* CI/CD
* Monitoring
* Power BI
* Architecture documentation

---

## Synthetic Data Model

The platform currently generates four primary entities.

### Customer

```text
customer_id
first_name
last_name
email
country
state
signup_date
risk_segment
account_status
updated_at
```

### Merchant

```text
merchant_id
name
category
country
merchant_risk_level
updated_at
```

### Device

```text
device_id
customer_id
device_type
operating_system
first_seen
last_seen
trusted_device
```

### Transaction

```text
transaction_id
customer_id
merchant_id
device_id
transaction_timestamp
amount
currency
channel
ip_country
card_present
transaction_status
is_fraud
```

---

## Data Relationships

```text
Customer
   |
   +------< Device
   |
   +------< Transaction >------ Merchant
```

Each transaction references:

* One customer
* One merchant
* One device

Devices are associated with customers, and transaction generation ensures that a transaction only uses a device belonging to the selected customer.

---

## Data Validation

Pydantic is used to enforce data contracts before generated records enter downstream pipelines.

Examples include:

* Valid customer risk segments
* Valid account statuses
* Valid merchant risk levels
* Valid device types
* Valid currencies
* Valid transaction channels
* Valid transaction statuses
* Valid email addresses
* Positive transaction amounts
* Timezone-aware transaction timestamps
* Transaction timestamps cannot be in the future
* Device `last_seen` cannot occur before `first_seen`

These checks simulate the schema and business-rule validation normally performed in production ingestion pipelines.

---

## Fraud Simulation

Fraud labels are not generated using a purely random Boolean.

Each transaction receives a base fraud probability that is adjusted using signals such as:

* High transaction amount
* International activity
* Untrusted device
* High-risk merchant
* Medium-risk merchant
* High-risk customer
* Unusual transaction hour

This produces a synthetic fraud dataset containing patterns that can later be used for feature engineering and ML experimentation.

The current dataset maintains an overall fraud rate of approximately:

```text
~3%
```

---

## Deterministic Data Generation

The generator supports reproducible synthetic datasets using:

```text
Random seed
+
Fixed reference timestamp
```

For example:

```powershell
--seed 42
```

Using the same configuration and seed generates the same synthetic transaction population.

This helps with:

* Debugging
* Testing
* Benchmarking
* Reproducible ML experiments

---

## Large-Scale Generation Strategy

The generator does not load all 10 million transaction records into memory.

Transactions are generated in batches:

```text
10,000,000 transactions
        |
        v
100,000 records per batch
        |
        v
100 batches
        |
        v
Parquet files
```

This prevents memory-bound processing and allows the generator to scale efficiently.

---

## Final 10M Transaction Benchmark

The current generator successfully produced:

```text
Customers:       100,000
Merchants:        10,000
Devices:         200,000
Transactions: 10,000,000

Fraud records:    295,740
Fraud rate:          2.96%

Generation time: 343.36 seconds
Throughput:       29,124 records/sec

Parquet files:       100
Parquet size:      319.05 MB
```

Configuration:

```text
Transaction batch size: 100,000
Seed:                   42
```

---

## JSONL vs Parquet Benchmark

A 1 million transaction benchmark was performed using both formats.

| Metric          |              JSONL |            Parquet |
| --------------- | -----------------: | -----------------: |
| Transactions    |          1,000,000 |          1,000,000 |
| File size       |          307.17 MB |           33.04 MB |
| Generation time |          40.40 sec |          35.00 sec |
| Throughput      | 24,755 records/sec | 28,571 records/sec |
| Fraud rate      |              2.98% |              2.97% |

Parquet reduced the transaction dataset size by approximately **89%** compared with JSONL and preserved a typed analytical schema.

---

## Parquet Schema

```text
transaction_id: string
customer_id: string
merchant_id: string
device_id: string
transaction_timestamp: timestamp[us, tz=UTC]
amount: decimal128(12, 2)
currency: string
channel: string
ip_country: string
card_present: bool
transaction_status: string
is_fraud: bool
```

Financial transaction amounts are stored using:

```text
DECIMAL(12,2)
```

rather than floating-point values.

---

## Repository Structure

```text
fraud-risk-data-platform/
│
├── README.md
├── pyproject.toml
├── .gitignore
│
├── src/
│   └── fraud_platform/
│       └── data_generator/
│           ├── __init__.py
│           ├── models.py
│           ├── generator.py
│           ├── writer.py
│           └── run_generation.py
│
├── tests/
│   ├── test_models.py
│   └── test_generator.py
│
├── data/
│   ├── raw/
│   └── processed/
│
└── terraform/
```

Generated datasets are excluded from Git.

---

## Local Setup

### Clone the repository

```powershell
git clone <repository-url>
cd fraud-risk-data-platform
```

### Create a virtual environment

```powershell
python -m venv .venv
```

### Activate it

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -e ".[dev]"
```

---

## Running Tests

```powershell
pytest -v
```

Run linting:

```powershell
ruff check .
```

Automatically fix supported linting issues:

```powershell
ruff check . --fix
```

---

## Generate a Small Dataset

```powershell
python -m fraud_platform.data_generator.run_generation `
    --customers 1000 `
    --merchants 100 `
    --devices 2000 `
    --transactions 10000 `
    --batch-size 1000 `
    --seed 42
```

---

## Generate the Full Dataset

```powershell
python -m fraud_platform.data_generator.run_generation `
    --customers 100000 `
    --merchants 10000 `
    --devices 200000 `
    --transactions 10000000 `
    --batch-size 100000 `
    --seed 42
```

---

## Generated Output

Transaction data is written as multiple Parquet files:

```text
data/raw/transactions_parquet/
│
├── part-00001.parquet
├── part-00002.parquet
├── part-00003.parquet
│
├── ...
│
└── part-00100.parquet
```

The files together represent one logical transaction dataset.

---

## Verify Parquet Record Count

```python
import pyarrow.dataset as ds

dataset = ds.dataset(
    "data/raw/transactions_parquet",
    format="parquet",
)

print(f"Rows: {dataset.count_rows():,}")
print(dataset.schema)
```

Expected full-dataset result:

```text
Rows: 10,000,000
```

---

## Engineering Concepts Demonstrated

This project currently demonstrates:

* Data contracts
* Schema validation
* Semantic validation
* Referential integrity during generation
* Deterministic test data
* Financial decimal handling
* Timezone-aware timestamps
* Synthetic fraud modeling
* Batch processing
* Chunked processing
* Memory-conscious pipeline design
* Columnar storage
* Parquet schema enforcement
* Compression
* CLI-based pipeline execution
* Performance benchmarking
* Unit testing
* Git-based development

Future phases will extend this to:

* Cloud infrastructure
* Distributed batch processing
* Streaming
* Data quality
* Orchestration
* Warehouse modeling
* Machine learning
* CI/CD
* Observability

---

## Disclaimer

This project uses entirely synthetic data and is intended for educational, portfolio, and technical demonstration purposes.

It does not contain proprietary financial information, customer information, employer data, or production source code.
