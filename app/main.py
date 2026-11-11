import random

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.catalog import load_catalog
from app.uvicorn_7xx import register_7xx_statuses

app = FastAPI(
    title="7XX Service",
    description="Random HTTP 7XX status code generator",
    version="1.0.0",
)

CODES = load_catalog()

register_7xx_statuses(CODES)


def make_response(code: int) -> JSONResponse:
    description = CODES[code]

    return JSONResponse(
        status_code=code,
        content={
            "status": code,
            "message": description,
            "series": "7XX",
        },
        headers={
            "X-7XX-Message": description,
            "Cache-Control": "no-store",
        },
    )


@app.get("/", include_in_schema=False)
@app.get("/random")
def random_status():
    code = random.choice(tuple(CODES))
    return make_response(code)


@app.get("/codes")
def list_codes():
    return {
        "count": len(CODES),
        "codes": [
            {
                "status": code,
                "message": description,
            }
            for code, description in CODES.items()
        ],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "available_codes": len(CODES),
    }


@app.get("/{code}")
def specific_status(code: int):
    if code not in CODES:
        raise HTTPException(
            status_code=404,
            detail=f"7XX status code {code} not found",
        )

    return make_response(code)
