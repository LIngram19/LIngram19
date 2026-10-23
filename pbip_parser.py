from pathlib import Path
import json
import re


# ============================================================
# FILE DISCOVERY
# ============================================================

def get_tmdl_files(semantic_folder):
    """
    Returns all .tmdl files in the semantic model.
    """

    semantic_folder = Path(semantic_folder)

    return list(semantic_folder.rglob("*.tmdl"))


def get_json_files(report_folder):
    """
    Returns all .json files in the report.
    """

    report_folder = Path(report_folder)

    return list(report_folder.rglob("*.json"))


# ============================================================
# TEXT HELPERS
# ============================================================

def read_text(path):
    """
    Reads a file safely.
    """

    try:
        return Path(path).read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except Exception:
        return ""


def get_all_semantic_text(semantic_folder):
    """
    Concatenates all TMDL text.
    """

    chunks = []

    for file in get_tmdl_files(semantic_folder):
        chunks.append(read_text(file))

    return "\n".join(chunks)


def get_all_report_text(report_folder):
    """
    Concatenates all report JSON.
    """

    chunks = []

    for file in get_json_files(report_folder):
        chunks.append(read_text(file))

    return "\n".join(chunks)


# ============================================================
# TABLES
# ============================================================

def get_all_tables(semantic_folder):
    """
    Returns:
        {
            "Sales",
            "Customer",
            ...
        }
    """

    tables = set()

    for file in get_tmdl_files(semantic_folder):

        text = read_text(file)

        matches = re.findall(
            r"^\s*table\s+'([^']+)'",
            text,
            re.MULTILINE | re.IGNORECASE
        )

        tables.update(matches)

    return tables


# ============================================================
# MEASURES
# ============================================================

def get_all_measures(semantic_folder):
    
    measures = set()

    for file in get_tmdl_files(semantic_folder):

        text = read_text(file)

        matches = re.findall(
            r"^\s*measure\s+'([^']+)'",
            text,
            re.MULTILINE | re.IGNORECASE
        )

        measures.update(matches)

    return measures


# ============================================================
# COLUMNS
# ============================================================

def get_all_columns(semantic_folder):
    """
    Returns:
        {
            "Sales[Amount]",
            "Customer[Name]"
        }
    """

    columns = set()

    current_table = None

    for file in get_tmdl_files(semantic_folder):

        text = read_text(file)

        for line in text.splitlines():

            table_match = re.match(
                r"^\s*table\s+'([^']+)'",
                line,
                re.IGNORECASE
            )

            if table_match:
                current_table = table_match.group(1)

            column_match = re.match(
                r"^\s*column\s+'([^']+)'",
                line,
                re.IGNORECASE
            )

            if column_match and current_table:

                columns.add(
                    f"{current_table}[{column_match.group(1)}]"
                )

    return columns


# ============================================================
# EXPRESSIONS
# ============================================================

def get_all_expressions(semantic_folder):
    """
    Extract expression names.

    expression ABC =
    expression XYZ =
    """

    expressions = set()

    for file in get_tmdl_files(semantic_folder):

        text = read_text(file)

        matches = re.findall(
            r"^\s*expression\s+([^\s=]+)",
            text,
            re.MULTILINE | re.IGNORECASE
        )

        expressions.update(matches)

    return expressions


# ============================================================
# RELATIONSHIPS
# ============================================================

def get_relationships(semantic_folder):
    """
    Returns:

    [
        ("Sales", "Customer"),
        ("Sales", "Date")
    ]
    """

    relationships = []

    for file in get_tmdl_files(semantic_folder):

        text = read_text(file)

        from_tables = re.findall(
            r"fromTable:\s*'([^']+)'",
            text,
            re.IGNORECASE
        )

        to_tables = re.findall(
            r"toTable:\s*'([^']+)'",
            text,
            re.IGNORECASE
        )

        for src, dst in zip(from_tables, to_tables):
            relationships.append((src, dst))

    return relationships


def get_relationship_counts(semantic_folder):
    """
    Returns:

    {
        "Sales": 12,
        "Customer": 3
    }
    """

    counts = {}

    relationships = get_relationships(
        semantic_folder
    )

    for src, dst in relationships:

        counts[src] = counts.get(src, 0) + 1
        counts[dst] = counts.get(dst, 0) + 1

    return counts


# ============================================================
# REPORT REFERENCES
# ============================================================

def get_report_measure_names(report_folder):
    """
    Measure names used in visuals.
    """

    used = set()

    for file in get_json_files(report_folder):

        text = read_text(file)

        matches = re.findall(
            r'"Measure".*?"Property"\s*:\s*"([^"]+)"',
            text,
            re.DOTALL
        )

        used.update(matches)

    return used


def get_report_columns(report_folder):
    """
    Columns used in visuals.

    Returns:

    {
        "Sales[Amount]"
    }
    """

    used = set()

    for file in get_json_files(report_folder):

        text = read_text(file)

        column_blocks = re.findall(
            r'"Column".*?"Entity"\s*:\s*"([^"]+)".*?"Property"\s*:\s*"([^"]+)"',
            text,
            re.DOTALL
        )

        for table, column in column_blocks:
            used.add(f"{table}[{column}]")

    return used


# ============================================================
# DEPENDENCY HELPERS
# ============================================================

def find_measure_references(
    semantic_folder,
    measure_names
):
    """
    Finds DAX references to measures.

    Returns:
        set()
    """

    text = get_all_semantic_text(
        semantic_folder
    )

    referenced = set()

    for measure in measure_names:

        pattern = re.escape(
            f"[{measure}]"
        )

        matches = re.findall(
            pattern,
            text
        )

        if len(matches) > 1:
            referenced.add(measure)

    return referenced


def find_expression_references(
    semantic_folder,
    expressions
):
    """
    Finds referenced expressions.
    """

    text = get_all_semantic_text(
        semantic_folder
    )

    referenced = set()

    for expression in expressions:

        count = len(
            re.findall(
                rf"\b{re.escape(expression)}\b",
                text
            )
        )

        if count > 1:
            referenced.add(expression)

    return referenced