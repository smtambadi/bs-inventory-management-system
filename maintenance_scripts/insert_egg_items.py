import os
import sys
import django

sys.path.append(r'd:\BS\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

items_to_add = [
    ('7227', 'EGG BOTI FRY', 'Egg'),
    ('7161', 'EGG FRIED RICE', 'Egg'),
    ('7160', 'EGG BIRYANI', 'Egg'),
    ('7134', 'BOILED EGG (2 NOS)', 'Egg'),
    ('7133', 'EGG MASALA', 'Egg'),
    ('7132', 'EGG OMLETTE', 'Egg'),
    ('7131', 'EGG BURJI', 'Egg'),
    ('7130', 'EGG PAKODA', 'Egg'),
    ('7129', 'EGG MANCHURIAN', 'Egg'),
    ('7128', 'EGG CHILLY', 'Egg'),
]

with connection.cursor() as cursor:
    
    # Insert or update in IN_Menu_Items
    for icode, iname, category in items_to_add:
        cursor.execute("SELECT COUNT(*) FROM VANGROTIPARKDB.dbo.IN_Menu_Items WHERE ICode = %s AND IName = %s", [icode, iname])
        if cursor.fetchone()[0] == 0:
            # Check if ICode exists with different name
            cursor.execute("SELECT COUNT(*) FROM VANGROTIPARKDB.dbo.IN_Menu_Items WHERE ICode = %s", [icode])
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO VANGROTIPARKDB.dbo.IN_Menu_Items (ICode, IName, Category)
                    VALUES (%s, %s, %s)
                """, [icode, iname, category])
                print(f"Added {iname} ({icode}) to POS.")
            else:
                # Update existing
                cursor.execute("""
                    UPDATE VANGROTIPARKDB.dbo.IN_Menu_Items 
                    SET IName = %s, Category = %s 
                    WHERE ICode = %s
                """, [iname, category, icode])
                print(f"Updated ICode {icode} to {iname}.")
        else:
            print(f"{iname} ({icode}) already exists.")

    # Get Egg Inventory Item ID
    cursor.execute("SELECT InventoryItemId FROM BIERSYMPHONYDB.dbo.InventoryItem WHERE ItemName='Egg'")
    egg_row = cursor.fetchone()
    
    if egg_row:
        egg_id = egg_row[0]
        # Add tracking mapping for 2 eggs
        for icode, iname, category in items_to_add:
            cursor.execute("SELECT COUNT(*) FROM BIERSYMPHONYDB.dbo.MenuItemConsumption WHERE MenuItemName = %s AND InventoryItemId = %s", [iname, egg_id])
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO BIERSYMPHONYDB.dbo.MenuItemConsumption (MenuItemName, InventoryItemId, ConsumptionPerQty)
                    VALUES (%s, %s, 2.0)
                """, [iname, egg_id])
                print(f"Tracking mapped: {iname} -> 2 Eggs")
            else:
                print(f"Tracking already mapped for {iname}")
                
    connection.commit()
    print("\nAll items successfully configured!")
