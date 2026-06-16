from db import get_pos_connection, get_bier_connection
from datetime import datetime


# ==================================================
# SYNC LOG FUNCTIONS
# ==================================================

def create_sync_run(cursor):
    """
    Create a SyncLog entry at the start of
    each sync run. Returns the SyncRunId.
    """

    cursor.execute(
        """
        INSERT INTO dbo.SyncLog
        (
            SyncStarted,
            RecordsRead,
            Success
        )
        VALUES (GETDATE(), 0, 0)
        """
    )

    cursor.execute(
        """
        SELECT SCOPE_IDENTITY()
        """
    )

    sync_run_id = int(
        cursor.fetchone()[0]
    )

    return sync_run_id


def complete_sync_run(
    cursor,
    sync_run_id,
    records_read,
    success,
    error_message=None
):
    """
    Update the SyncLog entry at the end
    of each sync run.
    """

    cursor.execute(
        """
        UPDATE dbo.SyncLog
        SET
            SyncEnded = GETDATE(),
            RecordsRead = ?,
            Success = ?,
            ErrorMessage = ?
        WHERE Id = ?
        """,
        records_read,
        1 if success else 0,
        error_message,
        sync_run_id
    )


# ==================================================
# WRITE DELTAS
# ==================================================

def write_deltas(
    cursor,
    sync_run_id,
    new_items,
    increased_items,
    reduced_items,
    removed_items
):
    """
    Write all detected changes to
    InventoryDelta with Processed = 0.

    Returns total deltas written.
    """

    delta_count = 0

    # ---------------------------
    # NEW ITEMS
    # ---------------------------

    for key, qty in new_items:

        bill_id, item_name = key

        cursor.execute(
            """
            INSERT INTO dbo.InventoryDelta
            (
                SyncRunId,
                BillId,
                ItemName,
                EventType,
                OldQty,
                NewQty,
                QtyDifference,
                EventTime,
                Processed
            )
            VALUES (?, ?, ?, 'NEW', 0, ?, ?, GETDATE(), 0)
            """,
            sync_run_id,
            bill_id,
            item_name,
            qty,
            qty
        )

        delta_count += 1

    # ---------------------------
    # INCREASED ITEMS
    # ---------------------------

    for key, old_qty, new_qty, delta in increased_items:

        bill_id, item_name = key

        cursor.execute(
            """
            INSERT INTO dbo.InventoryDelta
            (
                SyncRunId,
                BillId,
                ItemName,
                EventType,
                OldQty,
                NewQty,
                QtyDifference,
                EventTime,
                Processed
            )
            VALUES (?, ?, ?, 'INCREASED', ?, ?, ?, GETDATE(), 0)
            """,
            sync_run_id,
            bill_id,
            item_name,
            old_qty,
            new_qty,
            delta
        )

        delta_count += 1

    # ---------------------------
    # REDUCED ITEMS
    # ---------------------------

    for key, old_qty, new_qty, delta in reduced_items:

        bill_id, item_name = key

        cursor.execute(
            """
            INSERT INTO dbo.InventoryDelta
            (
                SyncRunId,
                BillId,
                ItemName,
                EventType,
                OldQty,
                NewQty,
                QtyDifference,
                EventTime,
                Processed
            )
            VALUES (?, ?, ?, 'REDUCED', ?, ?, ?, GETDATE(), 0)
            """,
            sync_run_id,
            bill_id,
            item_name,
            old_qty,
            new_qty,
            -(delta)
        )

        delta_count += 1

    # ---------------------------
    # REMOVED ITEMS
    # ---------------------------

    for key, old_qty in removed_items:

        bill_id, item_name = key

        cursor.execute(
            """
            INSERT INTO dbo.InventoryDelta
            (
                SyncRunId,
                BillId,
                ItemName,
                EventType,
                OldQty,
                NewQty,
                QtyDifference,
                EventTime,
                Processed
            )
            VALUES (?, ?, ?, 'REMOVED', ?, 0, ?, GETDATE(), 0)
            """,
            sync_run_id,
            bill_id,
            item_name,
            old_qty,
            -(old_qty)
        )

        delta_count += 1

    return delta_count


