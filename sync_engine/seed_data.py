from db import get_bier_connection


# ==================================================
# SEED DATA SCRIPT
# ==================================================
# One-time script to populate:
#   1. InventoryItem (Chicken, Mutton, Boti, Rice)
#   2. MenuItemConsumption (POS menu → inventory)
# ==================================================


def seed_inventory_items(cursor):
    """
    Insert the 4 initial inventory items.
    Skip if items already exist.
    """

    items = [
        ("Chicken", "KG", 1.00),
        ("Mutton",  "KG", 1.00),
        ("Boti",    "KG", 0.50),
        ("Rice",    "KG", 20.00),
    ]

    inserted = 0

    for item_name, unit, reorder_level in items:

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.InventoryItem
            WHERE ItemName = ?
            """,
            item_name
        )

        exists = cursor.fetchone()[0]

        if exists > 0:
            print(
                f"  SKIP : {item_name} "
                f"(already exists)"
            )
            continue

        cursor.execute(
            """
            INSERT INTO dbo.InventoryItem
            (
                ItemName,
                Unit,
                ReorderLevel,
                CurrentCost,
                IsActive,
                CreatedAt
            )
            VALUES (?, ?, ?, 0, 1, GETDATE())
            """,
            item_name,
            unit,
            reorder_level
        )

        inserted += 1

        print(
            f"  ADD  : {item_name} "
            f"(Unit={unit}, "
            f"Reorder={reorder_level})"
        )

    return inserted


def get_item_id_map(cursor):
    """
    Return dict: ItemName -> InventoryItemId
    """

    cursor.execute(
        """
        SELECT InventoryItemId, ItemName
        FROM dbo.InventoryItem
        """
    )

    return {
        row.ItemName: row.InventoryItemId
        for row in cursor.fetchall()
    }


def seed_menu_consumption(cursor, item_map):
    """
    Insert MenuItemConsumption mappings.
    Each POS menu item maps to one or more
    inventory items with a consumption rate.

    Multi-ingredient dishes (e.g. biryani,
    fried rice) consume both meat AND rice.
    """

    # ------------------------------------------
    # CHICKEN DISHES → Chicken 0.25 KG
    # ------------------------------------------

    chicken_only = [
        "ANDHRA STYLE CHILLY CHICKEN",
        "BUTTER CHICKEN",
        "CHICKEN 65",
        "CHICKEN ALIKON",
        "CHICKEN CHATPAT",
        "CHICKEN HYDERABADI",
        "CHICKEN KADAI",
        "CHICKEN KALI MIRCH",
        "CHICKEN KEBAB",
        "CHICKEN KOLHAPURI",
        "CHICKEN LOLLIPOP",
        "CHICKEN MANCHURIAN",
        "CHICKEN MASALA",
        "CHICKEN NOODLES",
        "CHICKEN PATIALA",
        "CHICKEN SHAHI KURMA",
        "CHICKEN TIKKA",
        "CHILLY CHICKEN",
        "FRENCH CHICKEN",
        "GARLIC CHICKEN",
        "GUNTUR CHICKEN",
        "LEMON CHICKEN",
        "PEPPER CHICKEN DRY",
        "PUDINA CHICKEN",
        "ROTI PARK SPECIAL CHICKEN",
        "SUNDAY CHICKEN",
        "TANDOORI CHICKEN FULL",
        "TANDOORI CHICKEN HALF",
    ]

    # ------------------------------------------
    # CHICKEN + RICE DISHES
    # → Chicken 0.25 KG + Rice 0.11 KG
    # ------------------------------------------

    chicken_and_rice = [
        "CHICKEN BIRYANI",
        "CHICKEN PARDA BIRYANI",
        "CHICKEN FRIED RICE",
        "CHICKEN SCHEZWAN FRIED RICE",
        "CHICKEN SHANGHAI FRIED RICE",
    ]

    # ------------------------------------------
    # MUTTON DISHES → Mutton 0.25 KG
    # ------------------------------------------

    mutton_only = [
        "MUTTON DRY",
        "MUTTON FRY",
        "MUTTON HEAD CURRY",
        "MUTTON HEAD DRY",
        "MUTTON KURMA",
        "MUTTON THALE MAMSA",
    ]

    # ------------------------------------------
    # MUTTON + RICE DISHES
    # → Mutton 0.25 KG + Rice 0.11 KG
    # ------------------------------------------

    mutton_and_rice = [
        "MUTTON BIRYANI",
    ]

    # ------------------------------------------
    # BOTI DISHES → Boti 0.33 KG
    # ------------------------------------------

    boti_only = [
        "BOTI FRY",
        "BOTI MASALA",
    ]

    # ------------------------------------------
    # RICE-ONLY DISHES → Rice 0.11 KG
    # ------------------------------------------

    rice_only = [
        "BIRYANI RICE",
        "CURD RICE",
        "GHEE RICE",
        "JEERA RICE",
        "LEMON RICE",
        "MASALA RICE",
        "PALAK RICE",
        "PLAIN RICE",
        "TOMATO RICE",
        "VEG FRIED RICE",
        "VEG SCHEZWAN FRIED RICE",
        "VEG SHANGHAI FRIED RICE",
        "GINGER CAPSICUM FRIED RICE",
    ]

    # ------------------------------------------
    # SKIPPED ITEMS (no mapping yet)
    # ------------------------------------------
    # EGG BOTI FRY    → Egg (not tracked)
    # EGG FRIED RICE  → Egg (not tracked) + Rice
    # ------------------------------------------

    chicken_id = item_map["Chicken"]
    mutton_id = item_map["Mutton"]
    boti_id = item_map["Boti"]
    rice_id = item_map["Rice"]

    # Build mapping list:
    # (MenuItemName, InventoryItemId, ConsumptionPerQty)

    mappings = []

    for name in chicken_only:
        mappings.append(
            (name, chicken_id, 0.25)
        )

    for name in chicken_and_rice:
        mappings.append(
            (name, chicken_id, 0.25)
        )
        mappings.append(
            (name, rice_id, 0.11)
        )

    for name in mutton_only:
        mappings.append(
            (name, mutton_id, 0.25)
        )

    for name in mutton_and_rice:
        mappings.append(
            (name, mutton_id, 0.25)
        )
        mappings.append(
            (name, rice_id, 0.11)
        )

    for name in boti_only:
        mappings.append(
            (name, boti_id, 0.33)
        )

    for name in rice_only:
        mappings.append(
            (name, rice_id, 0.11)
        )

    # Clear existing mappings

    cursor.execute(
        """
        DELETE FROM dbo.MenuItemConsumption
        """
    )

    print(
        f"\n  Cleared existing mappings"
    )

    # Insert all mappings

    inserted = 0

    for menu_name, inv_id, rate in mappings:

        cursor.execute(
            """
            INSERT INTO dbo.MenuItemConsumption
            (
                MenuItemName,
                InventoryItemId,
                ConsumptionPerQty
            )
            VALUES (?, ?, ?)
            """,
            menu_name,
            inv_id,
            rate
        )

        inserted += 1

    print(
        f"  Inserted {inserted} "
        f"consumption mappings"
    )

    return inserted


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    print("\n===================================")
    print("SEED DATA")
    print("===================================")

    bier_conn = get_bier_connection()
    bier_cursor = bier_conn.cursor()

    try:

        # --------------------------
        # INVENTORY ITEMS
        # --------------------------

        print("\n--- Inventory Items ---")

        items_inserted = seed_inventory_items(
            bier_cursor
        )

        # --------------------------
        # GET ITEM ID MAP
        # --------------------------

        item_map = get_item_id_map(bier_cursor)

        print(f"\n  Item ID Map:")

        for name, iid in item_map.items():
            print(f"    {name} = {iid}")

        # --------------------------
        # MENU CONSUMPTION MAPPINGS
        # --------------------------

        print("\n--- Menu Consumption Mappings ---")

        mappings_inserted = seed_menu_consumption(
            bier_cursor,
            item_map
        )

        # --------------------------
        # COMMIT
        # --------------------------

        bier_conn.commit()

        print("\n===================================")
        print("SEED COMPLETE")
        print("===================================")
        print(
            f"Inventory Items  : "
            f"{items_inserted} new"
        )
        print(
            f"Consumption Maps : "
            f"{mappings_inserted} inserted"
        )

    except Exception as e:

        bier_conn.rollback()

        print(f"\nERROR: {e}")
        print("Transaction rolled back.")

    finally:

        bier_cursor.close()
        bier_conn.close()
