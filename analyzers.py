from pathlib import Path
from urllib.parse import unquote
from pbip_parser import (
    get_all_measures,
    get_all_semantic_text
)

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
# MEASURE DEPENDENCY HELPERS
# ============================================================
def build_model_objects(
    semantic_folder
):

    tables = set()
    measures = set()
    columns = set()

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    for table_file in tables_folder.glob(
        "*.tmdl"
    ):

        try:

            text = table_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception:

            continue

        #
        # Table
        #
        table_name = normalize_measure_name(
            unquote(
                table_file.stem
            )
        )

        tables.add(
            table_name
        )

        #
        # Measures
        #
        for match in re.finditer(
            r"measure\s+(?:'([^']+)'|([^\r\n=]+))",
            text,
            flags=re.IGNORECASE
        ):

            measure_name = (
                match.group(1)
                or match.group(2)
            )

            measures.add(
                normalize_measure_name(
                    measure_name.strip()
                )
            )

        #
        # Columns
        #
        for line in text.splitlines():

            line = line.strip()

            if not line.startswith(
                "column "
            ):
                continue

            column_name = (
                line
                .replace(
                    "column ",
                    ""
                )
                .split(
                    "=",
                    1
                )[0]
                .strip()
                .strip("'")
            )

            columns.add(
                normalize_measure_name(
                    column_name
                )
            )

    return (
        tables,
        measures,
        columns
    )
def build_measure_dependency_graph(
    semantic_folder
):

    graph = {}

    model_tables, model_measures, model_columns = (
        build_model_objects(
         semantic_folder
    )
)
    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    for table_file in tables_folder.glob(
        "*.tmdl"
    ):

        try:

            text = table_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception:

            continue

        blocks = re.finditer(
            r"measure\s+(?:'([^']+)'|([^\r\n=]+)).*?(?=\n\s*measure\s+(?:'|[^\r\n=])|\Z)",
            text,
            flags=re.DOTALL | re.IGNORECASE
            )

        for match in blocks:

            measure_name = normalize_measure_name(
    (
        match.group(1)
        or match.group(2)
    ).strip()
)

            definition = (
                match.group(0)
            )

            dependencies = {
                normalize_measure_name(
                    dep
                )
                for dep in re.findall(
                    r"\[([^\]]+)\]",
                    definition
                )
            }

            dependencies.discard(
                measure_name
            )

            graph[
                measure_name
            ] = dependencies

    for measure in graph:

        graph[measure] = {
            dep
            for dep in graph[measure]
            if dep in model_measures
        }

    print()
    print("=" * 60)
    print("GRAPH CHECK")
    print("=" * 60)

    for target in [
        "my net fees earned",
        "my sum net fees earned",
        "r12 sum backlog"
    ]:

        print()

        print(
            f"{target}: "
            f"{target in graph}"
        )

        if target in graph:

            for dep in sorted(
                graph[target]
            ):

                print(
                    f"  -> {dep}"
                )

    return graph

def get_visual_measure_names(
    report_folder,
    model_measures
):

    measures = set()

    report_path = Path(
        report_folder
    )

    for json_file in report_path.rglob(
        "*.json"
    ):

        try:

            text = json_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception:

            continue

        #
        # queryRef references
        #
        for ref in re.findall(
            r'"queryRef"\s*:\s*"([^"]+)"',
            text,
            flags=re.IGNORECASE
        ):

            if "." not in ref:

                continue

            object_name = normalize_measure_name(
                ref.split(
                    ".",
                    1
                )[1]
            )

            if object_name in model_measures:

                measures.add(
                    object_name
                )

        #
        # Property references
        #
        for prop in re.findall(
            r'"Property"\s*:\s*"([^"]+)"',
            text,
            flags=re.IGNORECASE
        ):

            object_name = normalize_measure_name(
                prop
            )

            if object_name in model_measures:

                measures.add(
                    object_name
                )

        #
        # Field Parameter references
        #
        for _, measure_name in re.findall(
            r"'''([^']+)''\[([^\]]+)\]",
            text,
            flags=re.IGNORECASE
        ):

            measure_name = (
                normalize_measure_name(
                    measure_name
                )
            )

            if (
                measure_name
                in model_measures
            ):

                measures.add(
                    measure_name
                )

    print()

    print(
        f"Root Measures Found: "
        f"{len(measures)}"
    )

    return measures
