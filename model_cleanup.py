from pathlib import Path
import json
import re


def get_used_query_groups(
    semantic_folder
):

    expressions_file = (
        Path(semantic_folder)
        / "definition"
        / "expressions.tmdl"
    )

    if not expressions_file.exists():

        return set()

    text = expressions_file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    used_groups = set()

    for line in text.splitlines():

        stripped = line.strip()

        if not stripped.startswith(
            "queryGroup:"
        ):
            continue

        group_name = (
            stripped
            .replace(
                "queryGroup:",
                "",
                1
            )
            .strip()
            .strip("'")
            .strip('"')
        )

        parts = group_name.split(
            "\\"
        )

        #
        # Keep group and all parents
        #
        for i in range(
            1,
            len(parts) + 1
        ):

            parent = "\\".join(
                parts[:i]
            )

            used_groups.add(
                parent.casefold()
            )

    return used_groups


def cleanup_model(
    semantic_folder,
    apply_changes=False
):

    model_file = (
        Path(semantic_folder)
        / "definition"
        / "model.tmdl"
    )

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    if not model_file.exists():

        return {
            "removed_refs": [],
            "remaining_tables": []
        }

    #
    # Build surviving table inventory
    #
    existing_tables = {}

    for table_file in tables_folder.rglob(
        "*.tmdl"
    ):

        table_name = (
            table_file.stem
            .replace("%2F", "/")
            .replace("%3F", "?")
        )

        existing_tables[
            table_name.casefold()
        ] = table_name

    text = model_file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    removed_refs = []

    #
    # ---------------------------------------------------------
    # CLEAN REF TABLES
    # ---------------------------------------------------------
    #
    output = []

    for line in text.splitlines():

        stripped = line.strip()

        if stripped.startswith(
            "ref table "
        ):

            table_name = (
                stripped
                .replace(
                    "ref table ",
                    "",
                    1
                )
                .strip()
                .strip("'")
                .strip('"')
            )

            if (
                table_name.casefold()
                not in existing_tables
            ):

                removed_refs.append(
                    table_name
                )

                continue

        output.append(
            line
        )

    text = "\n".join(
        output
    )

    #
    # ---------------------------------------------------------
    # CLEAN PBI_QUERYORDER
    # ---------------------------------------------------------
    #
    pattern = (
        r'annotation PBI_QueryOrder = (\[.*?\])'
    )

    match = re.search(
        pattern,
        text,
        flags=re.DOTALL
    )

    if match:

        try:

            current_order = (
                json.loads(
                    match.group(1)
                )
            )

            surviving_order = [
                item
                for item in current_order
                if item.casefold()
                in existing_tables
            ]

            replacement = (
                "annotation PBI_QueryOrder = "
                + json.dumps(
                    surviving_order,
                    ensure_ascii=False
                )
            )

            text = re.sub(
                pattern,
                replacement,
                text,
                flags=re.DOTALL
            )

        except Exception:

            pass

    #
    # QUERYGROUP CLEANUP
    #
    used_groups = (
        get_used_query_groups(
            semantic_folder
        )
    )

    lines = text.splitlines()

    output = []

    i = 0

    while i < len(lines):

        line = lines[i]

        stripped = line.strip()

        if stripped.startswith(
            "queryGroup "
        ):

            block = [line]

            i += 1

            while (
                i < len(lines)
                and not lines[i].startswith(
                    "queryGroup "
                )
                and not lines[i].startswith(
                    "annotation "
                )
                and not lines[i].startswith(
                    "ref table "
                )
                and not lines[i].startswith(
                    "ref role "
                )
                and not lines[i].startswith(
                    "ref cultureInfo "
                )
            ):

                block.append(
                    lines[i]
                )

                i += 1

            group_name = (
                block[0]
                .replace(
                    "queryGroup ",
                    "",
                    1
                )
                .strip()
                .strip("'")
                .strip('"')
            )

            if (
                group_name.casefold()
                in used_groups
            ):

                output.extend(
                    block
                )

            continue

        output.append(
            line
        )

        i += 1

    text = "\n".join(
        output
    )
    #
    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------
    #
    if apply_changes:

        model_file.write_text(
            text,
            encoding="utf-8"
        )

    return {
        "removed_refs": sorted(
            removed_refs
        ),
        "remaining_tables": sorted(
            existing_tables.values()
        )
    }