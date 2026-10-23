from pathlib import Path
from datetime import datetime
import shutil
import re

def normalize_measure_name(
    name
):

    return (
        str(name)
        .strip()
        .strip("'")
        .strip('"')
        .casefold()
    )

# ============================================================
# BACKUPS
# ============================================================

def get_timestamp():

    return datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

def create_backup(
    semantic_folder,
    report_name
):

    semantic_folder = Path(semantic_folder)

    backup_root = (
        semantic_folder.parent
        / "_cleanup_backup"
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    safe_report_name = (
    report_name
    .replace("/", "_")
    .replace("\\", "_")
    )

    backup_folder = (
        backup_root
        / f"{safe_report_name}_{timestamp}"
)

    backup_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    definition = (
        semantic_folder
        / "definition"
    )

    relationships_file = (
        definition
        / "relationships.tmdl"
    )

    expressions_file = (
        definition
        / "expressions.tmdl"
    )

    tables_folder = (
        definition
        / "tables"
    )

    if relationships_file.exists():

        shutil.copy2(
            relationships_file,
            backup_folder
            / "relationships.tmdl"
        )

    if expressions_file.exists():

        shutil.copy2(
            expressions_file,
            backup_folder
            / "expressions.tmdl"
        )

    backup_tables = (
        backup_folder
        / "tables"
    )

    shutil.copytree(
        tables_folder,
        backup_tables
    )

    return backup_folder



# ============================================================
# CLEANUP PLAN
# ============================================================

def write_plan(
    output_file,
    report_name,
    pass_count,
    tables,
    relationships,
    expressions,
    measures
):

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "RUN INFORMATION\n"
        )

        f.write(
            "=" * 60 + "\n"
        )

        f.write(
            f"Report: "
            f"{report_name}\n"
        )

        f.write(
            f"Cleanup Passes: "
            f"{pass_count}\n"
        )

        f.write("\n")

        f.write(
            "CLEANUP SUMMARY\n"
        )

        f.write(
            "=" * 60 + "\n"
        )

        f.write(
            f"Tables: {len(tables)}\n"
        )

        f.write(
            f"Relationships: {len(relationships)}\n"
        )

        f.write(
            f"Expressions: {len(expressions)}\n"
        )

        f.write(
            f"Measures: {len(measures)}\n"
        )

        f.write("\n\n")

        f.write(
            f"TABLES TO REMOVE ({len(tables)})\n"
        )

        f.write(
            "=" * 60 + "\n"
        )

        for item in sorted(tables):

            f.write(
                f"{item}\n"
            )

        f.write("\n\n")

        f.write(
            f"RELATIONSHIPS TO REMOVE ({len(relationships)})\n"
        )

        f.write(
            "=" * 60 + "\n"
        )

        for item in sorted(relationships):

            f.write(
                f"{item}\n"
            )

        f.write("\n\n")

        f.write(
            f"EXPRESSIONS TO REMOVE ({len(expressions)})\n"
        )

        f.write(
            "=" * 60 + "\n"
        )

        for item in sorted(expressions):

            f.write(
                f"{item}\n"
            )

        f.write("\n\n")

        f.write(
            f"MEASURES TO REMOVE ({len(measures)})\n"
        )

        f.write(
            "=" * 60 + "\n"
        )

        for item in sorted(measures):

            f.write(
                f"{item}\n"
            )


# ============================================================
# TABLES
# ============================================================

def remove_table_files(
    semantic_folder,
    table_names,
    apply_changes
):

    removed = []

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    table_names = set(table_names)

    for file in tables_folder.glob(
        "*.tmdl"
    ):

        table_name = (
            file.stem
            .replace("%2F", "/")
            .replace("%3F", "?")
        )

        if table_name not in table_names:
            continue

        removed.append(
            table_name
        )

        if apply_changes:
            file.unlink()

    return removed


# ============================================================
# RELATIONSHIPS
# ============================================================

def extract_relationship_tables(
    block
):

    tables = set()

    matches = re.findall(
        r"fromColumn:\s+'?([^'.]+)'?\.",
        block
    )

    tables.update(matches)

    matches = re.findall(
        r"toColumn:\s+'?([^'.]+)'?\.",
        block
    )

    tables.update(matches)

    return tables


