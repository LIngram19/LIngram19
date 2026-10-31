from __future__ import annotations

from pathlib import Path
from typing import Set

from expression_detector import (
    get_unused_expressions,
)

MODEL_ROOT = Path(
    r"c:\Users\LINGRAM\Documents\PBI Test Files\5 Year Look Back.SemanticModel"
)


def remove_expressions(
    expression_names: Set[str],
) -> Set[str]:

    expressions_file = (
        MODEL_ROOT
        / "definition"
        / "expressions.tmdl"
    )

    lines = expressions_file.read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines()

    output = []

    removed: Set[str] = set()

    i = 0

    while i < len(lines):

        stripped = lines[i].strip()

        if not stripped.startswith(
            "expression "
        ):
            output.append(lines[i])
            i += 1
            continue

        name_part = stripped[
            len("expression "):
        ]

        expression_name = (
            name_part.split(
                "=",
                1,
            )[0]
            .strip()
            .strip("'")
            .strip('"')
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

        if expression_name in expression_names:

            print(
                f"Removing expression: "
                f"{expression_name}"
            )

            removed.add(
                expression_name
            )

            i = block_end
            continue

        output.extend(
            lines[i:block_end]
        )

        i = block_end

    expressions_file.write_text(
        "\n".join(output).rstrip()
        + "\n",
        encoding="utf-8",
    )

    return removed


def main():

    unused = (
        get_unused_expressions()
    )

    removed = remove_expressions(
        unused
    )

    print()
    print("=" * 60)
    print("REMOVED EXPRESSIONS")
    print("=" * 60)

    for expression in sorted(
        removed
    ):
        print(expression)

    print()
    print(
        f"Removed: {len(removed)}"
    )


if __name__ == "__main__":
    main()