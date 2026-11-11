"""
Compatibility patch for experimental 7XX status codes.

Uvicorn's h11 backend maintains an internal mapping of
HTTP status codes to reason phrases. We extend it with
the codes loaded from the 7XX catalog.
"""


def register_7xx_statuses(codes: dict[int, str]) -> None:
    from uvicorn.protocols.http import h11_impl

    for code in codes:
        if not 700 <= code <= 799:
            continue

        # h11 expects a bytes reason phrase.
        # Keep it generic: the full description is in JSON.
        h11_impl.STATUS_PHRASES[code] = b"7XX"