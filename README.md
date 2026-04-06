# Mock Data Generator Agent

## Overview
Mock Data Generator Agent is an AI Hub module designed to generate realistic, structured, and configurable synthetic datasets for testing, development, demo, and training purposes.

The agent allows users to create artificial datasets based on predefined schemas or simple configuration rules, without requiring access to sensitive production data. It is particularly valuable in environments where data privacy, security, and regulatory constraints prevent the use of real datasets.

This agent focuses on fast, controlled, and explainable data generation using rule-based and statistical approaches rather than complex modeling techniques.

---

## Purpose
In enterprise environments, especially in banking, accessing real data for development, testing, or demonstrations is often restricted due to privacy and compliance requirements.

The purpose of the Mock Data Generator Agent is to:
- Enable safe data sharing without exposing sensitive information
- Support rapid prototyping and testing
- Provide realistic datasets for demos and presentations
- Reduce dependency on production data
- Accelerate development and validation workflows

---

## Core Capabilities

### 1. Schema-Based Data Generation
Users can define a dataset schema and generate structured data accordingly.

Supported column types:
- Numeric (integer, float)
- Categorical
- Date / datetime
- Boolean
- Text (names, cities, IDs, etc.)

---

### 2. Configurable Value Generation
Each column can be configured with generation rules such as:

#### Numeric
- Range-based (min, max)
- Distribution-based (normal, uniform)

#### Categorical
- Predefined value list
- Weighted probabilities

#### Date
- Date range generation
- Sequential or random dates

#### Boolean
- True/False with probability

---

### 3. Realistic Data Generation (Faker Integration)
The agent can generate realistic fields such as:
- Names
- Emails
- Phone numbers
- Cities
- Addresses
- Company names

---

### 4. Row Volume Control
Users can define:
- Number of rows to generate
- Dataset size scaling

---

### 5. Business Rule Enforcement
The agent supports simple logical constraints such as:
- Age ≥ 18
- Salary > 0
- Transaction amount depends on customer segment

This ensures generated data is not only random but also logically consistent.

---

### 6. Correlation Awareness (Basic Level)
The agent can simulate simple relationships between variables:
- Higher income → higher transaction amount
- Older age → higher balance (optional logic)

---

### 7. Noise Injection (Optional)
Users can optionally introduce controlled noise:
- Missing values
- Random outliers
- Slight inconsistencies

This helps simulate real-world imperfect data.

---

### 8. Export Options
Generated datasets can be exported in:
- CSV format
- Excel (XLSX) format

---

## Target Users
This agent is designed for:

- Data scientists and ML engineers
- Software developers
- QA and testing teams
- Business analysts
- Product teams
- Internal demo and training teams

---

## Example Use Cases

### Example 1: Testing a Data Pipeline
A developer needs a dataset with customer transactions to test an ETL pipeline. The agent generates a structured dataset with realistic distributions and relationships.

---

### Example 2: Demo Environment Preparation
A team needs to demonstrate a product without exposing real customer data. The agent generates a realistic but fully synthetic dataset.

---

### Example 3: Model Development Without Production Data
A data scientist wants to prototype a model but cannot access real data. The agent creates a dataset with similar structure and variability.

---

### Example 4: Training and Onboarding
New employees need sample datasets to practice analysis and reporting tasks.

---

## End-to-End Workflow

1. User selects dataset generation mode:
   - Schema-based generation

2. User defines:
   - Column names
   - Data types
   - Value generation rules

3. User sets parameters:
   - Number of rows
   - Optional noise level
   - Optional business rules

4. Agent generates dataset

5. User previews generated data

6. User downloads dataset in desired format
