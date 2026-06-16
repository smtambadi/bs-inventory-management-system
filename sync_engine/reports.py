import argparse
from datetime import datetime, timedelta

from db import get_bier_connection


# ==================================================
# TABLE FORMATTING HELPERS
# ==================================================

def format_table(headers, rows, alignments=None):
    """
    Build a formatted table string with column headers
    and separators. No external dependencies.

    Parameters
    ----------
    headers    : list of str   – column header labels
    rows       : list of tuple – data rows
    alignments : list of str   – 'l' (left) or 'r' (right)
                                 per column; defaults to left
    """

    if not rows:
        return None

    # -- Default all columns to left-aligned --
    if alignments is None:
        alignments = ["l"] * len(headers)

    # -- Convert every cell to a string --
    str_rows = []
    for row in rows:
        str_rows.append(
            [str(v) if v is not None else "" for v in row]
        )

    # -- Compute max width per column --
    col_widths = []
    for i, header in enumerate(headers):
        max_w = len(header)
        for row in str_rows:
            if i < len(row):
                max_w = max(max_w, len(row[i]))
        col_widths.append(max_w)

    # -- Build header line --
    header_parts = []
    for i, header in enumerate(headers):
        if alignments[i] == "r":
            header_parts.append(header.rjust(col_widths[i]))
        else:
            header_parts.append(header.ljust(col_widths[i]))

    header_line = " | ".join(header_parts)

    # -- Build separator --
    sep_parts = []
    for w in col_widths:
        sep_parts.append("-" * w)
    separator = "-+-".join(sep_parts)

    # -- Build data lines --
    data_lines = []
    for row in str_rows:
        parts = []
        for i in range(len(headers)):
            cell = row[i] if i < len(row) else ""
            if alignments[i] == "r":
                parts.append(cell.rjust(col_widths[i]))
            else:
                parts.append(cell.ljust(col_widths[i]))
        data_lines.append(" | ".join(parts))

    # -- Assemble --
    lines = [header_line, separator] + data_lines
    return "\n".join(lines)


def print_report_header(title, date_from=None, date_to=None):
    """Print a consistent report banner."""

    print("")
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)

    if date_from and date_to:
        print(
            f"  Period : {date_from}  to  {date_to}"
        )
        print("-" * 60)

    print("")


def print_report_footer(row_count):
    """Print a consistent report footer."""

    print("")
    print("-" * 60)
    print(f"  Total rows: {row_count}")
    print("=" * 60)
    print("")


# ==================================================
# REPORT 1 — CURRENT STOCK
# ==================================================

def report_stock():
    """
    Show current stock levels for all active
    inventory items, with reorder warnings.
    """

    print_report_header("CURRENT STOCK REPORT")

    conn = get_bier_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            i.ItemName,
            i.Unit,
            ISNULL(SUM(t.Quantity), 0) AS CurrentStock,
            i.ReorderLevel,
            CASE
                WHEN ISNULL(SUM(t.Quantity), 0) <= i.ReorderLevel
                THEN '⚠ LOW'
                ELSE 'OK'
            END AS Status
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

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    if not rows:
        print("No data found.")
        return

    # -- Format results --
    table_rows = []
    for row in rows:
        table_rows.append((
            row.ItemName,
            row.Unit or "",
            f"{row.CurrentStock:,.2f}",
            f"{row.ReorderLevel:,.2f}",
            row.Status
        ))

    headers = [
        "Item Name",
        "Unit",
        "Current Stock",
        "Reorder Level",
        "Status"
    ]

    alignments = ["l", "l", "r", "r", "l"]

    output = format_table(headers, table_rows, alignments)
    print(output)

    print_report_footer(len(table_rows))


# ==================================================
# REPORT 2 — PURCHASES
# ==================================================

