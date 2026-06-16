from db import get_bier_connection
from datetime import datetime
from decimal import Decimal, InvalidOperation


# ==================================================
# HELPER - DISPLAY INVENTORY ITEMS
# ==================================================

def display_inventory_items(cursor):
    """Query and display all active InventoryItem records."""

    cursor.execute(
        """
        SELECT
            InventoryItemId,
            ItemName,
            Unit
        FROM dbo.InventoryItem
        WHERE IsActive = 1
        ORDER BY InventoryItemId
        """
    )

    items = cursor.fetchall()

    if not items:
        print("\nNo active inventory items found.")
        return []

    print("\n===================================")
    print("AVAILABLE INVENTORY ITEMS")
    print("===================================")

    print(
        f"{'ID':<6} "
        f"{'Item Name':<30} "
        f"{'Unit':<10}"
    )

    print("-" * 48)

    for item in items:

        print(
            f"{item.InventoryItemId:<6} "
            f"{item.ItemName:<30} "
            f"{item.Unit:<10}"
        )

    return items


# ==================================================
# HELPER - DISPLAY CURRENT STOCK
# ==================================================

def display_current_stock(cursor):
    """Display current stock levels for all items."""

    cursor.execute(
        """
        SELECT
            i.ItemName,
            i.Unit,
            ISNULL(SUM(t.Quantity), 0) AS CurrentStock
        FROM dbo.InventoryItem i
        LEFT JOIN dbo.InventoryTransaction t
            ON i.InventoryItemId = t.InventoryItemId
        GROUP BY
            i.InventoryItemId,
            i.ItemName,
            i.Unit
        ORDER BY i.ItemName
        """
    )

    rows = cursor.fetchall()

    print("\n===================================")
    print("CURRENT STOCK LEVELS")
    print("===================================")

    print(
        f"{'Item Name':<30} "
        f"{'Unit':<10} "
        f"{'Stock':>12}"
    )

    print("-" * 54)

    for row in rows:

        print(
            f"{row.ItemName:<30} "
            f"{row.Unit:<10} "
            f"{row.CurrentStock:>12.4f}"
        )


# ==================================================
# HELPER - DISPLAY PURCHASE SUMMARY
# ==================================================

def display_summary(supplier_name, invoice_number,
                    purchase_date, line_items, total_amount):
    """Display the full purchase summary before confirmation."""

    print("\n===================================")
    print("PURCHASE SUMMARY")
    print("===================================")

    print(f"Supplier     : {supplier_name}")
    print(f"Invoice #    : {invoice_number}")
    print(f"Purchase Date: {purchase_date}")

    print(
        f"\n{'#':<4} "
        f"{'Item ID':<9} "
        f"{'Quantity':>12} "
        f"{'Unit Price':>12} "
        f"{'Total Price':>14}"
    )

    print("-" * 53)

    for idx, item in enumerate(line_items, start=1):

        print(
            f"{idx:<4} "
            f"{item['inventory_item_id']:<9} "
            f"{item['quantity']:>12.4f} "
            f"{item['unit_price']:>12.2f} "
            f"{item['total_price']:>14.2f}"
        )

    print("-" * 53)

    print(
        f"{'TOTAL AMOUNT':>39} "
        f"{total_amount:>14.2f}"
    )


# ==================================================
# STEP 1 - COLLECT PURCHASE HEADER INFO
# ==================================================

def collect_header_info():
    """Prompt user for supplier name, invoice number, and date."""

    print("\n===================================")
    print("NEW PURCHASE ENTRY")
    print("===================================")

    supplier_name = input(
        "\nSupplier Name : "
    ).strip()

    if not supplier_name:
        print("ERROR: Supplier name is required.")
        return None

    invoice_number = input(
        "Invoice Number: "
    ).strip()

    if not invoice_number:
        print("ERROR: Invoice number is required.")
        return None

    today_str = datetime.now().strftime(
        "%Y-%m-%d"
    )

    date_input = input(
        f"Purchase Date [{today_str}]: "
    ).strip()

    if not date_input:
        purchase_date = today_str
    else:
        # Validate date format
        try:
            datetime.strptime(
                date_input, "%Y-%m-%d"
            )
            purchase_date = date_input
        except ValueError:
            print(
                "ERROR: Invalid date format. "
                "Use YYYY-MM-DD."
            )
            return None

    return {
        "supplier_name": supplier_name,
        "invoice_number": invoice_number,
        "purchase_date": purchase_date,
    }


# ==================================================
# STEP 2 - COLLECT LINE ITEMS
# ==================================================

