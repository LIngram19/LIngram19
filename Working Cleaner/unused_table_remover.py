from __future__ import annotations

import re
from pathlib import Path
from typing import Set

from report_usage_lib import (
    parse_table_name_from_file,
)

from unused_table_detector import (
    get_unused_tables,
)


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

def find_referenced_local_date_tables(
    table_file: Path,
) -> Set[str]:

    text = table_file.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    referenced_tables: Set[str] = set()

    patterns = [
        r"LocalDateTable_[A-Za-z0-9\-]+",
        r"DateTableTemplate_[A-Za-z0-9\-]+",
    ]

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            referenced_tables.add(
                match.group(0)
            )

    return referenced_tables

def remove_unused_tables(
    model_tables_dir: Path,
    unused_table_names: Set[str],
) -> Set[str]:

    unused_table_names = {
        normalize_name(name) or name
        for name in unused_table_names
    }

    removed_tables: Set[str] = set()

    for table_file in sorted(
        model_tables_dir.glob("*.tmdl")
    ):

        table_name = parse_table_name_from_file(
            table_file
        )

        if not table_name:
            continue

        normalized_name = (
            normalize_name(table_name)
            or table_name
        )

        if normalized_name in unused_table_names:

            #
            # Look for references to
            # LocalDateTable_* and
            # DateTableTemplate_* tables.
            #
            generated_tables = (
                find_referenced_local_date_tables(
                    table_file
                )
            )

            print(
                f"Removing: {normalized_name}"
            )

            table_file.unlink(
                missing_ok=True
            )

            removed_tables.add(
                normalized_name
            )

            #
            # Remove any generated date tables
            # referenced by this table.
            #
            for generated_table in generated_tables:

                generated_file = (
                    model_tables_dir
                    / f"{generated_table}.tmdl"
                )

                if generated_file.exists():

                    print(
                        f"Removing generated table: "
                        f"{generated_table}"
                    )

                    generated_file.unlink(
                        missing_ok=True
                    )

                    removed_tables.add(
                        generated_table
                    )

    return removed_tables



def main():

    model_tables_dir = (
        MODEL_ROOT
        / "definition"
        / "tables"
    )

    unused_tables = get_unused_tables()

    print()
    print("=" * 60)
    print("UNUSED TABLES DETECTED")
    print("=" * 60)

    for table_name in sorted(
        unused_tables
    ):
        print(table_name)

    print()
    print(
        f"Unused Tables Found: "
        f"{len(unused_tables)}"
    )
    print()

    removed_tables = remove_unused_tables(
        model_tables_dir,
        unused_tables,
    )

    print()
    print("=" * 60)
    print("REMOVED TABLES")
    print("=" * 60)

    for table_name in sorted(
        removed_tables
    ):
        print(table_name)

    print()
    print(
        f"Removed Tables: "
        f"{len(removed_tables)}"
    )
    print()


if __name__ == "__main__":
    main()