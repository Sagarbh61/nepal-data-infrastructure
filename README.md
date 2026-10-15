# Nepal Data Infrastructure

Nepal Data Infrastructure (NDI) is a data engineering project for collecting, validating, transforming, storing, and serving Nepal-specific datasets.

The project currently integrates two datasets:

1. **National Population and Housing Census 2021 (NPHC 2021):** Local-government population and household statistics.
2. **World Development Indicators (WDI):** Development indicators for Nepal, organized by indicator, country, and year.

The system uses Python for data processing, PostgreSQL for storage, and Django REST Framework for read-only API access. Automated tests cover important parts of the data pipeline, database import process, and API behavior.

## Datasets

### 1. National Population and Housing Census 2021

- **Dataset:** Population by Sex
- **Source:** [National Statistics Office census dataset downloads](https://censusresults.nsonepal.gov.np/downloads/census-dataset)
- **Raw file:** `data/raw/nphc_2021/Indv01_PopulationBySex.csv`
- **Processed file:** `data/processed/nphc_2021/local_government_population.csv`
- **Coverage:** 753 local governments
- **Schema:** 10 columns covering geographic identifiers, geographic names, households, and population counts by sex.

The pipeline classifies source records, validates population arithmetic and geographic identifiers, transforms local-government records into a consistent schema, and imports validated records into PostgreSQL.

Population figures refer to the 2021 census, not current population estimates.

### 2. World Development Indicators

- **Dataset:** World Development Indicators for Nepal
- **Source:** [World Bank World Development Indicators](https://databank.worldbank.org/source/world-development-indicators)
- **Raw file:** `data/raw/wdi_nepal/API_NPL_DS2_en_csv_v2_18651.csv`
- **Processed file:** `data/processed/wdi_nepal/indicators.csv`
- **Indicators:** 1,498
- **Year columns:** 66
- **Observation records:** 98,868
- **Non-missing values:** 40,896
- **Missing values:** 57,972

The WDI pipeline validates and transforms the source data into an observation-oriented format. Indicator metadata and country-year observations are stored in PostgreSQL through the `indicators` Django app.

Missing source observations are preserved as missing values rather than converted to zero. Decimal values are validated and handled using decimal arithmetic rather than binary floating-point conversion during transformation.

These counts describe the current processed dataset and may change when the source data or processing rules are updated.

### Data availability

Raw and processed data files are excluded from Git. Download the required source datasets and place them at the paths specified above before running the relevant pipelines. Check the source providers' terms of use before redistributing data.

## What It Does

- Profiles source datasets and identifies data-quality issues.
- Validates geographic identifiers, population totals, and numeric values.
- Transforms source files into consistent, structured datasets.
- Imports validated records into PostgreSQL using transactional database operations.
- Supports repeatable imports without creating duplicate records for existing keys.
- Exposes population records, indicator metadata, and indicator observations through read-only REST API endpoints.
- Supports filtering and pagination for API queries.
- Uses automated tests to check transformation, import, validation, and API behavior.

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- pytest and pytest-django
- python-dotenv

## Project Structure

```text
nepal-data-infrastructure/
├── data/
│   ├── raw/
│   │   ├── nphc_2021/
│   │   └── wdi_nepal/
│   └── processed/
│       ├── nphc_2021/
│       └── wdi_nepal/
├── src/
│   ├── config/                 # Django configuration and root URLs
│   ├── ndi/
│   │   ├── profiling/          # Data profiling
│   │   ├── transformation/     # Data transformation
│   │   ├── validation/         # Data validation
│   │   └── ...
│   ├── population/             # Population models, API, importer
│   ├── indicators/             # Indicator models, API, importer
│   ├── tests/                  # Automated tests
│   └── docs/
│       ├── api.md              # API reference
│       ├── architecture/
│       ├── data-dictionary/
│       └── data-sources/
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

### 4. Obtain the source datasets

Place the downloaded source files at these paths:

```text
data/raw/nphc_2021/Indv01_PopulationBySex.csv
data/raw/wdi_nepal/API_NPL_DS2_en_csv_v2_18651.csv
```

The source files are excluded from Git and must be obtained separately.

### 5. Configure the environment

Create a local environment file:

```powershell
Copy-Item .env.example .env
```

Configure the environment variables in `.env`:

- `DJANGO_SECRET_KEY`: Private Django secret key.
- `DJANGO_DEBUG`: Set to `True` for local development only.
- `DB_NAME`: PostgreSQL database name.
- `DB_USER`: PostgreSQL username.
- `DB_PASSWORD`: PostgreSQL password.
- `DB_HOST` and `DB_PORT`: PostgreSQL connection settings.

Create the configured PostgreSQL database and ensure the database user has appropriate permissions.

Do not commit `.env` or real credentials.

### 6. Apply database migrations

From the repository root:

```powershell
.\.venv\Scripts\python.exe src\manage.py migrate
```

## Data Pipelines

Run the commands from the repository root after completing setup.

### 1. NPHC 2021 population pipeline

#### Profile the source data

```powershell
.\.venv\Scripts\python.exe src\ndi\profiling\profile_population.py
```

This reports the CSV structure, record types, missing values, duplicate geographic keys, and population arithmetic issues.

#### Validate the data

```powershell
.\.venv\Scripts\python.exe src\ndi\validation\validate_population.py
```

This checks population totals, geographic identifiers and hierarchy, and aggregate consistency.

#### Transform the data

```powershell
.\.venv\Scripts\python.exe src\ndi\transformation\transform_population.py
```

The transformation selects local-government records, standardizes column names, and writes the processed dataset to:

`data/processed/nphc_2021/local_government_population.csv`

The expected output contains 753 records and 10 columns.

#### Import into PostgreSQL

```powershell
.\.venv\Scripts\python.exe src\manage.py import_population
```

The importer validates the processed dataset before writing to the database. It uses an atomic transaction and updates matching geographic records when the import is repeated.

### 2. World Development Indicators pipeline

The WDI pipeline transforms the raw World Bank CSV into an observation-oriented dataset, then imports the validated observations and indicator metadata into PostgreSQL.

#### Transform the data

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe src\ndi\transformation\wdi.py
```

By default, the command reads:

`data/raw/wdi_nepal/API_NPL_DS2_en_csv_v2_18651.csv`

It validates the source metadata, year columns, row structure, identifiers, and numeric values, then writes:

`data/processed/wdi_nepal/indicators.csv`

The processed dataset contains 98,868 observation records across 1,498 indicators and 66 years. Missing values are preserved, and non-missing decimal values are validated without conversion to binary floating-point numbers.

#### Import into PostgreSQL

After generating the processed CSV, run:

```powershell
.\.venv\Scripts\python.exe src\manage.py import_wdi
```

The importer validates the input before writing to the database, uses an atomic transaction, and supports repeatable imports without creating duplicate records for existing keys.

## Database and API

The Django application stores population records and WDI indicator data in PostgreSQL.

The API is read-only and exposes the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/population/` | List and filter population records |
| GET | `/api/indicators/` | List indicator metadata |
| GET | `/api/indicators/<code>/` | Retrieve an indicator by code |
| GET | `/api/observations/` | List and filter indicator observations |

List endpoints use page-number pagination with a default page size of 100 records.

The observation API supports filtering by country code, year, and indicator code. Decimal values are returned as strings to preserve precision, and missing values are represented as `null`.

### Run the development server

```powershell
.\.venv\Scripts\python.exe src\manage.py runserver
```

The local API base URL is:

`http://127.0.0.1:8000`

See the [API Reference](src/docs/api.md) for endpoint details, query parameters, response formats, pagination, and validation behavior.

## Tests

Run the complete test suite from the repository root:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m pytest src\tests -q
```

The current verified baseline is **61 passing tests**. The suite covers data transformation, database import behavior, validation, API filtering, pagination, and decimal representation.

The test count is a snapshot and should be updated when the suite changes.

## Data Quality and Limitations

The validation pipeline checks internal consistency, including population totals, geographic key uniqueness, and numeric validity. These checks can identify inconsistencies but cannot independently establish the accuracy of every figure in the original source.

Other limitations include:

- The current implementation focuses on selected datasets rather than a comprehensive national data platform.
- WDI observations currently cover the processed Nepal dataset, not the entire global WDI database.
- Geographic identifiers must be interpreted according to the relevant dataset and geographic definitions.
- The API is read-only and does not currently provide authentication or authorization.
- Source datasets are managed separately from the Git repository.

## Roadmap

- Improve geographic standardization and data provenance.
- Expand validation rules and automated test coverage.
- Add additional datasets relevant to Nepal.
- Improve API documentation and data dictionaries.
- Build a frontend with geographic filters, charts, and analytics.
- Explore public deployment and appropriate access controls.