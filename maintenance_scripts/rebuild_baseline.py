import os
import sys
import django

sys.path.append(r'd:\BS\sync_engine')
import sync

import pyodbc

conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=VANGROTIPARKDB;UID=sa;PWD=sqlsa;TrustServerCertificate=yes;"
vang_conn = pyodbc.connect(conn_str)
vang_cursor = vang_conn.cursor()

bier_conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=BIERSYMPHONYDB;UID=sa;PWD=sqlsa;TrustServerCertificate=yes;"
bier_conn = pyodbc.connect(bier_conn_str)
bier_cursor = bier_conn.cursor()

# Get current state
vang_cursor.execute("""
    SELECT
        B.BillId,
        MI.IName,
        SUM(KT.SaleQty) as TotalQty
    FROM dbo.POS_Tab_KOTBill B
    INNER JOIN dbo.POS_Tab_KOTBill_Details BD ON B.BillId = BD.BillId
    INNER JOIN dbo.POS_TAB_KOTTRANSACTIONDATA KT ON BD.KtNo = KT.KTNo
    INNER JOIN (
        SELECT ICode, IName
        FROM dbo.IN_Menu_Items
        GROUP BY ICode, IName
    ) MI ON KT.ICode = MI.ICode
    WHERE B.BillSettled = 1
    GROUP BY B.BillId, MI.IName
""")

current_state = {}
for row in vang_cursor.fetchall():
    key = (row.BillId, row.IName)
    current_state[key] = float(row.TotalQty)

print(f"Loaded {len(current_state)} rows from POS.")

# Rebuild snapshot manually
sync.rebuild_snapshot(bier_cursor, bier_conn, current_state)
print("Snapshot fully rebuilt! Baseline established.")
