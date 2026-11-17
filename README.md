<p align="center">
  <img src="assets/ascii.png" alt="ASCII" width="100%">
</p>

# 7XX Service

A playful HTTP status code generator that brings the unofficial 7XX status code series to life.

![CI](https://github.com/nico-tinico/7xx-service/actions/workflows/ci.yml/badge.svg) ![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-powered-009688.svg) ![Docker](https://img.shields.io/badge/Docker-supported-2496ED.svg)

## Overview

**7XX Service** is a lightweight REST API built with Python and FastAPI that generates real HTTP responses using status codes from the unofficial 7XX series.

Inspired by [joho/7XX-rfc](https://github.com/joho/7XX-rfc), this project turns humorous and unconventional HTTP status codes into an actual, working API.

Instead of returning a standard HTTP 200 response containing a fictional status code in the JSON body, **7XX Service** attempts to send the requested **7XX code** as the actual HTTP response status.

For example:

```
HTTP/1.1 725
Content-Type: application/json
X-7XX-Message: It works on my machine
Cache-Control: no-store
```

The response body contains the corresponding status code and description.

Note: The 7XX status code series is experimental and unofficial. These codes are not part of the HTTP standard and may not be supported by HTTP clients, reverse proxies, gateways or monitoring systems.

## Features

- Random status codes — Generate a random 7XX response.
- Real HTTP status codes — Return 7XX codes as actual HTTP response statuses.
- Specific status codes — Request any code available in the catalog.
- Code catalog — Retrieve the complete list of available 7XX codes.
- Automatic catalog parsing — Load status codes and descriptions from the upstream RFC document.
- JSON responses — Consistent and structured response payloads.
- Docker support — Run the service using Docker or Docker Compose.
- Automated testing — Test the application with pytest.
- Continuous integration — Automated checks through GitHub Actions.

## Quick Start

### Requirements
- Python 3.12 or newer
- pip
- Git

Docker and Docker Compose are optional.

### 1. Clone the repository

```
git clone https://github.com/nico-tinico/7xx-service.git
cd 7xx-service
```

### 2. Create a virtual environment

```
python -m venv .venv
```

Activate it:

Linux / macOS

```
source .venv/bin/activate
```

Windows (PowerShell)

```
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Start the service

```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --http h11
```

The API will be available at:

```
http://localhost:8000
```

Interactive API documentation:

-Swagger UI: http://localhost:8000/docs
-ReDoc: http://localhost:8000/redoc

## API Reference

| Method | Endpoint     | Description                                  |
| ------ | ------------ | -------------------------------------------- |
| GET    | /            | Generate a random 7XX response               |
| GET    | /random      | Generate a random 7XX response               |
| GET    | /random/info | Retrieve information about a random 7XX code |
| GET    | /codes       | List all available 7XX codes                 |
| GET    | /health      | Check service health                         |
| GET    | /{code}      | Return a specific 7XX status code            |

### 1. Random status code

Generate a random status code from the catalog.

```
curl -i http://localhost:8000/random
```

Example response:

```
HTTP/1.1 725
Content-Type: application/json
X-7XX-Message: It works on my machine
Cache-Control: no-store
```

Body response:

```
{
  "status": 725,
  "message": "It works on my machine",
  "series": "7XX"
}
```

The returned status code and message depend on the selected catalog entry.

The / endpoint is also an alias for /random.

### 2. Content negotiation
7XX Service supports HTTP content negotiation through the Accept request header.

The API automatically selects the response representation based on the client's preferences.

Supported media types:

| Accept header    | Response format | 
| ---------------- | --------------- | 
| application/json | JSON            | 
| text/plain       | Plain text      | 
| text/html        | HTML            | 
| */*              | JSON (default)  | 

JSON is also used when the Accept header is missing.

#### JSON response

```
curl -i \
  -H "Accept: application/json" \
  http://localhost:8000/random
```

Example body:

```
{
  "status": 725,
  "message": "It works on my machine",
  "series": "7XX"
}
```

#### Plain text response

```
curl -i \
  -H "Accept: text/plain" \
  http://localhost:8000/random
```

Example body:

```
725 - It works on my machine
```

#### HTML response

```
curl -i \
  -H "Accept: text/html" \
  http://localhost:8000/random
```

The API returns a complete HTML document containing the response information.

#### Quality values and preferences

The content negotiation mechanism also supports quality values (q) and wildcard media types.

For example:

```
curl -i \
  -H "Accept: text/html;q=0.9, application/json;q=1.0" \
  http://localhost:8000/random
```

In this case, JSON is preferred because it has the highest quality value.

If none of the requested media types can be satisfied, the API returns:

```
HTTP/1.1 406 Not Acceptable
```

The response includes a Vary: Accept header to indicate that the representation depends on the request's Accept header.

Content negotiation is supported by /random, /random/info, /codes and /{code}.

### 3. Random code information

The /random/info endpoint retrieves information about a randomly selected 7XX status code without using that code as the actual HTTP response status.

Unlike /random, this endpoint always returns HTTP 200 for a successful request.

```
curl -i http://localhost:8000/random/info
```

Example response:

```
HTTP/1.1 200 OK
Content-Type: application/json
```

Response body:

```
{
  "status": 725,
  "message": "It works on my machine",
  "series": "7XX"
}
```

This endpoint is useful when clients need to retrieve random 7XX information without handling unconventional HTTP status codes.

It also supports content negotiation, allowing JSON, plain text and HTML responses.

### 4. Reproducible random generation

Both /random and /random/info support an optional seed query parameter.

A seed allows the random selection to be reproduced across requests.

Example:

```
curl -i "http://localhost:8000/random?seed=12345"
```

Repeated requests using the same seed produce the same selected catalog entry, provided the catalog remains unchanged.

The same behavior applies to /random/info:

```
curl "http://localhost:8000/random/info?seed=12345"
```

Example:

```
{
  "status": 725,
  "message": "It works on my machine",
  "series": "7XX"
}
```

Using a different seed can produce a different selection.

**Notes**:

- The seed parameter is optional.
- Without a seed, the API uses normal random selection.
- The same seed and catalog produce reproducible results.
- Changes to the catalog may affect which code is selected for a given seed.

### 5. Request a specific status code

Retrieve a specific 7XX status code:

```
curl -i http://localhost:8000/701
```

The service returns the requested code if it exists in the catalog.

Unknown codes return a standard HTTP 404 response.

### 6. Browse and search the code catalog
The /codes endpoint provides access to the complete 7XX catalog.

It supports text search, numeric range filtering, sorting and pagination.

Basic request:

```
curl http://localhost:8000/codes
```

Example response:

```
{
  "count": 42,
  "total": 42,
  "limit": 100,
  "offset": 0,
  "codes": [
    {
      "status": 701,
      "message": "Example description"
    },
    {
      "status": 725,
      "message": "It works on my machine"
    }
  ]
}
```

The example is illustrative; the actual catalog may contain additional entries.

#### Query parameters

| Parameter | Type    | Default | Description                                 | 
| --------- | ------- | ------- | ------------------------------------------- | 
| search    | string  | None    | Search within code numbers and descriptions | 
| min       | integer | None    | Minimum status code                         | 
| max	      | integer | None    | Maximum status code                         | 
| sort      | string  | asc     | Sort order: asc or desc                     | 
| limit     | integer | 100     | Maximum number of results (1–1000)          | 
| offset    | integer | 0       | Number of results to skip                   | 

#### Text search
Search for a keyword within code descriptions or status code numbers.

```
curl "http://localhost:8000/codes?search=machine"
```

Search is case-insensitive when matching descriptions.

#### Numeric range filtering
Retrieve codes within a specific numeric range:

```
curl "http://localhost:8000/codes?min=720&max=730"
```

Both parameters are optional and accept values between 700 and 799.

#### Sorting
Sort results in ascending order (default):

```
curl "http://localhost:8000/codes?sort=asc"
```

Sort results in descending order:

```
curl "http://localhost:8000/codes?sort=desc"
```

Sorting is based on the numeric status code.

#### Pagination
Limit the number of returned results:

```
curl "http://localhost:8000/codes?limit=10"
```

Skip the first results using offset:

```
curl "http://localhost:8000/codes?limit=10&offset=10"
```

The response contains:

- count — Number of results returned in the current page.
- total — Total number of results after filtering, before pagination.
- limit — Maximum number of results requested.
- offset — Number of results skipped.
- codes — Array containing the current page.

#### Combining filters
All filtering and pagination parameters can be combined.

For example:

```
curl "http://localhost:8000/codes?search=machine&min=700&max=799&sort=desc&limit=5&offset=0"
```
This request:

Searches for machine in descriptions and code numbers.
Restricts results to the specified numeric range.
Sorts matching codes in descending order.
Returns at most five results.
Starts from the first result.

#### Validation and errors

The endpoint validates query parameters and returns HTTP 422 for invalid requests.

Examples include:

- min greater than max.
- min or max outside the 700–799 range.
- limit outside the 1–1000 range.
- Negative offset.
- Invalid sort values.
- Empty search values.

Example:

```
curl -i "http://localhost:8000/codes?min=750&max=720"
```
Returns:

```
HTTP/1.1 422 Unprocessable Entity
```

The /codes endpoint also supports content negotiation.

### 7. Health check
Check whether the service is running:

```
curl http://localhost:8000/health
```

Example response:

```
{
  "status": "ok",
  "available_codes": 42
}
```
The number of available codes depends on the loaded catalog.

## Docker

The easiest way to run **7XX Service** without installing Python dependencies locally is **Docker Compose**.

### Build and start

```
cd 7xx-service
docker compose up --build -d
```

### Check container status

```
docker compose ps
```

### View logs

```
docker compose logs -f
```

Stop the service

```
docker compose down 7xx
```

The service listens on port 8000.

### Catalog Management

The status code catalog is based on the original 7XX RFC repository by **joho**.

The application automatically parses the local Markdown document at startup and builds the status code catalog.

To retrieve an updated version of the upstream document, run:

```
python -m scripts.update_catalog
```

Restart the service after updating the catalog to load the new entries.

**Important**: The upstream specification and catalog are subject to their own licensing terms. See the Credits and Licensing sections before redistributing modified or downloaded catalog data.

## Development

###Running tests

Install the project dependencies and run:

```
pytest -v
```

The test suite covers:

- Health check and catalog integrity.
- Random and specific status code generation.
- Real HTTP 7XX responses through Uvicorn.
- Content negotiation and supported media types.
- Random information retrieval.
- Deterministic generation using seeds.
- Catalog search and numeric range filtering.
- Sorting and pagination.
- Invalid parameter handling.

### Project structure

```
7xx-service/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── catalog.py
│   └── uvicorn_7xx.py
│
├── data/
│   └── 7xx.md
│
├── scripts/
│   └── update_catalog.py
│
├── tests/
│   ├── test_api.py
│   └── ...
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── README.md
```

### Implementation

7XX Service uses:

- **FastAPI** for the REST API.
- **Uvicorn** as the ASGI server.
- **h11** as the HTTP protocol implementation.
- Python's **random module** for random selection and seeded generation.
- **pytest** for automated testing.
- **Docker** for containerization.

One of the main technical challenges is that HTTP server implementations normally reject status codes outside the standardized range.

To work around this limitation, the application registers the 7XX status codes in Uvicorn's underlying h11 status phrase mapping.

This allows the service to emit actual **non-standard** HTTP response codes rather than simply placing fictional status numbers inside a JSON payload.

This implementation relies on an internal **Uvicorn/h11** data structure and may require adjustments when upgrading dependencies.

## Considerations

Experimental HTTP status codes

The 7XX series is not officially registered as part of HTTP.

Standard HTTP status codes currently belong to the 100–599 range.

As a consequence:

- Some HTTP clients may **reject** 7XX responses.
- Reverse proxies may **normalize** or **discard** unknown status codes.
- API gateways may **return errors** instead of forwarding the original response.
- Monitoring and observability tools may **not recognize** these codes.
- Browser and SDK behavior may **vary**.

For reliable results, test the service directly before introducing additional HTTP infrastructure.

### Intended use

This project is intended for:

- Experimentation with HTTP protocol behavior.
- API demonstrations.
- Testing HTTP client compatibility.
- Learning about ASGI servers and HTTP protocol implementations.
- Fun and unconventional HTTP responses.

It is not intended to replace standard HTTP status codes in production APIs.

## Credits

This project is inspired by the original work:

[joho/7XX-rfc](https://github.com/joho/7XX-rfc)

The original specification provides the humorous and experimental 7XX status code definitions used by this service.

**Special thanks** to the original contributors for creating and maintaining the specification.

## Licensing

**7xx-service** uses a **dual-licensing approach** to distinguish original application code from **third-party catalog data**.

### Application source code

The original application source code is licensed under the MIT License.

See the root LICENSE file.

### 7XX Status Code Catalog

The status code catalog in the data/ directory is based on the original work by Joho:

https://github.com/joho/7XX-rfc

The catalog is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).

See [data/LICENSE](https://github.com/nico-tinico/7xx-service/blob/main/data/LICENSE) for the full license and [data/README.md](https://github.com/nico-tinico/7xx-service/blob/main/data/README.md) for attribution details.

The MIT License does not apply to third-party catalog data.

**Commercial use of the catalog is not permitted under CC BY-NC-SA 4.0 without separate authorization from the relevant rights holder.**

<p align="center">
<b>Because sometimes HTTP 500 just isn't enough.</b>
</p>
