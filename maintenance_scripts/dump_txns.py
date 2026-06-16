import os
import sys
import django

sys.path.append(r'd:\BS\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT TransactionId, TransactionType, ReferenceType, Quantity, InventoryItemId FROM BIERSYMPHONYDB.dbo.InventoryTransaction")
    rows = cursor.fetchall()
    print(f"Total Transactions: {len(rows)}")
    for row in rows[:20]:
        print(row)
    if len(rows) > 20:
        print("...")
