from pathlib import Path
from urllib.parse import unquote
import re


# ============================================================
# HELPERS
# ============================================================

def normalize_name(
    text
):
    return (
        str(text)
        .strip()
        .strip("'")
        .strip('"')
        .casefold()
    )


# ============================================================
# INVENTORY
# ============================================================

def build_inventory(
    semantic_folder
):

    inventory = {}

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    files = list(
        tables_folder.rglob(
            "*.tmdl"
        )
    )

    print(
        f"TMDL Files Found: "
        f"{len(files)}"
    )

    for table_file in files:

        try:

            text = table_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception:

            continue

        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        table_name = normalize_name(
            unquote(
                table_file.stem
            )
        )

        inventory[
            table_name
        ] = {
            "type": "table",
            "table": table_name,
            "name": table_name,
            "helper": table_name,
            "dax": None
        }

        # ----------------------------------------------------
        # MEASURES
        # ----------------------------------------------------

        measure_blocks = re.finditer(
            r"measure\s+(?:'([^']+)'|([^\r\n=]+)).*?(?=\n\s*measure\s+(?:'|[^\r\n=])|\Z)",
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

        for match in measure_blocks:

            measure_name = (
                match.group(1)
                or match.group(2)
            )

            measure_name = normalize_name(
                measure_name.strip()
            )

            helper_name = (
                f"{table_name}."
                f"{measure_name}"
            )

            inventory[
                helper_name
            ] = {
                "type": "measure",
                "table": table_name,
                "name": measure_name,
                "helper": helper_name,
                "dax": match.group(0)
            }

        # ----------------------------------------------------
        # COLUMNS
        # ----------------------------------------------------

        for line in text.splitlines():

            stripped = line.strip()

            if not stripped.startswith(
                "column "
            ):
                continue

            column_name = (
                stripped
                .replace(
                    "column ",
                    "",
                    1
                )
                .split(
                    "=",
                    1
                )[0]
                .strip()
                .strip("'")
                .strip('"')
            )

            column_name = normalize_name(
                column_name
            )

            helper_name = (
                f"{table_name}."
                f"{column_name}"
            )

            inventory[
                helper_name
            ] = {
                "type": "column",
                "table": table_name,
                "name": column_name,
                "helper": helper_name,
                "dax": None
            }

    # ----------------------------------------------------
    # NAME LOOKUP
    # ----------------------------------------------------

    name_lookup = {}

    for item in inventory.values():

        if item["type"] not in (
            "measure",
            "column"
        ):
            continue

        name_lookup[
            item["name"]
        ] = item["helper"]

    return (
        inventory,
        name_lookup
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    inventory, name_lookup = (
            build_inventory(
                r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.SemanticModel"
            )
        )

    tables = [
        x
        for x in inventory.values()
        if x["type"] == "table"
    ]

    measures = [
        x
        for x in inventory.values()
        if x["type"] == "measure"
    ]

    columns = [
        x
        for x in inventory.values()
        if x["type"] == "column"
    ]

    print()
    print(
        f"Tables: "
        f"{len(tables)}"
    )

    print(
        f"Measures: "
        f"{len(measures)}"
    )

    print(
        f"Columns: "
        f"{len(columns)}"
    )

    print()
    print(
        "Sample Measures"
    )
    print()

    print(
        "Lookup Test"
    )

    print(
        "-" * 60
    )

    print(
        name_lookup.get(
            "total nfe amount"
        )
    )

    print()
    print(
        "-" * 60
    )

    for item in measures[:20]:

        print(
            item["helper"]
        )