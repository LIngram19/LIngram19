from pathlib import Path


def cleanup_roles(
    semantic_folder,
    apply_changes=False
):

    roles_folder = (
        Path(semantic_folder)
        / "definition"
        / "roles"
    )

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    #
    # Surviving tables
    #
    surviving_tables = set()

    for table_file in tables_folder.rglob(
        "*.tmdl"
    ):

        surviving_tables.add(
            table_file.stem.casefold()
        )

    removed_permissions = []

    if not roles_folder.exists():

        return {
            "removed_permissions": [],
            "roles_updated": []
        }

    updated_roles = []

    for role_file in roles_folder.rglob(
        "*.tmdl"
    ):

        text = role_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        lines = text.splitlines(
            keepends=True
        )

        output = []

        i = 0

        role_changed = False

        while i < len(lines):

            line = lines[i]

            stripped = (
                line.strip()
            )

            #
            # tablePermission block
            #
            if stripped.startswith(
                "tablePermission "
            ):

                table_name = (
                    stripped
                    .replace(
                        "tablePermission ",
                        "",
                        1
                    )
                    .strip()
                    .strip("'")
                    .strip('"')
                )

                block = [line]

                i += 1

                while (
                    i < len(lines)
                    and (
                        lines[i].startswith(" ")
                        or lines[i].startswith("\t")
                    )
                ):

                    block.append(
                        lines[i]
                    )

                    i += 1

                if (
                    table_name.casefold()
                    not in surviving_tables
                ):

                    removed_permissions.append(
                        f"{role_file.stem}: "
                        f"{table_name}"
                    )

                    role_changed = True

                    continue

                output.extend(
                    block
                )

                continue

            output.append(
                line
            )

            i += 1

        if (
            role_changed
            and apply_changes
        ):

            role_file.write_text(
                "".join(output),
                encoding="utf-8"
            )

            updated_roles.append(
                role_file.stem
            )

    return {
        "removed_permissions":
            sorted(
                removed_permissions
            ),
        "roles_updated":
            sorted(
                set(updated_roles)
            )
    }
