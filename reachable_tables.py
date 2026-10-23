def get_reachable_tables(
    reachable,
    inventory
):

    tables = set()

    for helper in reachable:

        if helper not in inventory:
            continue

        tables.add(
            inventory[
                helper
            ]["table"]
        )

    return tables