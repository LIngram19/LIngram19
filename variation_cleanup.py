from pathlib import Path
import re


def cleanup_variations(
    semantic_folder,
    apply_changes=False
):

    relationships_file = (
        Path(semantic_folder)
        / "definition"
        / "relationships.tmdl"
    )

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    surviving_relationships = set()

    if relationships_file.exists():

        text = relationships_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        surviving_relationships = set(
            re.findall(
                r"relationship\s+([a-f0-9\-]{36})",
                text,
                flags=re.IGNORECASE
            )
        )

    removed_variations = []

    for table_file in tables_folder.rglob(
        "*.tmdl"
    ):

        try:

            lines = table_file.read_text(
                encoding="utf-8",
                errors="ignore"
            ).splitlines(
                keepends=True
            )

        except Exception:

            continue

        output = []

        i = 0

        modified = False

        while i < len(lines):

            line = lines[i]

            stripped = line.strip()

            if stripped.startswith(
                "variation "
            ):

                block = [line]

                relationship_id = None

                i += 1

                while (
                    i < len(lines)
                    and (
                        lines[i].startswith("\t\t")
                        or lines[i].startswith("        ")
                    )
                ):

                    block.append(
                        lines[i]
                    )

                    rel_match = re.search(
                        r"relationship:\s+([a-f0-9\-]{36})",
                        lines[i],
                        flags=re.IGNORECASE
                    )

                    if rel_match:

                        relationship_id = (
                            rel_match.group(1)
                        )

                    i += 1

                if (
                    relationship_id
                    and relationship_id
                    not in surviving_relationships
                ):

                    removed_variations.append(
                        (
                            table_file.stem,
                            relationship_id
                        )
                    )

                    modified = True

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
            modified
            and apply_changes
        ):

            table_file.write_text(
                "".join(output),
                encoding="utf-8"
            )

    return removed_variations