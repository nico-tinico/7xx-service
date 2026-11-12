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
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:

```
http://localhost:8000
```

Interactive API documentation:

-Swagger UI: http://localhost:8000/docs
-ReDoc: http://localhost:8000/redoc

## API Reference

| Method | Endpoint | Description                       |
| ------ | -------- | --------------------------------- |
| GET    | /        | Generate a random 7XX response    |
| GET    | /random  | Generate a random 7XX response    |
| GET    | /codes   | List all available 7XX codes      |
| GET    | /health  | Check service health              |
| GET    | /{code}  | Return a specific 7XX status code |

### Random status code

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

### Request a specific status code

Retrieve a specific 7XX status code:

```
curl -i http://localhost:8000/701
```

The service returns the requested code if it exists in the catalog.

Unknown codes return a standard HTTP 404 response.

### List available status codes

Retrieve the complete catalog:

```
curl http://localhost:8000/codes
```

Example response:

```
{
  "count": 2,
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

The example above is **illustrative**; the actual catalog may contain additional entries.

### Health check

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
