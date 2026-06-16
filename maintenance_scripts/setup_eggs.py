import os
import sys
import django

sys.path.append(r'd:\BS\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from inventory.models import InventoryItem, MenuItemConsumption

# 1. Create Egg Inventory Item
egg, created = InventoryItem.objects.get_or_create(
    ItemName='Egg',
    defaults={'Unit': "No's", 'ReorderLevel': 50, 'CurrentCost': 5.0}
)
if not created:
    egg.Unit = "No's"
    egg.save()
print(f"Egg inventory item ready with Unit: {egg.Unit}")

# 2. Get all egg items from POS
egg_items = []
with connection.cursor() as cursor:
    cursor.execute("SELECT IName FROM VANGROTIPARKDB.dbo.IN_Menu_Items WHERE Category LIKE '%EGG%' OR IName LIKE '%EGG%'")
    for row in cursor.fetchall():
        egg_items.append(row[0])

# 3. Add to Tracking System
for item_name in egg_items:
    consumption, c_created = MenuItemConsumption.objects.get_or_create(
        MenuItemName=item_name,
        InventoryItemId=egg.InventoryItemId,
        defaults={'ConsumptionPerQty': 2.0}
    )
    if not c_created:
        consumption.ConsumptionPerQty = 2.0
        consumption.save()
    print(f"Tracking enabled: {item_name} -> 2 Eggs")

print("Egg setup completed!")
