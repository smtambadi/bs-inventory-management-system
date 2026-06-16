import os
import sys
import django

sys.path.append(r'd:\BS\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT T.TransactionId, T.TransactionType, T.Quantity, T.ReferenceId, I.ItemName
        FROM BIERSYMPHONYDB.dbo.InventoryTransaction T
        JOIN BIERSYMPHONYDB.dbo.InventoryItem I ON T.InventoryItemId = I.InventoryItemId
    """)
    rows = cursor.fetchall()
    print(f"Total Transactions: {len(rows)}")
    for row in rows[:50]:
        print(row)
    if len(rows) > 50:
        print("...")
