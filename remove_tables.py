from pathlib import Path


def remove_tables(
    semantic_folder,
    tables_to_remove,
    apply_changes=False
):

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    tables_to_remove = {
        table.casefold()
        for table in tables_to_remove
    }

    removed = []

    for table_file in tables_folder.rglob(
        "*.tmdl"
    ):

        table_name = (
            table_file.stem
            .strip("'")
            .strip('"')
            .casefold()
        )

        if table_name not in tables_to_remove:
            continue

        removed.append(
            table_name
        )

        if apply_changes:

            table_file.unlink()

    return sorted(
        removed
    )