# Nepal Data Infrastructure

Nepal Data Infrastructure (NDI) is a data engineering project focused on making Nepal-specific data easier to discover, validate, transform, and query.

The initial implementation uses Nepal's National Population and Housing Census 2021 (NPHC 2021) to build a reproducible data pipeline and a read-only REST API backed by PostgreSQL.

## Current Dataset

* **Dataset:** Population by Sex, National Population and Housing Census 2021
* **Source:** [National Statistics Office census dataset downloads](https://censusresults.nsonepal.gov.np/downloads/census-dataset)
* **Expected raw file:** `data/raw/nphc_2021/Indv01_PopulationBySex.csv`
* **Generated output:** `data/processed/nphc_2021/local_government_population.csv`
* **Coverage:** 753 local-government records
* **Schema:** 10 columns covering geographic identifiers, geographic names, household counts, and population totals by sex

The CSV files are not included in this repository. Obtain the dataset from the official source and place it at the expected path before running the pipeline. Check the source's terms of use before redistributing the dataset.

All population figures refer to the 2021 census, not current population estimates.

## Features

* Profile raw census data, including record types, missing values, and potential duplicates.
* Validate population arithmetic, geographic identifiers, and aggregate consistency.
* Transform raw records into a consistent local-government dataset.
* Import validated records into PostgreSQL.
* Expose population records through Django REST Framework.
* Filter API results by province or district.
* Paginate API responses.
* Test the processing pipeline, database import, and API behavior.

## Technology Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* pytest and pytest-django
* python-dotenv

## Project Structure

```text
nepal-data-infrastructure/
├── data/
│   ├── raw/                  # Local source files, not committed
│   └── processed/            # Generated datasets, not committed
├── src/
│   ├── config/               # Django project configuration
│   ├── ndi/
│   │   ├── profiling/
│   │   ├── transformation/
│   │   └── validation/
│   ├── population/           # Models, API, and import command
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

### 4. Obtain the source dataset

Download the appropriate NPHC 2021 population-by-sex CSV from the official source listed above.

Place it at:

```text
data/raw/nphc_2021/Indv01_PopulationBySex.csv
```

The profiling, validation, and transformation scripts expect this path. The raw dataset is excluded from Git.

### 5. Configure environment variables

Create your local `.env` file from the template:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and configure:

* `DJANGO_SECRET_KEY`: a unique, private Django secret key.
* `DJANGO_DEBUG`: `True` for local development only.
* `DB_NAME`: the PostgreSQL database name.
* `DB_USER`: your PostgreSQL username.
* `DB_PASSWORD`: your PostgreSQL password.
* `DB_HOST` and `DB_PORT`: your database connection settings.

Create an empty PostgreSQL database with the name configured in `DB_NAME`. Ensure the configured user has permission to access it.

Never commit `.env` or real credentials.

## Data Pipeline

Run the following commands from the repository root, after installing dependencies and obtaining the source dataset.

### 1. Profile the source data

```powershell
.\.venv\Scripts\python.exe src\ndi\profiling\profile_population.py
```

This reports the source structure, geographic record types, missing values, duplicate keys, and population arithmetic issues.

### 2. Validate the source data

```powershell
.\.venv\Scripts\python.exe src\ndi\validation\validate_population.py
```

This checks population arithmetic, geographic keys and hierarchy, and aggregate reconciliation.

### 3. Transform the data

```powershell
.\.venv\Scripts\python.exe src\ndi\transformation\transform_population.py
```

This selects local-government records, standardizes column names, validates the output, and writes the processed CSV to:

`data/processed/nphc_2021/local_government_population.csv`

The expected output contains 753 records and 10 columns.

### 4. Import into PostgreSQL

Apply Django migrations:

```powershell
.\.venv\Scripts\python.exe src\manage.py migrate
```

Import the processed data:

```powershell
.\.venv\Scripts\python.exe src\manage.py import_population
```

The import command checks the CSV schema, numeric fields, population arithmetic, geographic keys, and expected record count before writing records. The database operation is atomic, and rerunning the command updates matching geographic records.

## API

Start the local development server:

```powershell
.\.venv\Scripts\python.exe src\manage.py runserver
```

The population endpoint is available at:

`http://127.0.0.1:8000/api/population/`

### Supported query parameters

| Parameter       | Purpose              | Example                             |
| --------------- | -------------------- | ----------------------------------- |
| `province_code` | Filter by province   | `/api/population/?province_code=1`  |
| `district_code` | Filter by district   | `/api/population/?district_code=72` |
| `page`          | Select a result page | `/api/population/?page=2`           |

Filters can be combined:

`/api/population/?province_code=7&district_code=72`

Responses contain a total count, next and previous page links, and a `results` array. The configured page size is 100 records.

The endpoint is read-only. Invalid query values and invalid province-district combinations are rejected.

## Tests

Run the complete test suite from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The current test suite contains 30 passing tests covering data transformation, database import, and API behavior.

## Data Quality and Limitations

The implemented checks verify internal consistency, including whether male and female population counts sum to the reported total, geographic keys are unique, and aggregates reconcile with their underlying records.

Passing these checks does not independently establish that every source figure is accurate. The project currently focuses on a single census dataset and is under active development.

## Roadmap

* Improve geographic standardization and data provenance.
* Expand data validation and automated test coverage.
* Add further Nepal-specific datasets.
* Build a frontend dashboard with geographic filters, visualizations, and analytics.
* Explore public deployment and broader data access.
