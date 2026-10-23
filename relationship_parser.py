from pathlib import Path


def get_relationships_to_remove(
    semantic_folder,
    unused_tables
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

    unused_tables = {
        table.casefold()
        for table in unused_tables
    }

    relationships_to_remove = []

    for block in blocks:

        block_lower = (
            block.casefold()
        )

        relationship_name = (
            block.splitlines()[0]
            .replace(
                "relationship ",
                ""
            )
            .strip()
        )

        tables_found = set()

        for line in block.splitlines():

            stripped = line.strip()

            if not (
                stripped.startswith(
                    "fromColumn:"
                )
                or stripped.startswith(
                    "toColumn:"
                )
            ):
                continue

            value = (
                stripped
                .split(
                    ":",
                    1
                )[1]
                .strip()
            )

            #
            # Examples:
            #
            # 'Cost Center Hierarchy'.'Mgmt Adj'
            # Currency.Join
            # calendar.Date
            #
            if "." not in value:
                continue

            table_name = (
                value
                .split(
                    ".",
                    1
                )[0]
                .strip()
                .strip("'")
                .strip('"')
                .casefold()
            )

            tables_found.add(
                table_name
            )

        if tables_found & unused_tables:

            relationships_to_remove.append(
                relationship_name
            )

    return sorted(
        relationships_to_remove
    )
