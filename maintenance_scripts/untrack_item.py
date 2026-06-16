import os
import sys
import django
import argparse

sys.path.append(r'd:\BS\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def untrack_item(item_name):
    # Ensure item_name matches exactly (case-insensitive for SQL Server but good practice)
    item_name = item_name.strip().upper()
    
    query = """
        DELETE FROM BIERSYMPHONYDB.dbo.MenuItemConsumption
        WHERE UPPER(MenuItemName) = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM BIERSYMPHONYDB.dbo.MenuItemConsumption WHERE UPPER(MenuItemName) = %s", [item_name])
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"Item '{item_name}' is not currently being tracked. No action taken.")
            return

        cursor.execute(query, [item_name])
        connection.commit()
        print(f"Successfully untracked '{item_name}'. It will no longer reduce inventory when sold.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Untrack a menu item so it stops consuming inventory.")
    parser.add_argument("item_name", type=str, help="The exact name of the POS menu item (e.g. 'CHICKEN LOLLIPOP')")
    
    args = parser.parse_args()
    untrack_item(args.item_name)
