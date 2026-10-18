# Nepal Data Infrastructure

Nepal Data Infrastructure (NDI) is a data engineering project for collecting, validating, transforming, storing, and serving Nepal-specific datasets through documented, read-only APIs.

The project currently integrates three datasets:

1. **National Population and Housing Census 2021 (NPHC 2021):** Local-government population and household statistics.
2. **World Development Indicators (WDI):** Development indicators for Nepal, organized by indicator, country, and year.
3. **World Bank Enterprise Survey (WBES), Nepal 2023:** Survey-weighted and unweighted statistics describing business obstacles reported by eligible formal-sector establishments.

The backend uses Python, PostgreSQL, Django, and Django REST Framework. Population and WDI data are stored in PostgreSQL, while the WBES API serves summarized statistics from a processed CSV file. A React and TypeScript frontend provides interfaces for exploring development indicators and their historical trends, as well as reported business obstacles.

Automated tests cover important parts of the data pipeline, database imports, validation, transformations, and API behavior.

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

The WDI pipeline validates and transforms the source data into an observation-oriented format. Indicator metadata and country-year observations are stored in PostgreSQL through the Django `indicators` app.

Missing source observations are preserved as missing values rather than converted to zero. Decimal values are handled using decimal arithmetic during transformation to avoid unnecessary binary floating-point conversion.

These counts describe the current processed dataset and may change when the source data or processing rules are updated.

### 3. World Bank Enterprise Survey (WBES), Nepal 2023