# ==================================================
# REBUILD SNAPSHOT
# ==================================================

def rebuild_snapshot(bier_cursor, bier_conn, current_state):

    print("\nRebuilding Snapshot...")

    bier_cursor.execute(
        """
        DELETE FROM dbo.SyncSnapshot
        """
    )

    for key, qty in current_state.items():

        bill_id, item_name = key

        bier_cursor.execute(
            """
            INSERT INTO dbo.SyncSnapshot
            (
                BillId,
                ItemName,
                Qty
            )
            VALUES (?, ?, ?)
            """,
            bill_id,
            item_name,
            qty
        )

    bier_conn.commit()

    print(
        f"Snapshot rebuilt with "
        f"{len(current_state)} rows"
    )


# ==================================================
# STEP 1 - READ CURRENT POS STATE
# ==================================================

query = """
SELECT
    B.BillId,
    MI.IName,
    KT.SaleQty
FROM VANGROTIPARKDB.dbo.POS_Tab_KOTBill B
INNER JOIN VANGROTIPARKDB.dbo.POS_Tab_KOTBill_Details BD
    ON B.BillId = BD.BillId
INNER JOIN VANGROTIPARKDB.dbo.POS_TAB_KOTTRANSACTIONDATA KT
    ON BD.KtNo = KT.KTNo
INNER JOIN (
    SELECT ICode, IName
    FROM VANGROTIPARKDB.dbo.IN_Menu_Items
    GROUP BY ICode, IName
) MI
    ON KT.ICode = MI.ICode
WHERE B.BillSettled = 1;
"""

pos_conn = get_pos_connection()
pos_cursor = pos_conn.cursor()

pos_cursor.execute(query)

rows = pos_cursor.fetchall()

current_state = {}

for row in rows:

    key = (
        row.BillId,
        row.IName
    )

    qty = float(row.SaleQty)

    # Handle duplicate items in same bill
    if key in current_state:
        current_state[key] += qty
    else:
        current_state[key] = qty

pos_cursor.close()
pos_conn.close()

print("\n===================================")
print("CURRENT POS STATE")
print("===================================")

print(
    f"Current State Rows : "
    f"{len(current_state)}"
)


# ==================================================
# STEP 2 - CONNECT TO BIERSYMPHONYDB
# ==================================================

bier_conn = get_bier_connection()
bier_cursor = bier_conn.cursor()

bier_cursor.execute(
    """
    SELECT COUNT(*)
    FROM dbo.SyncSnapshot
    """
)

snapshot_count = bier_cursor.fetchone()[0]

print(
    f"Snapshot Rows : "
    f"{snapshot_count}"
)


# ==================================================
# FIRST RUN
# ==================================================

if snapshot_count == 0:

    print(
        "\nNo snapshot found."
    )

    inserted_count = 0

    for key, qty in current_state.items():

        bill_id, item_name = key

        bier_cursor.execute(
            """
            INSERT INTO dbo.SyncSnapshot
            (
                BillId,
                ItemName,
                Qty
            )
            VALUES (?, ?, ?)
            """,
            bill_id,
            item_name,
            qty
        )

        inserted_count += 1

    bier_conn.commit()

    print(
        f"\nInserted "
        f"{inserted_count} rows."
    )

    bier_cursor.close()
    bier_conn.close()

    print(
        "\nInitial snapshot created."
    )

    exit()


# ==================================================
# STEP 3 - LOAD SNAPSHOT
# ==================================================

snapshot_state = {}

bier_cursor.execute(
    """
    SELECT
        BillId,
        ItemName,
        Qty
    FROM dbo.SyncSnapshot
    """
)

snapshot_rows = bier_cursor.fetchall()

for row in snapshot_rows:

    key = (
        row.BillId,
        row.ItemName
    )

    snapshot_state[key] = float(
        row.Qty
    )

print(
    f"Snapshot Loaded : "
    f"{len(snapshot_state)}"
)


# ==================================================
# STEP 4 - COMPARE
# ==================================================

new_items = []
increased_items = []
reduced_items = []
removed_items = []


