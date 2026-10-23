from pathlib import Path


def remove_relationships(
    semantic_folder,
    relationships_to_remove,
    apply_changes=False
):

    relationships_file = (
        Path(semantic_folder)
        / "definition"
        / "relationships.tmdl"
    )

    if not relationships_file.exists():

        return []

    text = relationships_file.read_text(
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
                "relationship "
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

        relationship_name = (
            first_line
            .replace(
                "relationship ",
                ""
            )
            .strip()
        )

        if relationship_name in relationships_to_remove:

            removed.append(
                relationship_name
            )

        else:

            remaining.append(
                block
            )

    if apply_changes:

        relationships_file.write_text(
            "".join(remaining),
            encoding="utf-8"
        )

    return removed