def report_purchases(date_from, date_to):
    """
    Show purchase details within the selected
    date range, broken down by line item.
    """

    print_report_header(
        "PURCHASE REPORT",
        date_from,
        date_to
    )

    conn = get_bier_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            p.PurchaseDate,
            p.SupplierName,
            p.InvoiceNumber,
            i.ItemName,
            pi.Quantity,
            i.Unit,
            pi.UnitPrice,
            pi.TotalPrice
        FROM dbo.Purchase p
        JOIN dbo.PurchaseItem pi
            ON p.PurchaseId = pi.PurchaseId
        JOIN dbo.InventoryItem i
            ON pi.InventoryItemId = i.InventoryItemId
        WHERE p.PurchaseDate >= ?
          AND p.PurchaseDate < DATEADD(day, 1, ?)
        ORDER BY
            p.PurchaseDate DESC,
            p.PurchaseId
        """,
        date_from,
        date_to
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    if not rows:
        print("No data found for the selected period.")
        return

    # -- Format results --
    table_rows = []
    grand_total = 0.0

    for row in rows:
        purchase_date = row.PurchaseDate
        if hasattr(purchase_date, "strftime"):
            purchase_date = purchase_date.strftime("%Y-%m-%d")

        line_total = float(row.TotalPrice or 0)
        grand_total += line_total

        table_rows.append((
            str(purchase_date),
            row.SupplierName or "",
            row.InvoiceNumber or "",
            row.ItemName,
            f"{row.Quantity:,.2f}",
            row.Unit or "",
            f"{row.UnitPrice:,.2f}",
            f"{line_total:,.2f}"
        ))

    headers = [
        "Date",
        "Supplier",
        "Invoice #",
        "Item Name",
        "Qty",
        "Unit",
        "Unit Price",
        "Total Price"
    ]

    alignments = ["l", "l", "l", "l", "r", "l", "r", "r"]

    output = format_table(headers, table_rows, alignments)
    print(output)

    print_report_footer(len(table_rows))
    print(f"  Grand Total: {grand_total:,.2f}")
    print("")


# ==================================================
# REPORT 3 — CONSUMPTION
# ==================================================

def report_consumption(date_from, date_to):
    """
    Show total consumed quantity per inventory
    item within the selected date range.
    """

    print_report_header(
        "CONSUMPTION REPORT",
        date_from,
        date_to
    )

    conn = get_bier_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            i.ItemName,
            i.Unit,
            SUM(ABS(t.Quantity)) AS ConsumedQty
        FROM dbo.InventoryTransaction t
        JOIN dbo.InventoryItem i
            ON t.InventoryItemId = i.InventoryItemId
        WHERE t.TransactionType = 'SALE'
          AND t.Quantity < 0
          AND t.TransactionDate >= ?
          AND t.TransactionDate < DATEADD(day, 1, ?)
        GROUP BY
            i.InventoryItemId,
            i.ItemName,
            i.Unit
        ORDER BY ConsumedQty DESC
        """,
        date_from,
        date_to
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    if not rows:
        print("No data found for the selected period.")
        return

    # -- Format results --
    table_rows = []
    for row in rows:
        table_rows.append((
            row.ItemName,
            row.Unit or "",
            f"{row.ConsumedQty:,.4f}"
        ))

    headers = [
        "Item Name",
        "Unit",
        "Consumed Qty"
    ]

    alignments = ["l", "l", "r"]

    output = format_table(headers, table_rows, alignments)
    print(output)

    print_report_footer(len(table_rows))


# ==================================================
# REPORT 4 — INVENTORY LEDGER
# ==================================================

def report_ledger(date_from, date_to):
    """
    Show a detailed transaction ledger with running
    balance for one or all inventory items.
    """

    conn = get_bier_connection()
    cursor = conn.cursor()

    # -- List available items --
    cursor.execute(
        """
        SELECT
            InventoryItemId,
            ItemName
        FROM dbo.InventoryItem
        WHERE IsActive = 1
        ORDER BY ItemName
        """
    )

    items = cursor.fetchall()

    if not items:
        print("\nNo active inventory items found.")
        cursor.close()
        conn.close()
        return

    print("")
    print("=" * 40)
    print("  SELECT INVENTORY ITEM")
    print("=" * 40)
    print("  0 : ALL items")

    for idx, item in enumerate(items, start=1):
        print(
            f"  {idx} : {item.ItemName}"
        )

    print("")

    # -- Get user selection --
    try:
        choice = int(input("Enter choice (number): "))
    except (ValueError, EOFError):
        choice = 0

    item_filter = None
    item_label = "ALL ITEMS"

    if 1 <= choice <= len(items):
        item_filter = items[choice - 1].InventoryItemId
        item_label = items[choice - 1].ItemName

    print_report_header(
        f"INVENTORY LEDGER — {item_label}",
        date_from,
        date_to
    )

    # -- Build query --
    if item_filter is not None:
        cursor.execute(
            """
            SELECT
                t.TransactionDate,
                t.TransactionType,
                t.Quantity,
                t.ReferenceType,
                t.ReferenceId,
                t.TransactionId
            FROM dbo.InventoryTransaction t
            WHERE t.InventoryItemId = ?
              AND t.TransactionDate >= ?
              AND t.TransactionDate < DATEADD(day, 1, ?)
            ORDER BY
                t.TransactionDate,
                t.TransactionId
            """,
            item_filter,
            date_from,
            date_to
        )
    else:
        cursor.execute(
            """
            SELECT
                t.TransactionDate,
                t.TransactionType,
                t.Quantity,
                t.ReferenceType,
                t.ReferenceId,
                t.TransactionId,
                i.ItemName
            FROM dbo.InventoryTransaction t
            JOIN dbo.InventoryItem i
                ON t.InventoryItemId = i.InventoryItemId
            WHERE t.TransactionDate >= ?
              AND t.TransactionDate < DATEADD(day, 1, ?)
            ORDER BY
                i.ItemName,
                t.TransactionDate,
                t.TransactionId
            """,
            date_from,
            date_to
        )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    if not rows:
        print("No data found for the selected period.")
        return

    # -- Calculate running balance --
    table_rows = []
    running_balance = 0.0
    current_item = None

    for row in rows:

        # -- Detect item boundary when showing ALL --
        if item_filter is None:
            row_item = row.ItemName
        else:
            row_item = item_label

        if row_item != current_item:
            running_balance = 0.0
            current_item = row_item

            # -- Insert a separator row for clarity --
            if table_rows:
                table_rows.append(
                    ("", "", "", "", "", "", "")
                )

        running_balance += float(row.Quantity)

        txn_date = row.TransactionDate
        if hasattr(txn_date, "strftime"):
            txn_date = txn_date.strftime(
                "%Y-%m-%d %H:%M"
            )

        ref_id = (
            str(row.ReferenceId)
            if row.ReferenceId is not None
            else ""
        )

        table_rows.append((
            current_item if item_filter is None else "",
            str(txn_date),
            row.TransactionType,
            f"{row.Quantity:+,.4f}",
            f"{running_balance:,.4f}",
            row.ReferenceType or "",
            ref_id
        ))

    if item_filter is not None:
        headers = [
            "",
            "Date",
            "Type",
            "Quantity",
            "Balance",
            "Ref Type",
            "Ref Id"
        ]
    else:
        headers = [
            "Item",
            "Date",
            "Type",
            "Quantity",
            "Balance",
            "Ref Type",
            "Ref Id"
        ]

    alignments = ["l", "l", "l", "r", "r", "l", "r"]

    output = format_table(headers, table_rows, alignments)
    print(output)

    print_report_footer(len(table_rows))


