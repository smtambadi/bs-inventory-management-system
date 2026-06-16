import os
import sys
import django
from datetime import datetime

sys.path.append(r'd:\BS\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Get IDs
    cursor.execute("SELECT ItemName, InventoryItemId FROM BIERSYMPHONYDB.dbo.InventoryItem")
    items = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Delete existing purchases to be safe
    cursor.execute("DELETE FROM BIERSYMPHONYDB.dbo.InventoryTransaction WHERE TransactionType = 'PURCHASE'")
    
    # Insert Purchases
    purchases = [
        (items.get('Chicken'), 5.00, 'PurchaseOrder', 1, 'Initial Chicken Stock', '2026-06-15 08:00:00'),
        (items.get('Mutton'), 2.00, 'PurchaseOrder', 2, 'Initial Mutton Stock', '2026-06-15 08:00:00'),
        (items.get('Rice'), 2.00, 'PurchaseOrder', 3, 'Initial Rice Stock', '2026-06-15 08:00:00')
    ]
    
    for p in purchases:
        if p[0]:
            cursor.execute("""
                INSERT INTO BIERSYMPHONYDB.dbo.InventoryTransaction
                (InventoryItemId, TransactionType, Quantity, ReferenceType, ReferenceId, Notes, CreatedAt)
                VALUES (%s, 'PURCHASE', %s, %s, %s, %s, %s)
            """, p)
    
    connection.commit()
    print("Re-inserted base purchases.")