def collect_line_items(cursor):
    """Loop to collect purchase line items from the user."""

    items = display_inventory_items(cursor)

    if not items:
        return []

    # Build a set of valid IDs for validation
    valid_ids = set(
        item.InventoryItemId for item in items
    )

    line_items = []

    while True:

        print("\n--- Add Item ---")

        # ---------------------------
        # Inventory Item ID
        # ---------------------------

        id_input = input(
            "InventoryItemId (or 'done' to finish): "
        ).strip()

        if id_input.lower() == "done":
            break

        try:
            item_id = int(id_input)
        except ValueError:
            print("ERROR: Enter a valid integer ID.")
            continue

        if item_id not in valid_ids:
            print(
                f"ERROR: Item ID {item_id} "
                f"not found in inventory."
            )
            continue

        # ---------------------------
        # Quantity
        # ---------------------------

        qty_input = input(
            "Quantity        : "
        ).strip()

        try:
            quantity = Decimal(qty_input)
        except (InvalidOperation, ValueError):
            print("ERROR: Enter a valid quantity.")
            continue

        if quantity <= 0:
            print("ERROR: Quantity must be positive.")
            continue

        # ---------------------------
        # Unit Price
        # ---------------------------

        price_input = input(
            "Unit Price      : "
        ).strip()

        try:
            unit_price = Decimal(price_input)
        except (InvalidOperation, ValueError):
            print("ERROR: Enter a valid unit price.")
            continue

        if unit_price < 0:
            print("ERROR: Price cannot be negative.")
            continue

        # ---------------------------
        # Calculate Total
        # ---------------------------

        total_price = quantity * unit_price

        line_items.append(
            {
                "inventory_item_id": item_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": total_price,
            }
        )

        print(
            f"Added: ItemId={item_id}, "
            f"Qty={quantity}, "
            f"Price={unit_price}, "
            f"Total={total_price:.2f}"
        )

    return line_items


# ==================================================
# STEP 3 - SAVE PURCHASE TO DATABASE
# ==================================================

def save_purchase(cursor, conn, header, line_items):
    """
    Insert Purchase, PurchaseItem, and InventoryTransaction
    records inside a single transaction.
    """

    total_amount = sum(
        item["total_price"] for item in line_items
    )

    # ---------------------------
    # INSERT Purchase
    # ---------------------------

    cursor.execute(
        """
        INSERT INTO dbo.Purchase
        (
            SupplierName,
            InvoiceNumber,
            PurchaseDate,
            TotalAmount
        )
        VALUES (?, ?, ?, ?)
        """,
        header["supplier_name"],
        header["invoice_number"],
        header["purchase_date"],
        float(total_amount),
    )

    # ---------------------------
    # Get Generated PurchaseId
    # ---------------------------

    cursor.execute(
        "SELECT SCOPE_IDENTITY()"
    )

    purchase_id = cursor.fetchone()[0]

    purchase_id = int(purchase_id)

    print(
        f"\nPurchase created with "
        f"PurchaseId = {purchase_id}"
    )

    # ---------------------------
    # INSERT PurchaseItem rows
    # ---------------------------

    for item in line_items:

        cursor.execute(
            """
            INSERT INTO dbo.PurchaseItem
            (
                PurchaseId,
                InventoryItemId,
                Quantity,
                UnitPrice,
                TotalPrice
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            purchase_id,
            item["inventory_item_id"],
            float(item["quantity"]),
            float(item["unit_price"]),
            float(item["total_price"]),
        )

    print(
        f"Inserted {len(line_items)} "
        f"PurchaseItem row(s)"
    )

    # ---------------------------
    # INSERT InventoryTransaction rows
    # ---------------------------

    for item in line_items:

        cursor.execute(
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
            item["inventory_item_id"],
            "PURCHASE",
            float(item["quantity"]),
            "Purchase",
            purchase_id,
            header["purchase_date"],
        )

    print(
        f"Inserted {len(line_items)} "
        f"InventoryTransaction row(s)"
    )

    # ---------------------------
    # COMMIT
    # ---------------------------

    conn.commit()

    print("\nTransaction committed successfully.")

    return purchase_id


# ==================================================
# MAIN - PURCHASE ENTRY FLOW
# ==================================================

if __name__ == "__main__":

    print("\n===================================")
    print("PURCHASE RECORDING SYSTEM")
    print("===================================")

    try:

        # ---------------------------
        # Collect Header
        # ---------------------------

        header = collect_header_info()

        if header is None:
            print("\nPurchase cancelled.")
            exit()

        # ---------------------------
        # Connect to Database
        # ---------------------------

        conn = get_bier_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        # ---------------------------
        # Collect Line Items
        # ---------------------------

        line_items = collect_line_items(cursor)

        if not line_items:
            print("\nNo items added. Purchase cancelled.")
            cursor.close()
            conn.close()
            exit()

        # ---------------------------
        # Show Summary & Confirm
        # ---------------------------

        total_amount = sum(
            item["total_price"]
            for item in line_items
        )

        display_summary(
            header["supplier_name"],
            header["invoice_number"],
            header["purchase_date"],
            line_items,
            total_amount,
        )

        confirm = input(
            "\nConfirm and save? (y/n): "
        ).strip().lower()

        if confirm != "y":
            print("\nPurchase cancelled by user.")
            cursor.close()
            conn.close()
            exit()

        # ---------------------------
        # Save to Database
        # ---------------------------

        save_purchase(
            cursor,
            conn,
            header,
            line_items,
        )

        # ---------------------------
        # Display Current Stock
        # ---------------------------

        display_current_stock(cursor)

        # ---------------------------
        # Cleanup
        # ---------------------------

        cursor.close()
        conn.close()

        print("\nPurchase Completed Successfully")

    except Exception as e:

        print(f"\nERROR: {e}")

        try:
            conn.rollback()
            print("Transaction rolled back.")
            cursor.close()
            conn.close()
        except Exception:
            pass

        exit(1)
