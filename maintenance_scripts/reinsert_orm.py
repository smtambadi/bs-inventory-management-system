import os
import sys
import django
from django.utils import timezone

sys.path.append(r'd:\BS\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from inventory.models import InventoryItem, InventoryTransaction

chicken = InventoryItem.objects.get(ItemName='Chicken')
mutton = InventoryItem.objects.get(ItemName='Mutton')
rice = InventoryItem.objects.get(ItemName='Rice')

now = timezone.now()

InventoryTransaction.objects.create(InventoryItemId=chicken.InventoryItemId, TransactionType='PURCHASE', Quantity=5.00, ReferenceType='Purchase', TransactionDate=now)
InventoryTransaction.objects.create(InventoryItemId=mutton.InventoryItemId, TransactionType='PURCHASE', Quantity=2.00, ReferenceType='Purchase', TransactionDate=now)
InventoryTransaction.objects.create(InventoryItemId=rice.InventoryItemId, TransactionType='PURCHASE', Quantity=2.00, ReferenceType='Purchase', TransactionDate=now)

print("Created 5KG Chicken, 2KG Mutton, 2KG Rice purchases.")