def remove_relationships(
    semantic_folder,
    removed_tables,
    apply_changes
):

    relationships_file = (
        Path(semantic_folder)
        / "definition"
        / "relationships.tmdl"
    )

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

        if (
            line.startswith(
                "relationship "
            )
            and current
        ):

            blocks.append(
                "".join(current)
            )

            current = []

        current.append(line)

    if current:
        blocks.append(
            "".join(current)
        )

    kept = []

    removed = []

    removed_tables = set(
        removed_tables
    )

    for block in blocks:

        tables = (
            extract_relationship_tables(
                block
            )
        )

        if (
            tables
            & removed_tables
        ):

            rel_name = (
                block.splitlines()[0]
                .replace(
                    "relationship ",
                    ""
                )
                .strip()
            )

            removed.append(
                rel_name
            )

        else:

            kept.append(
                block
            )

    if apply_changes:

        relationships_file.write_text(
            "".join(kept),
            encoding="utf-8"
        )

    return removed


# ============================================================
# EXPRESSIONS
# ============================================================

def remove_expression(
    text,
    target_expression
):

    lines = text.splitlines(
        keepends=True
    )

    result = []

    skipping = False

    for line in lines:

        if (
            line.startswith(
                "expression "
            )
            and target_expression
            in line
        ):

            skipping = True

            continue

        if (
            skipping
            and line.startswith(
                "expression "
            )
        ):

            skipping = False

        if not skipping:

            result.append(
                line
            )

    return "".join(result)


def remove_expressions(
    semantic_folder,
    expressions,
    apply_changes
):

    expressions_file = (
        Path(semantic_folder)
        / "definition"
        / "expressions.tmdl"
    )

    text = (
        expressions_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    )

    for expr in expressions:

        text = remove_expression(
            text,
            expr
        )

    if apply_changes:

        expressions_file.write_text(
            text,
            encoding="utf-8"
        )

    return sorted(expressions)


# ============================================================
# MEASURES
# ============================================================

OBJECT_STARTS = (
    "measure ",
    "column ",
    "partition ",
    "hierarchy ",
    "calculationGroup "
)


def remove_measures_from_file(
    file_path,
    measures_to_remove
):

    measures_to_remove = set(
        measures_to_remove
    )

    lines = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    ).splitlines(
        keepends=True
    )

    output = []

    removed = []

    i = 0

    while i < len(lines):

        stripped = (
            lines[i].lstrip()
        )

        if stripped.startswith(
            "measure "
        ):

            match = re.search(
                r"measure\s+'([^']+)'",
                stripped
            )

            if match:

                measure_name = (
                    match.group(1)
                )

                normalized_measure_name = (
                    normalize_measure_name(
                        measure_name
                    )
                )

                if (
                    normalized_measure_name
                    in measures_to_remove
                ):

                    removed.append(
                        measure_name
                    )

                    i += 1

                    while i < len(lines):

                        next_line = (
                            lines[i]
                            .lstrip()
                        )

                        if any(
                            next_line.startswith(
                                obj
                            )
                            for obj in OBJECT_STARTS
                        ):

                            break

                        i += 1

                    continue

        output.append(
            lines[i]
        )

        i += 1

    file_path.write_text(
        "".join(output),
        encoding="utf-8"
    )

    return removed


def remove_measures(
    semantic_folder,
    measure_names,
    apply_changes
):

    measure_names = set(
        measure_names
    )
    measure_names = {
    normalize_measure_name(
        m
    )
    for m in measure_names
}

    removed = []

    tables_folder = (
    Path(semantic_folder)
    / "definition"
    / "tables"
)

    for file in tables_folder.glob(
        "*.tmdl"
    ):

        if apply_changes:

            removed.extend(
                remove_measures_from_file(
                    file,
                    measure_names
                )
            )

        else:

            text = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            for line in text.splitlines():

                match = re.search(
                    r"measure\s+'([^']+)'",
                    line,
                    flags=re.IGNORECASE
                )

                if not match:
                    continue

                measure_name = normalize_measure_name(
                    match.group(1)
                )

                if measure_name in measure_names:

                    removed.append(
                        measure_name
                    )

    return sorted(
        set(removed)
    )