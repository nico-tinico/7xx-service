import http.client
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app, CODES


client = TestClient(app)


# --------------------------------------------------
# Unit tests: FastAPI
# --------------------------------------------------

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["available_codes"] == len(CODES)


def test_catalog():
    response = client.get("/codes")

    assert response.status_code == 200
    assert response.json()["count"] == len(CODES)


def test_random_returns_defined_code():
    response = client.get("/random")

    assert response.status_code in CODES

    body = response.json()

    assert body["status"] == response.status_code
    assert body["series"] == "7XX"
    assert body["message"] == CODES[response.status_code]


def test_specific_code():
    code = next(iter(CODES))

    response = client.get(f"/{code}")

    assert response.status_code == code
    assert response.json()["message"] == CODES[code]


def test_unknown_code():
    response = client.get("/700")

    assert response.status_code == 404


def test_catalog_has_only_7xx():
    assert all(700 <= code <= 799 for code in CODES)


def test_catalog_has_no_empty_descriptions():
    assert all(description.strip() for description in CODES.values())


# --------------------------------------------------
# Integration tests: real Uvicorn HTTP server
# --------------------------------------------------

@pytest.fixture(scope="module")
def uvicorn_server():
    project_root = Path(__file__).resolve().parent.parent

    # Find an available local port.
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--http",
        "h11",
        "--log-level",
        "warning",
    ]

    process = subprocess.Popen(
        command,
        cwd=project_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    # Wait until the server is ready.
    ready = False

    try:
        for _ in range(100):
            if process.poll() is not None:
                pytest.fail(
                    f"Uvicorn exited with code {process.returncode}"
                )

            try:
                connection = http.client.HTTPConnection(
                    "127.0.0.1",
                    port,
                    timeout=1,
                )
                connection.request("GET", "/health")
                response = connection.getresponse()
                response.read()
                connection.close()

                if response.status == 200:
                    ready = True
                    break

            except OSError:
                pass

            time.sleep(0.1)

        if not ready:
            pytest.fail("Uvicorn did not start within 10 seconds")

        yield "127.0.0.1", port

    finally:
        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def test_real_http_701(uvicorn_server):
    host, port = uvicorn_server

    connection = http.client.HTTPConnection(host, port, timeout=5)
    connection.request("GET", "/701")

    response = connection.getresponse()
    body = json.loads(response.read().decode("utf-8"))

    assert response.status == 701
    assert response.reason == "7XX"
    assert body["status"] == 701
    assert body["message"] == CODES[701]
    assert body["series"] == "7XX"
    assert response.getheader("Content-Type").startswith(
        "application/json"
    )
    assert response.getheader("Cache-Control") == "no-store"

    connection.close()


def test_real_http_random(uvicorn_server):
    host, port = uvicorn_server

    connection = http.client.HTTPConnection(host, port, timeout=5)
    connection.request("GET", "/random")

    response = connection.getresponse()
    body = json.loads(response.read().decode("utf-8"))

    assert response.status in CODES
    assert response.reason == "7XX"
    assert body["status"] == response.status
    assert body["message"] == CODES[response.status]
    assert body["series"] == "7XX"

    connection.close()