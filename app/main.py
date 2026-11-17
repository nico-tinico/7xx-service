import html
import json
import random

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response

from app.catalog import load_catalog
from app.uvicorn_7xx import register_7xx_statuses

app = FastAPI(
    title="7XX Service",
    description="Random HTTP 7XX status code generator",
    version="1.0.0",
)

CODES = load_catalog()
register_7xx_statuses(CODES)

SUPPORTED_MEDIA_TYPES = (
    "application/json",
    "text/plain",
    "text/html",
)


def negotiate_content_type(request: Request) -> str:
    """Select the best supported response format from Accept."""

    accept = request.headers.get("accept", "").strip()

    if not accept or accept == "*/*":
        return "application/json"

    matches = []

    for position, item in enumerate(accept.split(",")):
        parts = item.strip().split(";")
        media_type = parts[0].strip().lower()
        quality = 1.0

        for parameter in parts[1:]:
            key, separator, value = parameter.strip().partition("=")

            if separator and key.strip().lower() == "q":
                try:
                    quality = float(value.strip())
                except ValueError:
                    quality = 0.0

        if not 0 < quality <= 1:
            continue

        for preference, supported in enumerate(SUPPORTED_MEDIA_TYPES):
            major, minor = supported.split("/", 1)
            accepted_major, accepted_minor = media_type.split("/", 1)

            if media_type == supported:
                specificity = 2
            elif accepted_major == major and accepted_minor == "*":
                specificity = 1
            elif media_type == "*/*":
                specificity = 0
            else:
                continue

            matches.append(
                (quality, specificity, -position, -preference, supported)
            )

    if not matches:
        raise HTTPException(
            status_code=406,
            detail="No acceptable representation available.",
        )

    return max(matches)[-1]

def render_response(
    request: Request,
    content: dict,
    status_code: int = 200,
    headers: dict | None = None,
) -> Response:
    """Render a payload using the negotiated representation."""

    media_type = negotiate_content_type(request)

    response_headers = {
        "Vary": "Accept",
        **(headers or {}),
    }

    if media_type == "application/json":
        return JSONResponse(
            content=content,
            status_code=status_code,
            headers=response_headers,
        )

    if media_type == "text/plain":
        if "status" in content and "message" in content:
            body = f"{content['status']} - {content['message']}\n"
        else:
            body = json.dumps(content, indent=2, ensure_ascii=False)

        return PlainTextResponse(
            content=body,
            status_code=status_code,
            headers=response_headers,
        )

    body = html.escape(
        json.dumps(content, indent=2, ensure_ascii=False)
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>7XX Service</title>
    <style>
        body {{
            font-family: system-ui, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            background: #111827;
            color: #f9fafb;
        }}
        pre {{
            padding: 20px;
            background: #1f2937;
            border-radius: 8px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <h1>7XX Service</h1>
    <pre>{body}</pre>
</body>
</html>"""

    return HTMLResponse(
        content=page,
        status_code=status_code,
        headers=response_headers,
    )


def get_random_code(seed: int | None = None) -> int:
    """Return a random catalog code, optionally using a deterministic seed."""

    rng = random.Random(seed)
    return rng.choice(tuple(CODES))


def make_response(code: int, request: Request) -> JSONResponse:
    description = CODES[code]

    return render_response(
        request=request,
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
def random_status(
    request: Request,
    seed: int | None = Query(default=None)
):
    code = get_random_code(seed)
    return make_response(code, request)


@app.get("/random/info")
def random_info(
    request: Request,
    seed: int | None = Query(default=None),
):
    code = get_random_code(seed)

    return render_response(
        request=request,
        content={
            "status": code,
            "message": CODES[code],
            "series": "7XX",
        },
        headers={"Cache-Control": "no-store"},
    )


@app.get("/codes")
def list_codes(
    request: Request,
    search: str | None = Query(default=None, min_length=1),
    min_code: int | None = Query(default=None, alias="min", ge=700, le=799),
    max_code: int | None = Query(default=None, alias="max", ge=700, le=799),
    sort: str = Query(default="asc", pattern="^(asc|desc)$"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    if min_code is not None and max_code is not None:
        if min_code > max_code:
            raise HTTPException(
                status_code=422,
                detail="'min' cannot be greater than 'max'.",
            )

    filtered = [
        {"status": code, "message": description}
        for code, description in CODES.items()
        if (min_code is None or code >= min_code)
        and (max_code is None or code <= max_code)
        and (
            search is None
            or search.casefold() in description.casefold()
            or search in str(code)
        )
    ]

    filtered.sort(
        key=lambda item: item["status"],
        reverse=(sort == "desc"),
    )

    total = len(filtered)
    paginated = filtered[offset:offset + limit]
    
    return render_response(
        request=request,
        content={
            "count": len(paginated),
            "total": total,
            "limit": limit,
            "offset": offset,
            "codes": paginated,
        },
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "available_codes": len(CODES),
    }


@app.get("/{code}")
def specific_status(code: int, request: Request):
    if code not in CODES:
        raise HTTPException(
            status_code=404,
            detail=f"7XX status code {code} not found",
        )

    return make_response(code, request)
