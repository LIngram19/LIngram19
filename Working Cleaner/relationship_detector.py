from typing import Set
import re

from reference_remover import MODEL_ROOT
from unused_table_remover import normalize_name

def extract_table_name(
    column_reference: str,
) -> str | None:

    if not column_reference:
        return None

    column_reference = column_reference.strip()

    bracket_match = re.match(
        r"(?:'([^']+)'|([^\[]+))\s*\[",
        column_reference,
    )

    if bracket_match:
        return normalize_name(
            bracket_match.group(1)
            or bracket_match.group(2)
        )

    if "." in column_reference:
        return normalize_name(
            column_reference.rsplit(
                ".",
                1,
            )[0]
        )

    return None


def get_relationships_to_remove(
    unused_tables: Set[str],
) -> Set[str]:

    relationship_file = (
        MODEL_ROOT
        / "definition"
        / "relationships.tmdl"
    )

    unused_tables = {
        normalize_name(name) or name
        for name in unused_tables
    }

    lines = relationship_file.read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines()

    relationships_to_remove: Set[str] = set()

    i = 0

    while i < len(lines):

        if not lines[i].strip().startswith(
            "relationship "
        ):
            i += 1
            continue

        relationship_id = (
            lines[i]
            .strip()
            .replace(
                "relationship ",
                "",
            )
        )

        block_end = i + 1

        while block_end < len(lines):

            next_line = lines[block_end]

            if (
                next_line.strip()
                and not next_line.startswith(
                    (" ", "\t")
                )
            ):
                break

            block_end += 1

        block_text = "\n".join(
            lines[i:block_end]
        )

        relationship_tables: Set[str] = set()

        from_match = re.search(
            r"fromColumn:\s*(.+)",
            block_text,
            flags=re.IGNORECASE,
        )

        if from_match:

            table_name = extract_table_name(
                from_match.group(1)
            )

            if table_name:
                relationship_tables.add(
                    table_name
                )

        to_match = re.search(
            r"toColumn:\s*(.+)",
            block_text,
            flags=re.IGNORECASE,
        )

        if to_match:

            table_name = extract_table_name(
                to_match.group(1)
            )

            if table_name:
                relationship_tables.add(
                    table_name
                )

        if relationship_tables & unused_tables:

            relationships_to_remove.add(
                relationship_id
            )

        i = block_end

    return relationships_to_remove