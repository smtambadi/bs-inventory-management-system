import os
import sys
import django
from datetime import datetime

sys.path.append(r'd:\BS\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from inventory.models import InventoryItem, InventoryTransaction

egg = InventoryItem.objects.get(ItemName='Egg')

InventoryTransaction.objects.create(
    InventoryItemId=egg.InventoryItemId,
    TransactionType='PURCHASE',
    Quantity=300.0,
    ReferenceType='PurchaseOrder',
    ReferenceId=10,
    TransactionDate='2026-06-15 08:00:00'
)

print("Inserted 300 Egg Purchase.")
