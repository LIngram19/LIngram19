from visual_parser import (
    get_visual_refs
)

from rls_parser import (
    get_rls_refs
)


def get_root_objects(
    report_folder,
    semantic_folder
):

    visual_refs = (
        get_visual_refs(
            report_folder
        )
    )

    rls_refs = (
        get_rls_refs(
            semantic_folder
        )
    )

    return (
        visual_refs
        | rls_refs
    )