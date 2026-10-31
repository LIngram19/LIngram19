from __future__ import annotations

from pathlib import Path
from typing import Set


MODEL_ROOT = Path(
    r"c:\Users\LINGRAM\Documents\PBI Test Files\5 Year Look Back.SemanticModel"
)


def normalize_name(value: str | None) -> str | None:
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.replace("'", "").replace('"', "")

    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]

    return value.strip() or None


def remove_model_ref(
    model_tmdl: Path,
    table_names_to_remove: Set[str],
) -> int:

    text = model_tmdl.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    lines = text.splitlines()

    new_lines = []
    removed_count = 0

    for line in lines:

        stripped = line.strip()

        if stripped.startswith("ref table "):

            table_name = normalize_name(
                stripped[len("ref table "):].strip()
            )

            if table_name in table_names_to_remove:
                print(f"Removing model ref: {table_name}")
                removed_count += 1
                continue

        new_lines.append(line)

    model_tmdl.write_text(
        "\n".join(new_lines).rstrip() + "\n",
        encoding="utf-8",
    )

    return removed_count


def main():

    model_tmdl = (
        MODEL_ROOT
        / "definition"
        / "model.tmdl"
    )

    #
    # Replace with tables identified by your usage detector.
    #
    table_names_to_remove = {
        "LocalDateTable_12345678",
        "Unused Table",
        "Old Facts",
    }

    removed = remove_model_ref(
        model_tmdl,
        table_names_to_remove,
    )

    print()
    print(f"Removed {removed} model references")
    print()


if __name__ == "__main__":
    main()