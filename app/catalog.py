import html
import re
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RFC_FILE = ROOT / "data" / "7xx.md"

ENTRY_RE = re.compile(
    r"^\s*(?:[-*]|o)\s+(7\d{2})\s+-\s+(.+?)\s*$"
)


def parse_catalog(content: str) -> dict[int, str]:
    codes: dict[int, str] = {}
    current_code = None
    current_description = []

    def save_current():
        nonlocal current_code, current_description

        if current_code is None:
            return

        description = html.unescape(
            " ".join(current_description)
        ).strip()

        if description:
            previous = codes.get(current_code)

            if previous is None:
                codes[current_code] = description
            elif previous != description:
                warnings.warn(
                    f"Duplicate code {current_code}: "
                    f"keeping {previous!r}, ignoring {description!r}"
                )

        current_code = None
        current_description = []

    for line in content.splitlines():
        match = ENTRY_RE.match(line)

        if match:
            save_current()
            current_code = int(match.group(1))
            current_description = [match.group(2)]
            continue

        if current_code is not None:
            stripped = line.strip()

            if stripped:
                current_description.append(stripped)
            else:
                save_current()

    save_current()

    return dict(sorted(codes.items()))


def load_catalog() -> dict[int, str]:
    if not RFC_FILE.is_file():
        raise RuntimeError(
            f"Missing RFC catalog: {RFC_FILE}"
        )

    content = RFC_FILE.read_text(encoding="utf-8")
    catalog = parse_catalog(content)

    if not catalog:
        raise RuntimeError(
            "No 7XX codes found in RFC catalog"
        )

    return catalog
