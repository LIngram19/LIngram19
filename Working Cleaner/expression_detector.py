from __future__ import annotations

from pathlib import Path
from typing import Dict, Set
import re

MODEL_ROOT = Path(
    r"c:\Users\LINGRAM\Documents\PBI Test Files\5 Year Look Back.SemanticModel"
)


def normalize_name(value: str | None) -> str | None:

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.replace("'", "").replace('"', "")

    return value.strip() or None


def parse_expressions() -> Dict[str, str]:

    expressions_file = (
        MODEL_ROOT
        / "definition"
        / "expressions.tmdl"
    )

    lines = expressions_file.read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines()

    expressions: Dict[str, str] = {}

    i = 0

    while i < len(lines):

        stripped = lines[i].strip()

        if not stripped.startswith(
            "expression "
        ):
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

        j = i + 1

        while j < len(lines):

            next_line = lines[j]

            if (
                next_line.strip()
                and not next_line.startswith(
                    (" ", "\t")
                )
            ):
                break

            j += 1

        expressions[
            normalize_name(
                expression_name
            )
        ] = "\n".join(
            lines[i:j]
        )

        i = j

    return expressions


def build_expression_graph(
    expressions: Dict[str, str],
) -> Dict[str, Set[str]]:

    graph: Dict[str, Set[str]] = {
        name: set()
        for name in expressions
    }

    for expression_name, text in expressions.items():

        for dependency in expressions:

            if dependency == expression_name:
                continue

            quoted_pattern = (
                rf'#"{re.escape(dependency)}"'
            )

            bare_pattern = (
                rf"(?<![A-Za-z0-9_])"
                rf"{re.escape(dependency)}"
                rf"(?![A-Za-z0-9_])"
            )

            if re.search(
                quoted_pattern,
                text,
                flags=re.IGNORECASE,
            ):
                graph[
                    expression_name
                ].add(dependency)

            elif re.search(
                bare_pattern,
                text,
                flags=re.IGNORECASE,
            ):
                graph[
                    expression_name
                ].add(dependency)

    return graph


def get_table_tmdl_text() -> str:

    tables_dir = (
        MODEL_ROOT
        / "definition"
        / "tables"
    )

    chunks = []

    for table_file in sorted(
        tables_dir.glob("*.tmdl")
    ):

        chunks.append(
            table_file.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        )

    return "\n".join(chunks)


def find_root_expressions(
    expressions: Dict[str, str],
) -> Set[str]:

    roots: Set[str] = set()

    table_text = get_table_tmdl_text()

    for expression_name in expressions:

        quoted_pattern = (
            rf'#"{re.escape(expression_name)}"'
        )

        bare_pattern = (
            rf"(?<![A-Za-z0-9_])"
            rf"{re.escape(expression_name)}"
            rf"(?![A-Za-z0-9_])"
        )

        if re.search(
            quoted_pattern,
            table_text,
            flags=re.IGNORECASE,
        ):
            roots.add(
                expression_name
            )

        elif re.search(
            bare_pattern,
            table_text,
            flags=re.IGNORECASE,
        ):
            roots.add(
                expression_name
            )

    return roots


def find_active_expressions() -> Set[str]:

    expressions = parse_expressions()

    graph = build_expression_graph(
        expressions
    )

    roots = find_root_expressions(
        expressions
    )

    active: Set[str] = set(
        roots
    )

    queue = list(roots)

    while queue:

        current = queue.pop()

        for dependency in graph.get(
            current,
            set(),
        ):

            if dependency not in active:

                active.add(
                    dependency
                )

                queue.append(
                    dependency
                )

    return active


def get_unused_expressions() -> Set[str]:

    expressions = parse_expressions()

    active = find_active_expressions()

    return (
        set(expressions.keys())
        - active
    )


def main():

    unused = (
        get_unused_expressions()
    )

    print()
    print("=" * 60)
    print("UNUSED EXPRESSIONS")
    print("=" * 60)

    for expression in sorted(
        unused
    ):
        print(expression)

    print()
    print(
        f"Count: {len(unused)}"
    )


if __name__ == "__main__":
    main()