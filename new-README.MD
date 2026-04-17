📊 Mock Data Generator
Overview
Mock Data Generator is a user-friendly tool designed to generate synthetic datasets either from an existing dataset or entirely from scratch. The goal of the project is to enable both technical and non-technical users to quickly create realistic, customizable datasets for testing, development, and analysis purposes.
The application provides a structured and guided experience where users can define dataset properties, configure column-level rules, and generate data that mimics real-world scenarios.
Key Features
1. Dual Data Generation Modes
The system supports two main workflows:
Upload Existing Dataset
Users can upload a CSV or Excel file.
The system analyzes the dataset and generates similar synthetic data.
Design Dataset from Scratch
Users can fully define a dataset structure and generate synthetic data without any input file.
Dataset Creation (From Scratch)
The dataset creation process is designed as a step-by-step guided workflow to ensure ease of use and clarity.
Step 1: General Dataset Configuration
Users define the overall structure of the dataset:
Number of rows
Number of columns
Language (e.g., Turkish, English)
Dataset name (optional)
Dataset description / purpose (optional)
Step 2: Column Definition
Users define each column individually through a structured interface.
Each column includes:
Column name
Data type
Allow null values (optional)
Unique constraint (optional)
Columns are presented as modular “cards” to make the process intuitive and manageable.
Supported Data Types
The system provides both general and ready-to-use data types:
Integer
Float / Decimal
String / Text
Categorical
Boolean
Date / Datetime
ID
Email
Phone
Name
Company
Country / City / Address
Custom Pattern
This abstraction ensures usability for non-technical users while maintaining flexibility.
Step 3: Type-Specific Configuration
Each data type has its own configurable parameters.
Numeric (Integer / Float)
Minimum and maximum values
Decimal precision (for float)
Distribution type (uniform)
Negative values allowed
Sequential generation option
Step value (increment)
Categorical
Define categories manually
Assign probability/weight to each category
Control number of distinct categories
Null value option
String / Text
Minimum and maximum length
Character rules (letters, numbers, mixed)
Case selection (upper/lower/mixed)
Optional pattern-based generation
Example-based generation
Date / Datetime
Start date and end date
Output format (e.g., YYYY-MM-DD, DD/MM/YYYY)
Include time (optional)
Business days only (optional)
Boolean
Value format (True/False, Yes/No, 1/0)
Distribution ratio
ID
Prefix definition
Starting number
Fixed length
Sequential or random generation
Unique constraint enforcement
Predefined Types (Email, Phone, Name, etc.)
These types are generated using realistic patterns to simulate real-world data formats.
Step 4: Data Realism & Quality Settings
Users can control how realistic or noisy the dataset should be:
Missing value ratio
Duplicate ratio
Outlier generation
Format inconsistencies
Typographical variations
Whitespace inconsistencies
Two main modes can be supported conceptually:
Clean dataset
Real-world (noisy) dataset
Step 5: Data Preview
Before exporting, users can preview the generated dataset:
First N rows preview
Column type summary
Null distribution overview
Category distribution (if applicable)
This step ensures users can validate their configuration before final generation.
Step 6: Export Options
Generated datasets can be exported in multiple formats:
CSV
Excel (XLSX)
JSON
Usability Design Principles
The system is designed with accessibility in mind:
No technical jargon (e.g., avoid terms like "object", "varchar")
Clear and intuitive labels (e.g., "Text", "Number", "Date")
Step-by-step guided workflow
Visual column-based configuration
Inline previews for better understanding
Validation & Error Handling
The system includes built-in validation mechanisms to prevent incorrect configurations:
Invalid ranges (min > max)
Missing category definitions
Inconsistent distribution ratios
Missing required parameters
Users are guided with clear feedback messages to fix issues.
Architecture Overview (High-Level)
Frontend: Streamlit-based interactive UI
Backend Logic: Rule-based synthetic data generation engine
Data Handling: Pandas-based processing
Export Layer: Multi-format file generation (CSV, XLSX, JSON)
Target Users
Business users (non-technical)
Data analysts
Machine learning engineers
QA testers
Product teams
Use Cases
Testing data pipelines
Training machine learning models
Creating demo datasets
Simulating real-world scenarios
Validating data quality tools
Summary
Mock Data Generator transforms dataset creation into a structured, intuitive, and highly configurable process. By enabling users to design datasets from scratch or replicate existing ones, it significantly reduces dependency on real data while supporting rapid experimentation and development.