- **Dataset:** Business obstacles reported by eligible formal-sector establishments
- **Source:** [World Bank Enterprise Surveys](https://www.enterprisesurveys.org/)
- **Raw file:** `data/raw/wbes_2023/Nepal-2023-full-data.dta`
- **Processed file:** `data/processed/wbes_2023/business_obstacles.csv`
- **Survey cases:** 582
- **Output:** 14 summarized business-obstacle indicators
- **Survey period:** May–August 2023
- **Survey documentation:** `src/docs/data-sources/ddi-documentation-english_microdata-6457.pdf`

The pipeline calculates the unweighted share and survey-weighted share of valid responses rating each obstacle as a major or very severe constraint. The primary weighted measure uses the survey's `wmedian` sampling weight.

Ratings of 3 and 4 count as major or very severe. Valid ratings range from 0 to 4. Missing ratings and special response codes, including not applicable (`-7`) and don't know (`-9`), are excluded. The excluded-response count combines these categories.

**Coverage limitation:** The survey covers eligible formal-sector establishments with at least five employees, subject to the survey's sector and ownership eligibility criteria. It does not represent every business in Nepal.

The statistics measure respondents' reported perceptions of business obstacles. They do not establish that an obstacle caused a particular business outcome.

### Data availability

Raw and processed data files are excluded from Git. Obtain the required source datasets separately and place them at the paths specified in this README before running the relevant pipelines.

Check the source providers' terms of use before redistributing datasets or derived data.

## What It Does

- Profiles source datasets and identifies data-quality issues.
- Validates geographic identifiers, population totals, and numeric values.
- Transforms source files into consistent, structured datasets.
- Imports validated population and WDI records into PostgreSQL using transactional database operations.
- Supports repeatable imports without creating duplicate records for existing keys.
- Calculates documented, survey-weighted and unweighted business-obstacle statistics from WBES data.
- Exposes population records, indicator metadata, indicator observations, and WBES summaries through read-only REST API endpoints.
- Supports filtering and pagination for API queries.
- Provides a frontend for browsing development indicators, viewing historical trends, and exploring WBES business-obstacle statistics.
- Uses automated tests to check transformation, import, validation, and API behavior.

## Tech Stack

### Backend and data engineering

- Python
- Django
- Django REST Framework
- PostgreSQL
- pytest and pytest-django
- python-dotenv

### Frontend

- React
- TypeScript
- Vite
- React Router
- Recharts
- Lucide React

## Project Structure

```text
nepal-data-infrastructure/
├── data/
│   ├── raw/                         # Source datasets; excluded from Git
│   │   ├── nphc_2021/
│   │   ├── wdi_nepal/
│   │   └── wbes_2023/
│   └── processed/                   # Generated datasets; excluded from Git
│       ├── nphc_2021/
│       ├── wdi_nepal/
│       └── wbes_2023/
├── frontend/
│   ├── src/
│   │   ├── app/                     # Application and routes
│   │   ├── assets/                  # Images and static assets
│   │   ├── components/
│   │   │   ├── hero/
│   │   │   └── navbar/
│   │   ├── pages/                  # Home, explorer, detail, business environment
│   │   ├── services/               # API client
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
├── src/
│   ├── config/                      # Django configuration and root URLs
│   ├── ndi/
│   │   ├── profiling/               # Data profiling
│   │   ├── transformation/          # Dataset transformation
│   │   ├── validation/              # Data validation
│   │   └── ...
│   ├── population/                  # Population models, API, importer
│   ├── indicators/                  # WDI models, API, importer
│   ├── wbes/                        # WBES API and serializers
│   ├── tests/                       # Automated tests
│   ├── docs/
│   │   ├── api.md                   # API reference
│   │   └── data-sources/            # Source documentation
│   └── manage.py
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

### 2. Create a Python virtual environment

Run from the repository root:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

### 3. Install backend dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Use the virtual environment's Python executable for subsequent backend commands.

### 4. Obtain the source datasets

Place the downloaded files at these paths:

```text
data/raw/nphc_2021/Indv01_PopulationBySex.csv
data/raw/wdi_nepal/API_NPL_DS2_en_csv_v2_18651.csv
data/raw/wbes_2023/Nepal-2023-full-data.dta
```

The source files are excluded from Git and must be obtained separately. The WBES pipeline requires the 2023 Nepal formal-sector survey file; other survey years or the separate informal-sector survey are not interchangeable without an explicit methodological decision.

### 5. Configure the environment

Create a local environment file:

```powershell
Copy-Item .env.example .env
```

Configure the following environment variables in `.env`:

- `DJANGO_SECRET_KEY`: Private Django secret key.
- `DJANGO_DEBUG`: Set to `True` for local development only.
- `DB_NAME`: PostgreSQL database name.
- `DB_USER`: PostgreSQL username.
- `DB_PASSWORD`: PostgreSQL password.
- `DB_HOST` and `DB_PORT`: PostgreSQL connection settings.

Create the configured PostgreSQL database and ensure the database user has appropriate permissions.

Do not commit `.env` or real credentials.

### 6. Apply database migrations

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe src\manage.py migrate
```

## Data Pipelines

Run the commands from the repository root after completing the setup and obtaining the relevant source files.

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

The transformation selects local-government records, standardizes column names, and writes:

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

```powershell
.\.venv\Scripts\python.exe src\ndi\transformation\wdi.py
```

By default, the command reads:

`data/raw/wdi_nepal/API_NPL_DS2_en_csv_v2_18651.csv`

It validates source metadata, year columns, row structure, identifiers, and numeric values, then writes:

`data/processed/wdi_nepal/indicators.csv`

The processed dataset contains 98,868 observation records across 1,498 indicators and 66 years. Missing values are preserved, and non-missing decimal values are validated without conversion to binary floating-point numbers.

#### Import into PostgreSQL

After generating the processed CSV, run:

```powershell
.\.venv\Scripts\python.exe src\manage.py import_wdi
```

The importer validates the input before writing to the database, uses an atomic transaction, and supports repeatable imports without creating duplicate records for existing keys.

### 3. World Bank Enterprise Survey pipeline

#### Transform the data

```powershell
.\.venv\Scripts\python.exe src\ndi\transformation\transform_wbes_obstacles.py
```

The transformation reads the Nepal 2023 WBES source data and generates:

`data/processed/wbes_2023/business_obstacles.csv`

The output summarizes 14 business obstacles, including response counts, excluded-response counts, unweighted shares, and shares calculated using the `wmedian` survey weight.

The processed CSV is served directly by the Django WBES API. The current implementation does not import these summarized WBES records into PostgreSQL.

## Database and API

The Django application stores population records and WDI indicator data in PostgreSQL. The WBES business-obstacle API reads its summarized statistics from a processed CSV file and exposes survey-methodology metadata through a separate endpoint.

The API is read-only and exposes the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/population/` | List and filter population records |
| GET | `/api/indicators/` | List indicator metadata |
| GET | `/api/indicators/<code>/` | Retrieve an indicator by code |
| GET | `/api/observations/` | List and filter indicator observations |
| GET | `/api/wbes/business-obstacles/` | List summarized business-obstacle statistics |
| GET | `/api/wbes/metadata/` | Retrieve WBES methodology and limitations |

List endpoints use page-number pagination with a default page size of 100 records.

The population API supports filtering by census year, province code, district code, and local-government code. Multiple filters can be combined.

The observation API supports filtering by country code, year, and indicator code. Decimal values are returned as strings to preserve precision, and missing values are represented as `null`.

The WBES business-obstacles endpoint returns weighted and unweighted shares for valid responses. Its metadata endpoint documents the survey population, weighting method, measurement approach, and limitations. These statistics should not be generalized to all businesses in Nepal.

### Run the backend server

From the repository root:

```powershell
.\.venv\Scripts\python.exe src\manage.py runserver
```

The local API base URL is:

`http://127.0.0.1:8000`

For endpoint details, query parameters, response formats, pagination, and validation behavior, see the [API Reference](src/docs/api.md).

## Frontend

The project includes a React and TypeScript frontend built with Vite.

The current application includes:

- **Home page:** Landing page for the project.
- **Indicator explorer:** Browse available development indicators.
- **Indicator detail page:** View historical observations, trend charts, and summary statistics for an individual indicator.
- **Business Environment page:** Explore weighted and unweighted WBES business-obstacle statistics, response coverage, and survey limitations.

The frontend includes WDI indicator exploration and a Business Environment page for exploring WBES business-obstacle statistics. Population data remains available through the backend API but has not yet been integrated into the frontend.

### Requirements

- Node.js and npm
- A configured PostgreSQL database
- The Django backend with the required population and WDI data imported
- The processed WBES CSV available for the Business Environment page

The WBES API requires its processed CSV output to be available at `data/processed/wbes_2023/business_obstacles.csv`. Generate this file using the WBES transformation command before using the WBES frontend features.

### Install frontend dependencies

Open a second terminal at the repository root:

```powershell
cd frontend
npm install
```

### Run the frontend development server

```powershell
npm run dev
```

Open the local URL printed by Vite, normally:

`http://localhost:5173`

Keep the Django backend running in the first terminal while using the frontend.

### Build and lint

From the `frontend` directory, build the frontend:

```powershell
npm run build
```

Run the linter:

```powershell
npm run lint
```

The frontend currently uses `http://127.0.0.1:8000/api` as its API base URL. The backend's CORS configuration must permit the frontend's development origin.

Production API configuration and deployment are future improvements.

## Tests

Run the backend test suite from the repository root:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m pytest src\tests -q
```

The suite covers data transformation, database import behavior, validation, API filtering and pagination, decimal representation, and WBES API and methodology behavior.

Run the suite after changes to verify that existing behavior remains correct. Test counts may change as coverage expands.

## Data Quality and Limitations

The validation pipeline checks internal consistency, including population totals, geographic key uniqueness, and numeric validity. These checks can identify inconsistencies but cannot independently establish the accuracy of every figure in the original source.

Other limitations include:

- The project focuses on selected datasets rather than a comprehensive national data platform.
- NPHC population figures describe the 2021 census, not current population estimates.
- WDI observations currently cover the processed Nepal dataset, not the entire global WDI database.
- WBES statistics describe reported perceptions among eligible formal-sector establishments, not every business in Nepal.
- WBES obstacle statistics do not establish causal effects on business performance.
- Population frontend integration has not yet been implemented.
- Geographic identifiers must be interpreted according to the relevant dataset and geographic definitions.
- Indicator charts and summary statistics should be interpreted in the context of each indicator's units, coverage, and missing observations.
- The APIs are read-only and do not currently provide authentication or authorization.
- Source datasets are managed separately from the Git repository.
- Production deployment and configuration have not yet been completed.

## Roadmap

### Data engineering and API

- Expand validation rules and automated test coverage.
- Improve geographic standardization and data provenance.
- Add additional datasets relevant to Nepal.
- Improve API documentation and data dictionaries.
- Continue improving API filtering and query efficiency.
- Evaluate whether additional datasets should be stored in PostgreSQL or served from validated processed files.

### Analytics and frontend

- Audit indicator-level statistical calculations.
- Add annual absolute and percentage changes with appropriate safeguards.
- Introduce configurable period comparisons and date ranges.
- Expand data-coverage, missing-value, and quality information.
- Develop additional time-series analytics.
- Integrate population data into the frontend.
- Expand geographic analysis using Nepal's province, district, and local-government data.

### Deployment

- Improve frontend and backend configuration for deployment.
- Evaluate suitable hosting and database options.
- Establish appropriate security, access controls, and operational monitoring before public deployment.