# ==================================================
# REPORT 5 — SALES VS USAGE
# ==================================================

def report_sales_vs_usage(date_from, date_to):
    """
    Compare POS-detected sales quantities against
    returned quantities from InventoryDelta.
    """

    print_report_header(
        "POS SALES vs INVENTORY USAGE",
        date_from,
        date_to
    )

    conn = get_bier_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            d.ItemName AS MenuItemSold,
            SUM(
                CASE
                    WHEN d.EventType IN ('NEW', 'INCREASED')
                    THEN d.QtyDifference
                    ELSE 0
                END
            ) AS QtySold,
            SUM(
                CASE
                    WHEN d.EventType IN ('REDUCED', 'REMOVED')
                    THEN ABS(d.QtyDifference)
                    ELSE 0
                END
            ) AS QtyReturned
        FROM dbo.InventoryDelta d
        WHERE d.EventTime >= ?
          AND d.EventTime < DATEADD(day, 1, ?)
        GROUP BY d.ItemName
        ORDER BY QtySold DESC
        """,
        date_from,
        date_to
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    if not rows:
        print("No data found for the selected period.")
        return

    # -- Format results --
    table_rows = []
    for row in rows:
        qty_sold = float(row.QtySold or 0)
        qty_returned = float(row.QtyReturned or 0)
        net = qty_sold - qty_returned

        table_rows.append((
            row.MenuItemSold,
            f"{qty_sold:,.2f}",
            f"{qty_returned:,.2f}",
            f"{net:,.2f}"
        ))

    headers = [
        "Menu Item",
        "Qty Sold",
        "Qty Returned",
        "Net"
    ]

    alignments = ["l", "r", "r", "r"]

    output = format_table(headers, table_rows, alignments)
    print(output)

    print_report_footer(len(table_rows))


# ==================================================
# CLI ENTRY POINT
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Restaurant Inventory Intelligence System"
            " — Reports"
        )
    )

    parser.add_argument(
        "--report",
        required=True,
        choices=[
            "stock",
            "purchases",
            "consumption",
            "ledger",
            "sales-vs-usage"
        ],
        help="Report to generate"
    )

    parser.add_argument(
        "--from",
        dest="date_from",
        default=None,
        help="Start date (YYYY-MM-DD), default: 30 days ago"
    )

    parser.add_argument(
        "--to",
        dest="date_to",
        default=None,
        help="End date (YYYY-MM-DD), default: today"
    )

    args = parser.parse_args()

    # -- Resolve default date range (last 30 days) --
    if args.date_to:
        date_to = args.date_to
    else:
        date_to = datetime.now().strftime("%Y-%m-%d")

    if args.date_from:
        date_from = args.date_from
    else:
        date_from = (
            datetime.now() - timedelta(days=30)
        ).strftime("%Y-%m-%d")

    # -- Dispatch to the selected report --
    if args.report == "stock":
        report_stock()

    elif args.report == "purchases":
        report_purchases(date_from, date_to)

    elif args.report == "consumption":
        report_consumption(date_from, date_to)

    elif args.report == "ledger":
        report_ledger(date_from, date_to)

    elif args.report == "sales-vs-usage":
        report_sales_vs_usage(date_from, date_to)


if __name__ == "__main__":
    main()
