# Population API Reference

## Overview

The Nepal Data Infrastructure (NDI) Population API provides read-only access to local-government population records from Nepal's National Population and Housing Census 2021.

* **Base URL (local development):** `http://127.0.0.1:8000`
* **Endpoint:** `/api/population/`
* **HTTP method:** `GET`
* **Response format:** JSON
* **Pagination:** Page-number pagination, 100 records per page
* **Authentication:** No authentication is currently configured for this endpoint.

## Getting Started

Start the Django development server from the repository root:

```powershell
.\.venv\Scripts\python.exe src\manage.py runserver
```

Retrieve the first page of population records:

```http
GET http://127.0.0.1:8000/api/population/
```

## Query Parameters

All parameters are optional. Multiple filters can be combined.

| Parameter               | Type    | Purpose                                       | Example                    |
| ----------------------- | ------- | --------------------------------------------- | -------------------------- |
| `census_year`           | Integer | Filter by census year                         | `?census_year=2021`        |
| `province_code`         | Integer | Filter by province code, from 1 to 7          | `?province_code=1`         |
| `district_code`         | Integer | Filter by district code                       | `?district_code=72`        |
| `local_government_code` | Integer | Filter by local-government code, from 1 to 98 | `?local_government_code=5` |
| `page`                  | Integer | Select a page of results                      | `?page=2`                  |

### Examples

Get records for province 1:

```http
GET /api/population/?province_code=1
```

Get records for district 72:

```http
GET /api/population/?district_code=72
```

Get records for local-government code 5:

```http
GET /api/population/?local_government_code=5
```

Get records for census year 2021:

```http
GET /api/population/?census_year=2021
```

Combine filters to narrow the results:

```http
GET /api/population/?census_year=2021&province_code=1&district_code=72
```

Retrieve the second page of a filtered result:

```http
GET /api/population/?province_code=1&page=2
```

Filters are combined using AND logic. A record must satisfy every supplied filter to appear in the results.

## Response Format

A successful request returns a JSON object containing pagination metadata and a `results` array.

Example response structure:

```json
{
  "count": 753,
  "next": "http://127.0.0.1:8000/api/population/?page=2",
  "previous": null,
  "results": [
    {
      "census_year": 2021,
      "province_code": 1,
      "district_code": 1,
      "local_government_code": 1,
      "province_name": "Example Province",
      "district_name": "Example District",
      "local_government_name": "Example Municipality",
      "households": 100,
      "population_total": 400,
      "population_male": 210,
      "population_female": 190
    }
  ]
}
```

**Note:** The values above illustrate the response structure. The `count`, names, and population figures are examples, not verified records. The actual `count` depends on the query and the data currently stored in the database.

### Pagination fields

| Field      | Meaning                                                           |
| ---------- | ----------------------------------------------------------------- |
| `count`    | Total number of matching records across all pages                 |
| `next`     | URL for the next page, or `null` if there is no next page         |
| `previous` | URL for the previous page, or `null` if there is no previous page |
| `results`  | Array of records on the current page                              |

The default page size is 100 records. Results are ordered by province code, district code, and local-government code.

## Population Record Fields

| Field                   | Type    | Description                            |
| ----------------------- | ------- | -------------------------------------- |
| `census_year`           | Integer | Census year associated with the record |
| `province_code`         | Integer | Province's geographic code             |
| `district_code`         | Integer | District's geographic code             |
| `local_government_code` | Integer | Local-government code                  |
| `province_name`         | String  | Province name                          |
| `district_name`         | String  | District name                          |
| `local_government_name` | String  | Local-government name                  |
| `households`            | Integer | Number of households                   |
| `population_total`      | Integer | Total recorded population              |
| `population_male`       | Integer | Recorded male population               |
| `population_female`     | Integer | Recorded female population             |

The API exposes only the fields listed above. It does not currently provide write operations.

## Validation and Errors

Invalid query parameters return HTTP `400 Bad Request` with a JSON error response.

| Parameter               | Invalid input                                          | Validation behavior |
| ----------------------- | ------------------------------------------------------ | ------------------- |
| `census_year`           | Non-integer value                                      | Rejected            |
| `census_year`           | Zero or negative integer                               | Rejected            |
| `province_code`         | Non-integer value                                      | Rejected            |
| `province_code`         | Value outside 1–7                                      | Rejected            |
| `district_code`         | Non-integer value                                      | Rejected            |
| `district_code`         | Zero or negative integer                               | Rejected            |
| `district_code`         | No matching district for the supplied province, if any | Rejected            |
| `local_government_code` | Non-integer value                                      | Rejected            |
| `local_government_code` | Value outside 1–98                                     | Rejected            |

Example invalid request:

```http
GET /api/population/?province_code=abc
```

Example error response:

```json
{
  "province_code": [
    "The province code must be an integer."
  ]
}
```

The precise JSON error structure can vary depending on the validation path. The messages shown here illustrate the API's validation behavior.

## Current Limitations

* The endpoint is read-only.
* The initial dataset covers local-government population records from NPHC 2021.
* A valid filter can return an empty `results` array if no records match.
* Geographic codes are dataset identifiers; a code should not be assumed to identify the same place across every dataset or census year without checking the relevant geographic definitions.
* This reference describes the current implementation and should be updated when endpoint behavior changes.
