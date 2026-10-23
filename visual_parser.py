from pathlib import Path
import re

from model_parser import (
    normalize_name
)


def get_visual_refs(
    report_folder
):

    refs = set()

    report_folder = Path(
        report_folder
    )

    files = list(
        report_folder.rglob(
            "visual.json"
        )
    )

    print(
        f"Visuals Found: "
        f"{len(files)}"
    )

    for visual_file in files:

        try:

            text = visual_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception:

            continue

        matches = re.findall(
            r'"queryRef"\s*:\s*"([^"]+)"',
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            refs.add(
                normalize_name(
                    match
                )
            )

    return refs