# ============================================================
# EXPRESSIONS
# ============================================================

def find_unused_expressions(report_folder, semantic_folder):

    expressions_file = (
        Path(semantic_folder)
        / "definition"
        / "expressions.tmdl"
    )

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    if not expressions_file.exists():
        return 0, []

    text = expressions_file.read_text(
        encoding="utf-8"
    )

    expressions = []

    for line in text.splitlines():

        if line.startswith("expression "):

            expr_name = line.split(
                "=",
                1
            )[0]

            expr_name = (
                expr_name
                .replace("expression ", "")
                .strip()
                .strip("'")
            )

            expressions.append(expr_name)

    references = {
        expr: 0
        for expr in expressions
    }

    for tmdl_file in tables_folder.rglob("*.tmdl"):

        contents = tmdl_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        for expr in expressions:

            if expr in contents:
                references[expr] += 1

    unused = sorted(
        [
            expr
            for expr, count
            in references.items()
            if count == 0
        ]
    )

    return (
        len(expressions),
        unused
    )


# ============================================================
# MEASURES
# ============================================================


def find_unused_measures(
    report_folder,
    semantic_folder
):

    graph = build_measure_dependency_graph(
        semantic_folder
    )

    target = (
        "my net fees earned"
    )

    print()

    print(
        f"Dependencies for "
        f"{target}:"
    )

    for dep in sorted(
        graph.get(
            target,
            set()
        )
    ):

        print(
            f"  -> {dep}"
        )

    all_measures = set(
        graph.keys()
    )

    _, model_measures, _ = (
        build_model_objects(
            semantic_folder
        )
    )

    root_measures = (
        get_visual_measure_names(
            report_folder,
            model_measures
        )
    )

    print()
    print("=" * 60)
    print("ROOT CHECK")
    print("=" * 60)

    for target in [
        "my net fees earned",
        "my sum net fees earned",
        "r12 sum backlog"
    ]:

        print(
            f"{target}: "
            f"{target in root_measures}"
        )

    print()
    print("=" * 60)
    print("ROOT MEASURE SAMPLE")
    print("=" * 60)

    for measure in sorted(
        root_measures
    )[:100]:

        print(measure)

    used_measures = (
        get_reachable_measures(
            graph,
            root_measures
        )
    )

    used_measures = (
        used_measures
        & all_measures
    )

    print()
    print("=" * 60)
    print("REACHABILITY CHECK")
    print("=" * 60)

    for target in [
        "my net fees earned",
        "my sum net fees earned",
        "r12 sum backlog"
    ]:

        print(
            f"{target}: "
            f"{target in used_measures}"
        )

    print()

    print(
        f"Measures In Graph: "
        f"{len(graph)}"
    )

    print(
        f"Root Measures: "
        f"{len(root_measures)}"
    )

    print(
        f"Reachable Measures: "
        f"{len(used_measures)}"
    )

    print(
        f"Unreachable Measures: "
        f"{len(all_measures) - len(used_measures)}"
    )

    details = []

    status_counts = {
        "UNUSED": 0,
        "DAX_ONLY": 0,
        "REPORT_ONLY": 0
    }

    for idx, measure in enumerate(
        sorted(all_measures),
        start=1
    ):

        if idx % 100 == 0:

            print(
                f"Measure Analysis: "
                f"{idx:,}/"
                f"{len(all_measures):,}"
            )

        report_refs = (
            measure in root_measures
        )

        reachable = (
            measure in used_measures
        )

        if not reachable:

            status = "UNUSED"

        elif report_refs:

            status = "REPORT_ONLY"

        else:

            status = "DAX_ONLY"

        status_counts[status] += 1

        details.append(
            {
                "name": measure,
                "status": status
            }
        )

    grouped = {
        "UNUSED": [],
        "DAX_ONLY": [],
        "REPORT_ONLY": []
    }

    for item in details:

        grouped[
            item["status"]
        ].append(
            item["name"]
        )

    print()

    print(
        "=" * 60
    )

    print(
        "MEASURE STATUS SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        f"UNUSED: "
        f"{status_counts['UNUSED']}"
    )

    print(
        f"DAX_ONLY: "
        f"{status_counts['DAX_ONLY']}"
    )

    print(
        f"REPORT_ONLY: "
        f"{status_counts['REPORT_ONLY']}"
    )

    print(
        f"TOTAL: "
        f"{len(all_measures)}"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"Measures Referenced By Visuals: "
        f"{len(root_measures)}"
    )

    return (
        len(all_measures),
        grouped
    )
        

