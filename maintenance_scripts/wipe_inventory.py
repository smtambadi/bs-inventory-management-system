import os
import sys
import django

sys.path.append(r'd:\BS\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Disable foreign key checks if any, though MS SQL uses different syntax.
    # We will just delete in order.
    
    cursor.execute("DELETE FROM BIERSYMPHONYDB.dbo.InventoryTransaction")
    print("Deleted all Inventory Transactions")
    
    cursor.execute("DELETE FROM BIERSYMPHONYDB.dbo.InventoryDelta")
    print("Deleted all Inventory Deltas")
    
    cursor.execute("DELETE FROM BIERSYMPHONYDB.dbo.SyncSnapshot")
    print("Deleted all Sync Snapshots")
    
    cursor.execute("DELETE FROM BIERSYMPHONYDB.dbo.PurchaseItem")
    print("Deleted all Purchase Items")
    
    cursor.execute("DELETE FROM BIERSYMPHONYDB.dbo.Purchase")
    print("Deleted all Purchases")
    
    # Reseed identity columns so new entries start at 1
    cursor.execute("DBCC CHECKIDENT ('BIERSYMPHONYDB.dbo.InventoryTransaction', RESEED, 0)")
    cursor.execute("DBCC CHECKIDENT ('BIERSYMPHONYDB.dbo.InventoryDelta', RESEED, 0)")
    cursor.execute("DBCC CHECKIDENT ('BIERSYMPHONYDB.dbo.PurchaseItem', RESEED, 0)")
    cursor.execute("DBCC CHECKIDENT ('BIERSYMPHONYDB.dbo.Purchase', RESEED, 0)")
    print("Reseeded Identity columns")
    
    connection.commit()
    
print("All inventory has been reset to zero!")
