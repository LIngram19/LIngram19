from __future__ import annotations

from typing import Set
import re

from config import MODEL_ROOT


def normalize_name(
    value: str | None,
) -> str | None:

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.replace(
        "'",
        "",
    ).replace(
        '"',
        "",
    )

    return value.strip() or None


def add_query_group_and_parents(
    active: Set[str],
    query_group: str,
) -> None:

    query_group = normalize_name(
        query_group
    )

    if not query_group:
        return

    active.add(
        query_group
    )

    current = query_group

    while "\\" in current:

        current = current.rsplit(
            "\\",
            1,
        )[0]

        active.add(
            current
        )


def get_all_query_groups() -> Set[str]:

    model_file = (
        MODEL_ROOT
        / "definition"
        / "model.tmdl"
    )

    query_groups: Set[str] = set()

    pattern = re.compile(
        r"queryGroup\s+(?:'([^']+)'|(.+))",
        flags=re.IGNORECASE,
    )

    for line in model_file.read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines():

        stripped = line.strip()

        if not stripped.startswith(
            "queryGroup "
        ):
            continue

        match = pattern.match(
            stripped
        )

        if not match:
            continue

        query_group = normalize_name(
            match.group(1)
            or match.group(2)
        )

        if query_group:

            query_groups.add(
                query_group
            )

    return query_groups


def get_active_query_groups() -> Set[str]:

    active: Set[str] = set()

    query_group_pattern = re.compile(
        r"queryGroup\s*:\s*(?:'([^']+)'|([^\r\n]+))",
        flags=re.IGNORECASE,
    )

    #
    # Scan table TMDLs
    #
    tables_dir = (
        MODEL_ROOT
        / "definition"
        / "tables"
    )

    for table_file in tables_dir.rglob(
        "*.tmdl"
    ):

        text = table_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        for match in query_group_pattern.finditer(
            text
        ):

            query_group = normalize_name(
                match.group(1)
                or match.group(2)
            )

            if not query_group:
                continue

            add_query_group_and_parents(
                active,
                query_group,
            )

    #
    # Scan expressions.tmdl
    #
    expressions_file = (
        MODEL_ROOT
        / "definition"
        / "expressions.tmdl"
    )

    if expressions_file.exists():

        text = expressions_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        for match in query_group_pattern.finditer(
            text
        ):

            query_group = normalize_name(
                match.group(1)
                or match.group(2)
            )

            if not query_group:
                continue

            add_query_group_and_parents(
                active,
                query_group,
            )

    return active


def get_unused_query_groups() -> Set[str]:

    all_query_groups = (
        get_all_query_groups()
    )

    active_query_groups = (
        get_active_query_groups()
    )

    return (
        all_query_groups
        - active_query_groups
    )


def main():

    active_groups = (
        get_active_query_groups()
    )

    unused_groups = (
        get_unused_query_groups()
    )

    print()
    print("=" * 60)
    print("ACTIVE QUERY GROUPS")
    print("=" * 60)

    for group in sorted(
        active_groups
    ):
        print(group)

        print()
        print(
            f"Active Count: "
            f"{len(active_groups)}"
        )

    print()
    print("=" * 60)
    print("UNUSED QUERY GROUPS")
    print("=" * 60)

    for group in sorted(
        unused_groups
    ):
        print(group)

    print()
    print(
        f"Unused Count: "
        f"{len(unused_groups)}"
    )


if __name__ == "__main__":
    main()