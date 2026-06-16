from django.db import models

class InventoryItem(models.Model):
    InventoryItemId = models.AutoField(primary_key=True, db_column='InventoryItemId')
    ItemName = models.CharField(max_length=200, db_column='ItemName', unique=True)
    Unit = models.CharField(max_length=50, db_column='Unit')
    ReorderLevel = models.DecimalField(max_digits=18, decimal_places=4, db_column='ReorderLevel')
    CurrentCost = models.DecimalField(max_digits=18, decimal_places=2, db_column='CurrentCost', default=0)
    IsActive = models.BooleanField(default=True, db_column='IsActive')
    CreatedAt = models.DateTimeField(auto_now_add=True, db_column='CreatedAt')

    class Meta:
        managed = False
        db_table = 'InventoryItem'

class InventoryDelta(models.Model):
    DeltaId = models.BigAutoField(primary_key=True, db_column='DeltaId')
    SyncRunId = models.BigIntegerField(db_column='SyncRunId')
    BillId = models.BigIntegerField(db_column='BillId')
    ItemName = models.CharField(max_length=200, db_column='ItemName')
    EventType = models.CharField(max_length=50, db_column='EventType')
    OldQty = models.DecimalField(max_digits=18, decimal_places=4, db_column='OldQty')
    NewQty = models.DecimalField(max_digits=18, decimal_places=4, db_column='NewQty')
    QtyDifference = models.DecimalField(max_digits=18, decimal_places=4, db_column='QtyDifference')
    EventTime = models.DateTimeField(db_column='EventTime')
    Processed = models.BooleanField(default=False, db_column='Processed')

    class Meta:
        managed = False
        db_table = 'InventoryDelta'

class InventoryTransaction(models.Model):
    TransactionId = models.BigAutoField(primary_key=True, db_column='TransactionId')
    InventoryItemId = models.IntegerField(db_column='InventoryItemId')
    TransactionType = models.CharField(max_length=50, db_column='TransactionType')
    Quantity = models.DecimalField(max_digits=18, decimal_places=4, db_column='Quantity')
    ReferenceType = models.CharField(max_length=100, db_column='ReferenceType')
    ReferenceId = models.BigIntegerField(db_column='ReferenceId', null=True, blank=True)
    TransactionDate = models.DateTimeField(db_column='TransactionDate')

    class Meta:
        managed = False
        db_table = 'InventoryTransaction'

class Purchase(models.Model):
    PurchaseId = models.BigAutoField(primary_key=True, db_column='PurchaseId')
    SupplierName = models.CharField(max_length=200, db_column='SupplierName')
    InvoiceNumber = models.CharField(max_length=100, db_column='InvoiceNumber')
    PurchaseDate = models.DateTimeField(db_column='PurchaseDate')
    TotalAmount = models.DecimalField(max_digits=18, decimal_places=2, db_column='TotalAmount')
    CreatedAt = models.DateTimeField(auto_now_add=True, db_column='CreatedAt')

    class Meta:
        managed = False
        db_table = 'Purchase'

class PurchaseItem(models.Model):
    PurchaseItemId = models.BigAutoField(primary_key=True, db_column='PurchaseItemId')
    PurchaseId = models.BigIntegerField(db_column='PurchaseId')
    InventoryItemId = models.IntegerField(db_column='InventoryItemId')
    Quantity = models.DecimalField(max_digits=18, decimal_places=4, db_column='Quantity')
    UnitPrice = models.DecimalField(max_digits=18, decimal_places=2, db_column='UnitPrice')
    TotalPrice = models.DecimalField(max_digits=18, decimal_places=2, db_column='TotalPrice')

    class Meta:
        managed = False
        db_table = 'PurchaseItem'

class MenuItemConsumption(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id')
    MenuItemName = models.CharField(max_length=200, db_column='MenuItemName')
    InventoryItemId = models.IntegerField(db_column='InventoryItemId')
    ConsumptionPerQty = models.DecimalField(max_digits=18, decimal_places=4, db_column='ConsumptionPerQty')

    class Meta:
        managed = False
        db_table = 'MenuItemConsumption'

class SyncLog(models.Model):
    Id = models.BigAutoField(primary_key=True, db_column='Id')
    SyncStarted = models.DateTimeField(db_column='SyncStarted')
    SyncEnded = models.DateTimeField(db_column='SyncEnded', null=True, blank=True)
    RecordsRead = models.IntegerField(db_column='RecordsRead', default=0)
    Success = models.BooleanField(db_column='Success', default=False)
    ErrorMessage = models.TextField(db_column='ErrorMessage', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'SyncLog'

class SyncSnapshot(models.Model):
    BillId = models.BigIntegerField(db_column='BillId', primary_key=True) 
    ItemName = models.CharField(max_length=200, db_column='ItemName')
    Qty = models.DecimalField(max_digits=18, decimal_places=4, db_column='Qty')

    class Meta:
        managed = False
        db_table = 'SyncSnapshot'
