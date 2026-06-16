import os
import sys
import django

sys.path.append(r'd:\BS\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

items_to_add = [
    ('7185', 'KASTOORI KEBAB', 'Chicken'),
    ('7182', 'TANDOORI KEBAB', 'Chicken'),
    ('7182', 'HARIYALI KEBAB', 'Chicken'),
]

with connection.cursor() as cursor:
    # 1. Insert into POS Database
    for icode, iname, category in items_to_add:
        # Check if it already exists to avoid true duplicates
        cursor.execute("SELECT COUNT(*) FROM VANGROTIPARKDB.dbo.IN_Menu_Items WHERE IName = %s", [iname])
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO VANGROTIPARKDB.dbo.IN_Menu_Items (ICode, IName, Category)
                VALUES (%s, %s, %s)
            """, [icode, iname, category])
            print(f"Added {iname} to POS Menu.")
        else:
            print(f"{iname} already exists in POS Menu.")

    # 2. Add to Tracking System
    cursor.execute("SELECT InventoryItemId FROM BIERSYMPHONYDB.dbo.InventoryItem WHERE ItemName = 'Chicken'")
    chicken_id_row = cursor.fetchone()
    if chicken_id_row:
        chicken_id = chicken_id_row[0]
        
        for icode, iname, category in items_to_add:
            cursor.execute("SELECT COUNT(*) FROM BIERSYMPHONYDB.dbo.MenuItemConsumption WHERE MenuItemName = %s", [iname])
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO BIERSYMPHONYDB.dbo.MenuItemConsumption (MenuItemName, InventoryItemId, ConsumptionPerQty)
                    VALUES (%s, %s, 0.25)
                """, [iname, chicken_id])
                print(f"Tracking enabled for {iname} (0.25 KG Chicken/Unit).")
            else:
                print(f"Tracking already enabled for {iname}.")

    connection.commit()
    print("Done!")