# ============================================================
# TABLES
# ============================================================

def find_unused_tables(
    report_folder,
    semantic_folder
):

    semantic_text = get_all_semantic_text(
        semantic_folder
    )

    #
    # Report text fallback
    #
    report_text = ""

    #
    # Explicit table references from visuals
    #
    report_tables = set()

    report_path = Path(
        report_folder
    )

    for file in report_path.rglob("*"):

        if not file.is_file():
            continue

        try:

            text = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            report_text += text

        except Exception:
            pass

    #
    # Visual entity references
    #
    for visual_file in report_path.rglob(
        "visual.json"
    ):

        try:

            visual_text = visual_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            entity_matches = re.findall(
                r'"Entity"\s*:\s*"([^"]+)"',
                visual_text,
                flags=re.IGNORECASE
            )

            for entity in entity_matches:

                report_tables.add(
                    entity
                )

        except Exception:
            pass

    #
    # RLS role text
    #
    roles_text = ""

    roles_folder = (
        Path(semantic_folder)
        / "definition"
        / "roles"
    )

    if roles_folder.exists():

        for role_file in roles_folder.rglob(
            "*.tmdl"
        ):

            try:

                roles_text += role_file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

            except Exception:
                pass

    #
    # Tables
    #
    tables = []

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    for table_file in tables_folder.glob(
        "*.tmdl"
    ):

        table_name = unquote(
            table_file.stem
        )

        #
        # Ignore auto-generated tables
        #
        if table_name.startswith(
            "LocalDateTable_"
        ):
            continue

        if table_name.startswith(
            "DateTableTemplate_"
        ):
            continue

        tables.append(
            table_name
        )

    grouped = {
        "UNUSED": [],
        "DAX_ONLY": [],
        "REPORT_ONLY": [],
        "RLS_ONLY": [],
        "USED": []
    }

    status_counts = {
        "UNUSED": 0,
        "DAX_ONLY": 0,
        "REPORT_ONLY": 0,
        "RLS_ONLY": 0,
        "USED": 0
    }

    table_status = {}

    for table in sorted(tables):

        #
        # Explicit visual reference
        #
        report_refs = (
            table in report_tables
        )

        #
        # Fallback text search
        #
        if not report_refs:

            report_refs = (
                table in report_text
            )

        #
        # Semantic model references
        #
        dax_refs = (
            semantic_text.count(
                f"'{table}'["
            ) > 0
        )

        #
        # RLS references
        #
        rls_refs = (
            table in roles_text
        )

        if (
            not report_refs
            and not dax_refs
            and not rls_refs
        ):

            status = "UNUSED"

        elif (
            not report_refs
            and dax_refs
            and not rls_refs
        ):

            status = "DAX_ONLY"

        elif (
            report_refs
            and not dax_refs
            and not rls_refs
        ):

            status = "REPORT_ONLY"

        elif (
            not report_refs
            and not dax_refs
            and rls_refs
        ):

            status = "RLS_ONLY"

        else:

            status = "USED"

        table_status[table] = status

        status_counts[status] += 1

        grouped[status].append(
            table
        )

    print()

    print(
        "=" * 60
    )

    print(
        "TABLE STATUS SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        f"UNUSED:      {status_counts['UNUSED']}"
    )

    print(
        f"DAX_ONLY:    {status_counts['DAX_ONLY']}"
    )

    print(
        f"REPORT_ONLY: {status_counts['REPORT_ONLY']}"
    )

    print(
        f"RLS_ONLY:    {status_counts['RLS_ONLY']}"
    )

    print(
        f"USED:        {status_counts['USED']}"
    )

    print(
        f"TOTAL:       {len(tables)}"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"Tables Referenced By Visuals: "
        f"{len(report_tables)}"
    )

    return (
        len(tables),
        grouped,
        table_status
    )
# ============================================================
# COLUMNS
# ============================================================

