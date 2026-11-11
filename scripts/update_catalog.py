from pathlib import Path
from urllib.request import Request, urlopen

from app.catalog import ROOT, parse_catalog

SOURCE = (
    "https://raw.githubusercontent.com/"
    "joho/7XX-rfc/master/7xx.md"
)

DESTINATION = ROOT / "data" / "7xx.md"


def main():
    request = Request(
        SOURCE,
        headers={"User-Agent": "7xx-service/1.0"},
    )

    print("Downloading original 7XX catalog...")

    with urlopen(request, timeout=20) as response:
        content = response.read().decode("utf-8")

    catalog = parse_catalog(content)

    if not catalog:
        raise RuntimeError(
            "Downloaded file contains no valid 7XX definitions"
        )

    DESTINATION.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    DESTINATION.write_text(content, encoding="utf-8")

    print("Catalog successfully updated!")
    print(f"Available codes: {len(catalog)}")
    print(f"Destination: {DESTINATION}")


if __name__ == "__main__":
    main()
