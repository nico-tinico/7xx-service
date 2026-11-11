7XX Service

A random HTTP 7XX status code generator, powered by Python and FastAPI.

Inspired by joho/7XX-rfc.

Features
Returns a random 7XX HTTP status code.
Uses real HTTP response status codes.
JSON response payloads.
Supports requesting a specific status code.
Lists all available status codes.
Automatically parses the original RFC document.
Docker and Docker Compose support.
Automated tests with pytest.
GitHub Actions CI.
Requirements
Python 3.12+
Docker (optional)
Quick start

Clone the repository:

bash
git clone https://github.com/YOUR_USERNAME/7xx-service.git
cd 7xx-service


Create a virtual environment:

bash
python -m venv .venv
source .venv/bin/activate


Install dependencies:

bash
pip install -r requirements.txt


Start the service:

bash
uvicorn app.main:app --host 0.0.0.0 --port 8000

API
Method	Endpoint	Description
GET	/	Random 7XX response
GET	/random	Random 7XX response
GET	/codes	List available codes
GET	/health	Health check
GET	/{code}	Return a specific 7XX code
Example response
http
HTTP/1.1 725
Content-Type: application/json

json
{
  "status": 725,
  "message": "It works on my machine",
  "series": "7XX"
}

Random response
bash
curl -i http://localhost:8000/random

Specific status code
bash
curl -i http://localhost:8000/701

List available codes
bash
curl http://localhost:8000/codes

Health check
bash
curl http://localhost:8000/health

Docker

Build and start:

bash
docker compose up --build -d


Stop:

bash
docker compose down


View logs:

bash
docker compose logs -f


The service listens on port 8000.

Update the RFC catalog

The catalog is based on the original 7XX RFC repository.

To download the latest version:

bash
python -m scripts.update_catalog


Restart the service after updating the catalog.

Tests
bash
pytest -v

Technical notes

The 7XX codes are an experimental proposal, not standard HTTP status codes. Current HTTP semantics define valid status codes in the range 100–599.

Some HTTP clients, proxies, gateways and monitoring systems may reject or normalize 7XX responses.

This project is intended for experimentation, demonstrations and compatibility testing.

Credits

Original specification: joho/7XX-rfc.

The original specification is distributed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license. See the original repository's LICENSE.md for its terms.

License

The application code and the upstream RFC data have different licensing considerations. Consult the upstream license before redistributing the catalog or using the project commercially.