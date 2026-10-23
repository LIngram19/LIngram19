from pathlib import Path


def remove_expressions(
    semantic_folder,
    expressions_to_remove,
    apply_changes=False
):

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

    lines = text.splitlines(
        keepends=True
    )

    blocks = []
    current = []

    for line in lines:

        stripped = line.lstrip()

        if (
            stripped.startswith(
                "expression "
            )
            and current
        ):

            blocks.append(
                "".join(current)
            )

            current = []

        current.append(
            line
        )

    if current:

        blocks.append(
            "".join(current)
        )

    removed = []
    remaining = []

    for block in blocks:

        first_line = (
            block.splitlines()[0]
            .strip()
        )

        expression_name = (
            first_line
            .replace(
                "expression ",
                ""
            )
            .split(
                "=",
                1
            )[0]
            .strip()
            .strip("'")
            .strip('"')
        )

        if expression_name in expressions_to_remove:

            removed.append(
                expression_name
            )

        else:

            remaining.append(
                block
            )

    if apply_changes:

        expressions_file.write_text(
            "".join(remaining),
            encoding="utf-8"
        )

    return removed