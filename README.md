# Nepal Data Infrastructure

Nepal Data Infrastructure (NDI) is a data engineering project for collecting, validating, and working with Nepal-specific datasets.

The first implementation uses population data from Nepal's National Population and Housing Census 2021 (NPHC 2021). It includes a data processing pipeline, a PostgreSQL database, and a read-only REST API built with Django REST Framework.

## Current Dataset

* **Dataset:** Population by Sex, NPHC 2021
* **Source:** [National Statistics Office census dataset downloads](https://censusresults.nsonepal.gov.np/downloads/census-dataset)
* **Raw file:** `data/raw/nphc_2021/Indv01_PopulationBySex.csv`
* **Processed file:** `data/processed/nphc_2021/local_government_population.csv`
* **Coverage:** 753 local governments
* **Schema:** 10 columns covering geographic identifiers, names, households, and population counts by sex

The dataset files are not included in this repository. Download the CSV from the official source and place it at the path shown above. Check the source's terms of use before redistributing the data.

Population figures refer to the 2021 census, not current estimates.

## What It Does

* Profiles the raw census data and checks for missing values and duplicate geographic keys.
* Validates population totals and geographic relationships.
* Converts the source CSV into a consistent local-government dataset.
* Imports validated records into PostgreSQL.
* Provides a read-only API with geographic filters and pagination.
* Tests the pipeline, database import, and API.

## Tech Stack

* Python
* Django and Django REST Framework
* PostgreSQL
* pytest and pytest-django
* python-dotenv

## Project Structure

```text
nepal-data-infrastructure/
├── data/
│   ├── raw/                  # Source files, excluded from Git
│   └── processed/            # Generated datasets, excluded from Git
├── src/
│   ├── config/               # Django configuration
│   ├── ndi/
│   │   ├── profiling/
│   │   ├── transformation/
│   │   └── validation/
│   ├── population/           # Database model, API, import command
│   └── tests/
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repository

```powershell
git clone https://github.com/Sagarbh61/nepal-data-infrastructure.git
cd nepal-data-infrastructure
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

### 3. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Add the source data

Download the NPHC 2021 population-by-sex CSV and place it here:

```text
data/raw/nphc_2021/Indv01_PopulationBySex.csv
```

The pipeline expects this file at that location. Source data is excluded from Git.

### 5. Configure the environment

Create a local environment file:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your PostgreSQL connection details and Django settings:

* `DJANGO_SECRET_KEY`: a private secret key for Django.
* `DJANGO_DEBUG`: set to `True` for local development only.
* `DB_NAME`: database name.
* `DB_USER`: PostgreSQL username.
* `DB_PASSWORD`: PostgreSQL password.
* `DB_HOST` and `DB_PORT`: database connection settings.

Create the PostgreSQL database specified by `DB_NAME` and ensure the configured user has access to it.

Do not commit `.env` or real credentials.

## Data Pipeline

Run these commands from the repository root after completing setup.

### 1. Profile the source data

```powershell
.\.venv\Scripts\python.exe src\ndi\profiling\profile_population.py
```

This reports the structure of the CSV, record types, missing values, duplicate geographic keys, and population arithmetic issues.

### 2. Validate the data

```powershell
.\.venv\Scripts\python.exe src\ndi\validation\validate_population.py
```

This checks population totals, geographic identifiers and hierarchy, and aggregate consistency.

### 3. Transform the data

```powershell
.\.venv\Scripts\python.exe src\ndi\transformation\transform_population.py
```

The transformation selects local-government records, standardizes the column names, and writes the processed CSV to:

```text
data/processed/nphc_2021/local_government_population.csv
```

The expected output contains 753 records and 10 columns.

### 4. Import into PostgreSQL

Apply the database migrations:

```powershell
.\.venv\Scripts\python.exe src\manage.py migrate
```

Import the processed dataset:

```powershell
.\.venv\Scripts\python.exe src\manage.py import_population
```

The import command checks the schema, numeric fields, population arithmetic, geographic keys, and expected record count before writing to the database. The operation is atomic, and rerunning the command updates matching geographic records.

## API

The API provides read-only access to population records stored in PostgreSQL.

Start the development server:

```powershell
.\.venv\Scripts\python.exe src\manage.py runserver
```

Endpoint:

```text
http://127.0.0.1:8000/api/population/
```

Records can be filtered by census year, province, district, and local-government code. Responses use page-number pagination, with 100 records per page.

See the [Population API Reference](src/docs/api.md) for query parameters, response fields, pagination, and validation behavior.

## Tests

Run the test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The tests cover data transformation, database import, and API behavior. Update the test count here when the suite changes rather than maintaining a number that can quickly become outdated.

## Data Quality and Limitations

The validation checks cover internal consistency, including population totals, geographic key uniqueness, and reconciliation between aggregate and underlying records.

These checks can identify inconsistencies, but they do not independently verify the accuracy of every figure published in the source data.

The project currently focuses on one census dataset and is still under development.

## Roadmap

* Improve geographic standardization and data provenance.
* Expand validation rules and test coverage.
* Add more datasets relevant to Nepal.
* Build a frontend with geographic filters, charts, and analytics.
* Explore public deployment.
