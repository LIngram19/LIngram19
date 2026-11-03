from __future__ import annotations

from typing import Set
import json
import re

from config import MODEL_ROOT

from unused_querygroup_detector import (
    get_unused_query_groups,
)


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

    if (
        value.startswith("[")
        and value.endswith("]")
    ):
        value = value[1:-1]

    return value.strip() or None


def get_existing_expressions() -> Set[str]:

    expressions_file = (
        MODEL_ROOT
        / "definition"
        / "expressions.tmdl"
    )

    existing: Set[str] = set()

    text = expressions_file.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    for line in text.splitlines():

        stripped = line.strip()

        if not stripped.startswith(
            "expression "
        ):
            continue

        name_part = stripped[
            len("expression "):
        ]

        expression_name = (
            name_part
            .split(
                "=",
                1,
            )[0]
            .strip()
            .strip("'")
            .strip('"')
        )

        normalized = normalize_name(
            expression_name
        )

        if normalized:
            existing.add(
                normalized
            )

    return existing


def parse_ref_table_name(
    line: str,
) -> str | None:

    stripped = line.strip()

    if not stripped.startswith(
        "ref table "
    ):
        return None

    table_name = stripped[
        len("ref table "):
    ].strip()

    return normalize_name(
        table_name
    )


def clean_query_order_line(
    line: str,
    removed_tables: Set[str],
    existing_expressions: Set[str],
) -> str:

    if (
        "annotation PBI_QueryOrder"
        not in line
    ):
        return line

    try:

        prefix, json_part = line.split(
            "=",
            1,
        )

        values = json.loads(
            json_part.strip()
        )

        cleaned_values = []

        for value in values:

            normalized = normalize_name(
                value
            )

            #
            # Remove deleted tables
            #
            if normalized in removed_tables:
                continue

            #
            # Preserve expressions
            #
            if (
                normalized
                in existing_expressions
            ):
                cleaned_values.append(
                    value
                )

                continue

            cleaned_values.append(
                value
            )

        return (
            prefix.rstrip()
            + " = "
            + json.dumps(
                cleaned_values,
                separators=(",", ":"),
            )
        )

    except Exception:

        return line


def clean_model(
    removed_tables: Set[str],
) -> dict:

    removed_tables = {
        normalize_name(t) or t
        for t in removed_tables
    }

    model_file = (
        MODEL_ROOT
        / "definition"
        / "model.tmdl"
    )

    existing_expressions = (
        get_existing_expressions()
    )

    unused_query_groups = {
        normalize_name(q)
        for q in get_unused_query_groups()
    }

    lines = model_file.read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines()

    output = []

    removed_refs: Set[str] = set()
    removed_query_groups: Set[str] = set()

    i = 0

    while i < len(lines):

        line = lines[i]
        stripped = line.strip()

        #
        # Remove deleted table refs
        #
        ref_table = parse_ref_table_name(
            line
        )

        if (
            ref_table
            and ref_table
            in removed_tables
        ):

            removed_refs.add(
                ref_table
            )

            i += 1
            continue

        #
        # Remove unused query groups
        #
        if stripped.startswith(
            "queryGroup "
        ):

            match = re.match(
                r"queryGroup\s+(?:'([^']+)'|(.+))",
                stripped,
            )

            if match:

                query_group = normalize_name(
                    match.group(1)
                    or match.group(2)
                )

                block_end = i + 1

                while (
                    block_end
                    < len(lines)
                ):

                    next_line = lines[
                        block_end
                    ]

                    if (
                        next_line                     and not next_line.startswith(
                            (
                                " ",
                                "\t",
                            )
                        )
                    ):
                        break

                    block_end += 1

                if (
                    query_group
                    and query_group
                    in unused_query_groups
                ):

                    removed_query_groups.add(
                        query_group
                    )

                    i = block_end
                    continue

        line = clean_query_order_line(
            line,
            removed_tables,
            existing_expressions,
        )

        output.append(
            line
        )

        i += 1

    model_file.write_text(
        "\n".join(output).rstrip()
        + "\n",
        encoding="utf-8",
    )

    return {
        "removed_refs": removed_refs,
        "removed_query_groups": removed_query_groups,
    }