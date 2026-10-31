from __future__ import annotations

from pathlib import Path
from typing import Set
from unused_table_detector import (
    get_unused_tables,
)

from relationship_detector import (
    get_relationships_to_remove,
)

MODEL_ROOT = Path(
    r"c:\Users\LINGRAM\Documents\PBI Test Files\5 Year Look Back.SemanticModel"
)


def remove_relationships(
    relationship_ids: Set[str],
) -> Set[str]:

    relationship_file = (
        MODEL_ROOT
        / "definition"
        / "relationships.tmdl"
    )

    lines = relationship_file.read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines()

    output = []

    removed: Set[str] = set()

    i = 0

    while i < len(lines):

        if not lines[i].strip().startswith(
      "relationship "
        ):
            output.append(lines[i])
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

        if relationship_id in relationship_ids:

            print(
                f"Removing: "
                f"{relationship_id}"
            )

            removed.add(
                relationship_id
            )

            i = block_end
            continue

        output.extend(
            lines[i:block_end]
        )

        i = block_end

    relationship_file.write_text(
        "\n".join(output).rstrip()
        + "\n",
        encoding="utf-8",
    )

    return removed


def main():

    unused_tables = get_unused_tables()

    relationship_ids = (
        get_relationships_to_remove(
            unused_tables
        )
    )

    removed = remove_relationships(
        relationship_ids
    )

    print()
    print("=" * 60)
    print("REMOVED RELATIONSHIPS")
    print("=" * 60)

    for relationship in sorted(
        removed
    ):
        print(relationship)

    print()
    print(
        f"Removed: {len(removed)}"
    )