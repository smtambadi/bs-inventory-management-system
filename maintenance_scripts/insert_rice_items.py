import os
import sys
import django

sys.path.append(r'd:\BS\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

safe_items = [
    ('7204', 'DAL KHICHDI', 'Rice'),
    ('7196', 'VEG BIRYANI', 'Rice'),
    ('7160', 'EGG BIRYANI', 'Rice'),
]

with connection.cursor() as cursor:
    # 1. Insert into POS Database
    for icode, iname, category in safe_items:
        cursor.execute("SELECT COUNT(*) FROM VANGROTIPARKDB.dbo.IN_Menu_Items WHERE IName = %s", [iname])
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO VANGROTIPARKDB.dbo.IN_Menu_Items (ICode, IName, Category)
                VALUES (%s, %s, %s)
            """, [icode, iname, category])
            print(f"Added {iname} to POS Menu.")
        else:
            print(f"{iname} already exists in POS Menu.")

    # 2. Add to Tracking System (Deducting Rice)
    cursor.execute("SELECT InventoryItemId FROM BIERSYMPHONYDB.dbo.InventoryItem WHERE ItemName = 'Rice'")
    rice_id_row = cursor.fetchone()
    if rice_id_row:
        rice_id = rice_id_row[0]
        for icode, iname, category in safe_items:
            cursor.execute("SELECT COUNT(*) FROM BIERSYMPHONYDB.dbo.MenuItemConsumption WHERE MenuItemName = %s AND InventoryItemId = %s", [iname, rice_id])
            if cursor.fetchone()[0] == 0:
                # Deducting 0.11 KG of Rice by default for these dishes
                cursor.execute("""
                    INSERT INTO BIERSYMPHONYDB.dbo.MenuItemConsumption (MenuItemName, InventoryItemId, ConsumptionPerQty)
                    VALUES (%s, %s, 0.11)
                """, [iname, rice_id])
                print(f"Tracking enabled for {iname} (0.11 KG Rice/Unit).")
            else:
                print(f"Tracking already enabled for {iname}.")

    connection.commit()
    print("Safe items processed!")
