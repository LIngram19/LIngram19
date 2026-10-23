from pathlib import Path


def get_project_paths(
    pbip_root,
    report_name
):

    pbip_root = Path(
        pbip_root
    )

    report_folder = (
        pbip_root
        / f"{report_name}.Report"
    )

    semantic_folder = (
        pbip_root
        / f"{report_name}.SemanticModel"
    )

    cleanup_plan_file = (
        pbip_root
        / (
            f"{report_name}"
            "_cleanup_plan.txt"
        )
    )

    return {
        "report_folder": report_folder,
        "semantic_folder": semantic_folder,
        "cleanup_plan_file": cleanup_plan_file
    }