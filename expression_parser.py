from pathlib import Path
import re


def get_expressions_to_remove(
    semantic_folder,
    reachable_tables
):
    """
    Returns expressions that are not
    referenced by any surviving table.
    """

    expressions_file = (
        Path(semantic_folder)
        / "definition"
        / "expressions.tmdl"
    )

    if not expressions_file.exists():

        return []

    text = expressions_file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    expression_names = []

    for line in text.splitlines():

        stripped = line.strip()

        if not stripped.startswith(
            "expression "
        ):
            continue

        expression_name = (
            stripped
            .replace(
                "expression ",
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

        expression_names.append(
            expression_name
        )

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    surviving_text = ""

    for table_file in tables_folder.rglob(
        "*.tmdl"
    ):

        table_name = (
            table_file.stem
            .strip()
            .strip("'")
            .strip('"')
            .casefold()
        )

        if table_name not in {
            t.casefold()
            for t in reachable_tables
        }:
            continue

        try:

            surviving_text += (
                table_file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )
            )

        except Exception:

            continue

    expressions_to_remove = []

    for expression in expression_names:

        #
        # If the expression name never appears
        # in any surviving table, remove it.
        #
        if expression not in surviving_text:

            expressions_to_remove.append(
                expression
            )

    return sorted(
        expressions_to_remove
    )