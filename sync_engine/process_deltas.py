from db import get_bier_connection


# ==================================================
# DELTA PROCESSING ENGINE
# Converts POS sales events (InventoryDelta) into
# inventory transactions using MenuItemConsumption
# mappings.
# ==================================================


try:

    # ==================================================
    # STEP 1 - CONNECT TO BIERSYMPHONYDB
    # ==================================================

    bier_conn = get_bier_connection()
    bier_cursor = bier_conn.cursor()

    print("===================================")
    print("DELTA PROCESSING ENGINE")
    print("===================================")

    print("\nConnected to BIERSYMPHONYDB")


    # ==================================================
    # STEP 2 - FETCH UNPROCESSED DELTAS
    # ==================================================

    bier_cursor.execute(
        """
        SELECT
            DeltaId,
            SyncRunId,
            BillId,
            ItemName,
            EventType,
            OldQty,
            NewQty,
            QtyDifference,
            EventTime
        FROM dbo.InventoryDelta
        WHERE Processed = 0
        ORDER BY DeltaId
        """
    )

    deltas = bier_cursor.fetchall()

    print(
        f"Unprocessed Deltas : "
        f"{len(deltas)}"
    )

    if len(deltas) == 0:

        print("No unprocessed deltas found.")

        bier_cursor.close()
        bier_conn.close()

        exit()


    # ==================================================
    # STEP 3 - LOAD MENU ITEM CONSUMPTION MAPPINGS
    # ==================================================

    bier_cursor.execute(
        """
        SELECT
            MenuItemName,
            InventoryItemId,
            ConsumptionPerQty
        FROM dbo.MenuItemConsumption
        """
    )

    mapping_rows = bier_cursor.fetchall()

    # Build dict: {MenuItemName: [(InventoryItemId, ConsumptionPerQty), ...]}
    consumption_map = {}

    for row in mapping_rows:

        menu_name = row.MenuItemName

        if menu_name not in consumption_map:
            consumption_map[menu_name] = []

        consumption_map[menu_name].append(
            (
                row.InventoryItemId,
                float(row.ConsumptionPerQty)
            )
        )

    print(
        f"Consumption Mappings Loaded : "
        f"{len(consumption_map)} menu items"
    )


    # ==================================================
    # STEP 4 - PROCESS EACH DELTA
    # ==================================================

    print("\n===================================")
    print("PROCESSING DELTAS")
    print("===================================")

    total_deltas_processed = 0
    total_transactions_created = 0
    skipped_items = []

    for delta in deltas:

        delta_id = delta.DeltaId
        item_name = delta.ItemName
        qty_difference = float(delta.QtyDifference)
        event_time = delta.EventTime
        event_type = delta.EventType


        # ---------------------------
        # LOOKUP CONSUMPTION MAPPING
        # ---------------------------

        if item_name not in consumption_map:

            print(
                f"  WARNING: No mapping for "
                f"'{item_name}' "
                f"(DeltaId={delta_id}) - skipping"
            )

            skipped_items.append(item_name)

            # Mark as processed even if skipped
            bier_cursor.execute(
                """
                UPDATE dbo.InventoryDelta
                SET Processed = 1
                WHERE DeltaId = ?
                """,
                delta_id
            )

            total_deltas_processed += 1
            continue


        # ---------------------------
        # CREATE INVENTORY TRANSACTIONS
        # ---------------------------

        mappings = consumption_map[item_name]

        for (
            inventory_item_id,
            consumption_per_qty
        ) in mappings:

            consumption_qty = (
                abs(qty_difference) * consumption_per_qty
            )

            # NEW or INCREASED (QtyDifference > 0):
            #   Items sold -> stock decreases (negative)
            # REDUCED or REMOVED (QtyDifference < 0):
            #   Items returned -> stock restored (positive)

            if qty_difference > 0:
                transaction_qty = -consumption_qty
            else:
                transaction_qty = consumption_qty

            bier_cursor.execute(
                """
                INSERT INTO dbo.InventoryTransaction
                (
                    InventoryItemId,
                    TransactionType,
                    Quantity,
                    ReferenceType,
                    ReferenceId,
                    TransactionDate
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                inventory_item_id,
                'SALE',
                transaction_qty,
                'InventoryDelta',
                delta_id,
                event_time
            )

            total_transactions_created += 1

        print(
            f"  DeltaId={delta_id} | "
            f"{item_name} | "
            f"{event_type} | "
            f"QtyDiff={qty_difference} | "
            f"Txns={len(mappings)}"
        )


        # ---------------------------
        # MARK DELTA AS PROCESSED
        # ---------------------------

        bier_cursor.execute(
            """
            UPDATE dbo.InventoryDelta
            SET Processed = 1
            WHERE DeltaId = ?
            """,
            delta_id
        )

        total_deltas_processed += 1


    # ==================================================
    # STEP 5 - COMMIT ALL CHANGES
    # ==================================================

    bier_conn.commit()


    # ==================================================
    # STEP 6 - PRINT SUMMARY
    # ==================================================

    print("\n===================================")
    print("PROCESSING SUMMARY")
    print("===================================")

    print(
        f"Total Deltas Processed      : "
        f"{total_deltas_processed}"
    )

    print(
        f"Total Transactions Created  : "
        f"{total_transactions_created}"
    )

    print(
        f"Skipped (No Mapping)        : "
        f"{len(skipped_items)}"
    )

    if skipped_items:

        # Deduplicate for cleaner output
        unique_skipped = sorted(set(skipped_items))

        print("\nSkipped Items:")

        for item in unique_skipped:

            count = skipped_items.count(item)

            print(
                f"  - {item} "
                f"({count} occurrence(s))"
            )


    # ==================================================
    # STEP 7 - CURRENT STOCK LEVELS
    # ==================================================

    print("\n===================================")
    print("CURRENT STOCK LEVELS")
    print("===================================")

    bier_cursor.execute(
        """
        SELECT
            i.ItemName,
            i.Unit,
            ISNULL(SUM(t.Quantity), 0) AS CurrentStock,
            i.ReorderLevel
        FROM dbo.InventoryItem i
        LEFT JOIN dbo.InventoryTransaction t
            ON i.InventoryItemId = t.InventoryItemId
        WHERE i.IsActive = 1
        GROUP BY
            i.InventoryItemId,
            i.ItemName,
            i.Unit,
            i.ReorderLevel
        """
    )

    stock_rows = bier_cursor.fetchall()

    low_stock_items = []

    for row in stock_rows:

        current_stock = float(row.CurrentStock)
        reorder_level = float(row.ReorderLevel)

        status = ""

        if current_stock <= reorder_level:
            status = " *** LOW STOCK ***"
            low_stock_items.append(row.ItemName)

        print(
            f"  {row.ItemName} | "
            f"{current_stock} {row.Unit} | "
            f"Reorder at {reorder_level}"
            f"{status}"
        )


    # ---------------------------
    # REORDER WARNINGS
    # ---------------------------

    if low_stock_items:

        print(
            f"\n*** WARNING: {len(low_stock_items)} "
            f"item(s) at or below reorder level! ***"
        )

        for item in low_stock_items:

            print(
                f"  -> REORDER: {item}"
            )


    # ==================================================
    # CLEANUP
    # ==================================================

    bier_cursor.close()
    bier_conn.close()

    print("\nDelta Processing Completed Successfully")


except Exception as e:

    print(
        f"\nERROR: {e}"
    )

    # Rollback uncommitted changes on error
    try:
        bier_conn.rollback()
        print("Transaction rolled back.")
    except Exception:
        pass

    # Clean up connections
    try:
        bier_cursor.close()
        bier_conn.close()
    except Exception:
        pass