def find_unused_columns(report_folder, semantic_folder):

    #
    # Reuse table analysis
    #
    _, _, table_status = find_unused_tables(
        report_folder,
        semantic_folder
    )

    semantic_text = get_all_semantic_text(
        semantic_folder
    )

    #
    # Report text
    #
    report_text = ""

    report_path = Path(report_folder)

    for file in report_path.rglob("*"):

        if not file.is_file():
            continue

        try:

            report_text += file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception:
            pass

    #
    # RLS text
    #
    roles_text = ""

    roles_folder = (
        Path(semantic_folder)
        / "definition"
        / "roles"
    )

    if roles_folder.exists():

        for role_file in roles_folder.rglob("*.tmdl"):

            try:

                roles_text += role_file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

            except Exception:
                pass

    #
    # Relationships
    #
    relationships_text = ""

    relationships_file = (
        Path(semantic_folder)
        / "definition"
        / "relationships.tmdl"
    )

    if relationships_file.exists():

        relationships_text = (
            relationships_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        )

    grouped = {
        "UNUSED": [],
        "RELATIONSHIP_ONLY": []
    }

    status_counts = {
        "SKIPPED_UNUSED_TABLE": 0,
        "UNUSED": 0,
        "RELATIONSHIP_ONLY": 0,
        "DAX_ONLY": 0,
        "REPORT_ONLY": 0,
        "RLS_ONLY": 0,
        "USED": 0
    }

    total_columns = 0

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    for table_file in tables_folder.glob("*.tmdl"):

        table_name = unquote(
            table_file.stem
        )

        if table_name.startswith(
            "LocalDateTable_"
        ):
            continue

        if table_name.startswith(
            "DateTableTemplate_"
        ):
            continue

        try:

            text = table_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception:
            continue

        #
        # Parse columns
        #
        for line in text.splitlines():

            line = line.strip()

            if not line.startswith("column "):
                continue

            col_name = (
                line
                .replace("column ", "")
                .split(" =", 1)[0]
                .strip()
                .strip("'")
            )

            total_columns += 1

            full_name = (
                f"{table_name}[{col_name}]"
            )

            #
            # Skip columns in tables already
            # classified UNUSED
            #
            if (
                table_status.get(
                    table_name
                ) == "UNUSED"
            ):

                status_counts[
                    "SKIPPED_UNUSED_TABLE"
                ] += 1

                continue

            report_refs = (
                col_name in report_text
            )

            dax_refs = (
                semantic_text.count(
                    f"[{col_name}]"
                ) > 0
            )

            relationship_refs = (
                col_name in relationships_text
            )

            rls_refs = (
                col_name in roles_text
            )

            if (
                not report_refs
                and not dax_refs
                and not relationship_refs
                and not rls_refs
            ):

                status = "UNUSED"

            elif (
                relationship_refs
                and not report_refs
                and not dax_refs
            ):

                status = (
                    "RELATIONSHIP_ONLY"
                )

            elif (
                dax_refs
                and not report_refs
            ):

                status = "DAX_ONLY"

            elif (
                report_refs
                and not dax_refs
            ):

                status = "REPORT_ONLY"

            elif (
                rls_refs
                and not report_refs
                and not dax_refs
            ):

                status = "RLS_ONLY"

            else:

                status = "USED"

            status_counts[
                status
            ] += 1

            if status in (
                "UNUSED",
                "RELATIONSHIP_ONLY"
            ):

                grouped[
                    status
                ].append(
                    full_name
                )

    print()
    print("=" * 60)
    print("COLUMN STATUS SUMMARY")
    print("=" * 60)
    print(
        f"SKIPPED (UNUSED TABLES): "
        f"{status_counts['SKIPPED_UNUSED_TABLE']}"
    )
    print(
        f"UNUSED: "
        f"{status_counts['UNUSED']}"
    )
    print(
        f"RELATIONSHIP_ONLY: "
        f"{status_counts['RELATIONSHIP_ONLY']}"
    )
    print(
        f"DAX_ONLY: "
        f"{status_counts['DAX_ONLY']}"
    )
    print(
        f"REPORT_ONLY: "
        f"{status_counts['REPORT_ONLY']}"
    )
    print(
        f"RLS_ONLY: "
        f"{status_counts['RLS_ONLY']}"
    )
    print(
        f"USED: "
        f"{status_counts['USED']}"
    )
    print(
        f"TOTAL ANALYZED: "
        f"{total_columns}"
    )
    print("=" * 60)

    return (
        total_columns,
        grouped
    )