<div align="center">
  <h1>📊 Serverless Customer Analytics Pipeline</h1>
  <p>An automated, end-to-end Data Engineering ETL Pipeline for Customer Sentiment Analysis.</p>
  
  [![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://www.python.org/)
  [![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?logo=amazonaws&logoColor=white)](https://aws.amazon.com/lambda/)
  [![Amazon S3](https://img.shields.io/badge/AWS-S3-569A31?logo=amazons3&logoColor=white)](https://aws.amazon.com/s3/)
  [![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
  [![Power BI](https://img.shields.io/badge/BI-Power_BI-F2C811?logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
</div>

---

## 📖 Project Overview

This project implements a fully automated, **Serverless Data Pipeline** designed to monitor customer satisfaction and extract actionable insights through Natural Language Processing (NLP). The infrastructure extracts real-world reviews, applies sentiment analysis, and persists the curated data in a cloud Data Warehouse for immediate consumption via Business Intelligence dashboards.

The architecture strictly adheres to modern Data Engineering best practices, utilizing event-driven cloud computing minimizing operational costs (nearly $0 footprint).

## 🏗️ Architecture & Flow

The pipeline executes daily through the following stages:

1. **Extract (Web Scraping)**: Triggered via a cron job (EventBridge), an AWS Lambda function crawls real customer reviews from public sources (e.g., Trustpilot).
2. **Transform (Data Cleaning & NLP)**: Raw HTML is parsed (`BeautifulSoup`). Data is structured into a `Pandas` DataFrame, cleansed, and categorized by Sentiment based on user ratings.
3. **Load (Data Lake Layer)**: Raw unformatted data is persisted in **Amazon S3** as a backup and data lake foundation.
4. **Load (Data Warehouse Layer)**: The transformed, clean DataFrame is appended into a **PostgreSQL** database (Supabase) using a serverless-friendly driver (`pg8000`).
5. **Analyze (BI Reporting)**: **Power BI** connects directly to the PostgreSQL warehouse via DirectQuery or Scheduled Import, immediately refreshing the visualizations.

## 🧰 Technology Stack

- **Extraction**: `Python`, `Requests`, `BeautifulSoup4`
- **Transformation**: `Pandas`
- **Storage/DB**: `Amazon S3` (Data Lake), `PostgreSQL` / `Supabase` (Data Warehouse)
- **Cloud Computing**: `AWS Lambda`, `Amazon EventBridge`
- **Visualization**: `Microsoft Power BI Desktop`

## 📂 Repository Structure

```text
├── lambda_function.py      # Production AWS Lambda target (ETL Core)
├── scraper.py              # Local testing environment for data extraction
├── aws_uploader.py         # S3 Connectivity testing module
├── requirements.txt        # Python dependencies for AWS Lambda Layer
├── README.md               # Project documentation
└── .gitignore              # Ignored files for version control
```

## 🚀 Setup & Execution

### Local Testing

1. Clone the repository and install dependencies:
   ```bash
   pip install pandas beautifulsoup4 requests sqlalchemy pg8000 boto3
   ```
2. Set your environment variables (or rely on `.env` files):
   ```bash
   export DB_URI="postgresql+pg8000://user:password@host:port/dbname"
   ```
3. Run the local script to test the ETL flow:
   ```bash
   python lambda_function.py
   ```

### Cloud Deployment (AWS)

1. Package `lambda_function.py` along with the required libraries (`pandas`, `bs4`, `sqlalchemy`, `pg8000`) into a `.zip` deployment package.
2. Upload the deployment package to an AWS Lambda function with Python 3.12+ runtime.
3. Attach an IAM Role granting `AmazonS3FullAccess` (or scoped permissions) to allow the function to write to S3.
4. Configure an Amazon EventBridge trigger (Schedule expression: `cron(0 8 * * ? *)` for 8:00 AM daily).

## 📈 Impact & Business Value

- **Cost Efficiency**: Serverless architecture means payment is made strictly per millisecond of compute.
- **Data Integrity**: Maintaining a raw copy in S3 ensures data traceability, while the database provides clean data for analysts.
- **Automation**: Marketing and Customer Success teams get a real-time pulse on consumer sentiment without any manual data entry.

---
*Created as part of a Data Engineering Porfolio Showcase.*