# ---------------------------
# NEW / INCREASED / REDUCED
# ---------------------------

for key, current_qty in current_state.items():

    if key not in snapshot_state:

        new_items.append(
            (
                key,
                current_qty
            )
        )

    else:

        old_qty = snapshot_state[key]

        if current_qty > old_qty:

            increased_items.append(
                (
                    key,
                    old_qty,
                    current_qty,
                    current_qty - old_qty
                )
            )

        elif current_qty < old_qty:

            reduced_items.append(
                (
                    key,
                    old_qty,
                    current_qty,
                    old_qty - current_qty
                )
            )


# ---------------------------
# REMOVED
# ---------------------------

for key, old_qty in snapshot_state.items():

    if key not in current_state:

        removed_items.append(
            (
                key,
                old_qty
            )
        )


# ==================================================
# STEP 5 - PRINT RESULT
# ==================================================

print("\n===================================")
print("SYNC RESULT")
print("===================================")

print(
    f"NEW ITEMS       : "
    f"{len(new_items)}"
)

print(
    f"INCREASED ITEMS : "
    f"{len(increased_items)}"
)

print(
    f"REDUCED ITEMS   : "
    f"{len(reduced_items)}"
)

print(
    f"REMOVED ITEMS   : "
    f"{len(removed_items)}"
)


# ---------------------------
# NEW
# ---------------------------

if new_items:

    print("\nNEW ITEMS")

    for key, qty in new_items:

        bill_id, item_name = key

        print(
            f"Bill={bill_id} | "
            f"{item_name} | "
            f"Qty={qty}"
        )


# ---------------------------
# INCREASED
# ---------------------------

if increased_items:

    print("\nINCREASED ITEMS")

    for (
        key,
        old_qty,
        new_qty,
        delta
    ) in increased_items:

        bill_id, item_name = key

        print(
            f"Bill={bill_id} | "
            f"{item_name} | "
            f"{old_qty} -> {new_qty} "
            f"(+{delta})"
        )


# ---------------------------
# REDUCED
# ---------------------------

if reduced_items:

    print("\nREDUCED ITEMS")

    for (
        key,
        old_qty,
        new_qty,
        delta
    ) in reduced_items:

        bill_id, item_name = key

        print(
            f"Bill={bill_id} | "
            f"{item_name} | "
            f"{old_qty} -> {new_qty} "
            f"(-{delta})"
        )


# ---------------------------
# REMOVED
# ---------------------------

if removed_items:

    print("\nREMOVED ITEMS")

    for (
        key,
        old_qty
    ) in removed_items:

        bill_id, item_name = key

        print(
            f"Bill={bill_id} | "
            f"{item_name} | "
            f"OldQty={old_qty}"
        )


# ==================================================
# STEP 6 - WRITE DELTAS TO DATABASE
# ==================================================

total_changes = (
    len(new_items)
    + len(increased_items)
    + len(reduced_items)
    + len(removed_items)
)

if total_changes > 0:

    try:

        sync_run_id = create_sync_run(
            bier_cursor
        )

        print(
            f"\nSync Run ID : {sync_run_id}"
        )

        delta_count = write_deltas(
            bier_cursor,
            sync_run_id,
            new_items,
            increased_items,
            reduced_items,
            removed_items
        )

        print(
            f"Deltas Written : {delta_count}"
        )

        complete_sync_run(
            bier_cursor,
            sync_run_id,
            len(current_state),
            True
        )

        bier_conn.commit()

        print("Deltas committed successfully")

    except Exception as e:

        bier_conn.rollback()

        print(f"\nERROR writing deltas: {e}")

        # Still try to log the failure
        try:
            complete_sync_run(
                bier_cursor,
                sync_run_id,
                len(current_state),
                False,
                str(e)
            )
            bier_conn.commit()
        except Exception:
            pass

else:

    print("\nNo changes detected. No deltas to write.")


# ==================================================
# STEP 7 - UPDATE SNAPSHOT
# ==================================================

rebuild_snapshot(
    bier_cursor,
    bier_conn,
    current_state
)


bier_cursor.close()
bier_conn.close()

print("\nSync Completed Successfully")