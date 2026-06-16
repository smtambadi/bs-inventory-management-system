import subprocess
import os
from django.db import transaction
from django.db.models import Sum
from .models import *
from django.utils import timezone

SYNC_ENGINE_DIR = r'd:\BS\sync_engine'

class SyncService:
    @staticmethod
    def run_sync():
        result = subprocess.run(['python', 'sync.py'], cwd=SYNC_ENGINE_DIR, capture_output=True, text=True)
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }

    @staticmethod
    def process_deltas():
        result = subprocess.run(['python', 'process_deltas.py'], cwd=SYNC_ENGINE_DIR, capture_output=True, text=True)
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }

class StockService:
    @staticmethod
    def get_current_stock():
        items = InventoryItem.objects.filter(IsActive=True)
        stock_data = []
        for item in items:
            stock = InventoryTransaction.objects.filter(InventoryItemId=item.InventoryItemId).aggregate(Sum('Quantity'))['Quantity__sum'] or 0
            stock_data.append({
                'id': item.InventoryItemId,
                'name': item.ItemName,
                'unit': item.Unit,
                'reorder_level': item.ReorderLevel,
                'current_stock': stock,
                'status': 'LOW' if stock <= item.ReorderLevel else 'OK'
            })
        return stock_data

class PurchaseService:
    @staticmethod
    def create_purchase(supplier_name, invoice_number, purchase_date, items):
        with transaction.atomic():
            total_amount = sum(float(item['quantity']) * float(item['unit_price']) for item in items)
            purchase = Purchase.objects.create(
                SupplierName=supplier_name,
                InvoiceNumber=invoice_number,
                PurchaseDate=purchase_date,
                TotalAmount=total_amount
            )
            for item in items:
                qty = float(item['quantity'])
                price = float(item['unit_price'])
                total = qty * price
                PurchaseItem.objects.create(
                    PurchaseId=purchase.PurchaseId,
                    InventoryItemId=item['id'],
                    Quantity=qty,
                    UnitPrice=price,
                    TotalPrice=total
                )
                InventoryTransaction.objects.create(
                    InventoryItemId=item['id'],
                    TransactionType='PURCHASE',
                    Quantity=qty,
                    ReferenceType='Purchase',
                    ReferenceId=purchase.PurchaseId,
                    TransactionDate=purchase_date
                )
            return purchase

    @staticmethod
    def get_purchase_details(purchase_id):
        purchase = Purchase.objects.get(PurchaseId=purchase_id)
        items = PurchaseItem.objects.filter(PurchaseId=purchase_id)
        
        items_data = []
        for item in items:
            inv_item = InventoryItem.objects.get(InventoryItemId=item.InventoryItemId)
            items_data.append({
                'id': item.PurchaseItemId,
                'inventory_item_id': item.InventoryItemId,
                'item_name': inv_item.ItemName,
                'quantity': item.Quantity,
                'unit_price': item.UnitPrice,
                'total_price': item.TotalPrice
            })
            
        return {
            'purchase_id': purchase.PurchaseId,
            'supplier': purchase.SupplierName,
            'invoice': purchase.InvoiceNumber,
            'date': purchase.PurchaseDate,
            'total_amount': purchase.TotalAmount,
            'items': items_data
        }

    @staticmethod
    def delete_purchase(purchase_id):
        with transaction.atomic():
            purchase = Purchase.objects.get(PurchaseId=purchase_id)
            InventoryTransaction.objects.filter(ReferenceType='Purchase', ReferenceId=purchase_id).delete()
            PurchaseItem.objects.filter(PurchaseId=purchase_id).delete()
            purchase.delete()
            return True

    @staticmethod
    def add_purchase_item(purchase_id, inventory_item_id, quantity, unit_price):
        with transaction.atomic():
            from decimal import Decimal
            purchase = Purchase.objects.get(PurchaseId=purchase_id)
            
            qty_d = Decimal(str(quantity))
            price_d = Decimal(str(unit_price))
            total = qty_d * price_d
            
            PurchaseItem.objects.create(
                PurchaseId=purchase.PurchaseId,
                InventoryItemId=inventory_item_id,
                Quantity=qty_d,
                UnitPrice=price_d,
                TotalPrice=total
            )
            
            purchase.TotalAmount = purchase.TotalAmount + total
            purchase.save()
            
            InventoryTransaction.objects.create(
                InventoryItemId=inventory_item_id,
                TransactionType='PURCHASE',
                Quantity=qty_d,
                ReferenceType='Purchase',
                ReferenceId=purchase.PurchaseId,
                TransactionDate=purchase.PurchaseDate
            )
            return True

    @staticmethod
    def update_purchase_item(item_id, new_qty, new_price):
        with transaction.atomic():
            from decimal import Decimal
            item = PurchaseItem.objects.get(PurchaseItemId=item_id)
            purchase = Purchase.objects.get(PurchaseId=item.PurchaseId)
            
            old_qty = item.Quantity
            old_total = item.TotalPrice
            
            new_qty_d = Decimal(str(new_qty))
            new_price_d = Decimal(str(new_price))
            new_total = new_qty_d * new_price_d
            
            # Update PurchaseItem
            item.Quantity = new_qty_d
            item.UnitPrice = new_price_d
            item.TotalPrice = new_total
            item.save()
            
            # Update Purchase total amount
            purchase.TotalAmount = purchase.TotalAmount - old_total + new_total
            purchase.save()
            
            # Update InventoryTransaction
            # Because multiple items could have same inventory ID, we match by exact quantity.
            # A better way is to delete old transaction and create new one, or just update it.
            # But we didn't store PurchaseItemId in InventoryTransaction.
            # To be safe, we'll try to find one matching transaction on that date for that purchase.
            inv_trans = InventoryTransaction.objects.filter(
                ReferenceType='Purchase',
                ReferenceId=purchase.PurchaseId,
                InventoryItemId=item.InventoryItemId,
                Quantity=old_qty
            ).first()
            if inv_trans:
                inv_trans.Quantity = new_qty_d
                inv_trans.save()
            else:
                # Fallback: create a new one for the difference
                InventoryTransaction.objects.create(
                    InventoryItemId=item.InventoryItemId,
                    TransactionType='PURCHASE_ADJUSTMENT',
                    Quantity=new_qty_d - old_qty,
                    ReferenceType='Purchase',
                    ReferenceId=purchase.PurchaseId,
                    TransactionDate=timezone.now()
                )
            return True

    @staticmethod
    def delete_purchase_item(item_id):
        with transaction.atomic():
            item = PurchaseItem.objects.get(PurchaseItemId=item_id)
            purchase = Purchase.objects.get(PurchaseId=item.PurchaseId)
            
            # Reduce Purchase total amount
            purchase.TotalAmount = purchase.TotalAmount - item.TotalPrice
            purchase.save()
            
            # Find and delete InventoryTransaction
            inv_trans = InventoryTransaction.objects.filter(
                ReferenceType='Purchase',
                ReferenceId=purchase.PurchaseId,
                InventoryItemId=item.InventoryItemId,
                Quantity=item.Quantity
            ).first()
            if inv_trans:
                inv_trans.delete()
            else:
                # Fallback: create negative adjustment
                InventoryTransaction.objects.create(
                    InventoryItemId=item.InventoryItemId,
                    TransactionType='PURCHASE_ADJUSTMENT',
                    Quantity=-item.Quantity,
                    ReferenceType='Purchase',
                    ReferenceId=purchase.PurchaseId,
                    TransactionDate=timezone.now()
                )
                
            item.delete()
            return True


class ReportService:
    @staticmethod
    def run_report(report_name, from_date=None, to_date=None):
        import subprocess
        import json
        
        cmd = ['python', 'reports.py', '--report', report_name]
        
        # We can just call the CLI but wait, the CLI formats as a table.
        # Instead, I'll just write simple raw SQL queries here to return JSON.
        from django.db import connection
        
        with connection.cursor() as cursor:
            if report_name == 'stock':
                cursor.execute("""
                    SELECT i.ItemName, i.Unit, 
                           ISNULL(SUM(t.Quantity), 0) AS CurrentStock,
                           i.ReorderLevel
                    FROM dbo.InventoryItem i
                    LEFT JOIN dbo.InventoryTransaction t ON i.InventoryItemId = t.InventoryItemId
                    WHERE i.IsActive = 1
                    GROUP BY i.InventoryItemId, i.ItemName, i.Unit, i.ReorderLevel
                """)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
            elif report_name == 'purchases':
                cursor.execute("""
                    SELECT p.PurchaseDate, p.SupplierName, p.InvoiceNumber,
                           i.ItemName, pi.Quantity, i.Unit, pi.UnitPrice, pi.TotalPrice
                    FROM dbo.Purchase p
                    JOIN dbo.PurchaseItem pi ON p.PurchaseId = pi.PurchaseId
                    JOIN dbo.InventoryItem i ON pi.InventoryItemId = i.InventoryItemId
                    ORDER BY p.PurchaseDate DESC, p.PurchaseId
                """)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
            elif report_name == 'consumption':
                query = """
                    SELECT CAST(t.TransactionDate AS DATE) AS Date,
                           i.ItemName, i.Unit,
                           SUM(ABS(t.Quantity)) AS ConsumedQty
                    FROM dbo.InventoryTransaction t
                    JOIN dbo.InventoryItem i ON t.InventoryItemId = i.InventoryItemId
                    WHERE t.TransactionType = 'SALE' AND t.Quantity < 0
                """
                params = []
                if from_date:
                    query += " AND CAST(t.TransactionDate AS DATE) >= %s"
                    params.append(from_date)
                if to_date:
                    query += " AND CAST(t.TransactionDate AS DATE) <= %s"
                    params.append(to_date)
                    
                query += """
                    GROUP BY CAST(t.TransactionDate AS DATE), i.ItemName, i.Unit
                    ORDER BY Date DESC, ConsumedQty DESC
                """
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

            elif report_name == 'sales-collection':
                query = """
                    SELECT CAST(B.Trdate AS DATE) AS Date,
                           MI.Category,
                           MI.IName AS MenuItem,
                           KT.SaleRate AS PricePerItem,
                           SUM(KT.SaleQty) AS TotalQtySold,
                           SUM(KT.SaleQty * KT.SaleRate) AS TotalCollection
                    FROM VANGROTIPARKDB.dbo.POS_Tab_KOTBill B
                    INNER JOIN VANGROTIPARKDB.dbo.POS_Tab_KOTBill_Details BD
                        ON B.BillId = BD.BillId
                    INNER JOIN VANGROTIPARKDB.dbo.POS_TAB_KOTTRANSACTIONDATA KT
                        ON BD.KtNo = KT.KTNo
                    INNER JOIN (
                        SELECT ICode, IName, MIN(Category) AS Category
                        FROM VANGROTIPARKDB.dbo.IN_Menu_Items
                        GROUP BY ICode, IName
                    ) MI
                        ON KT.ICode = MI.ICode
                    WHERE B.BillSettled = 1
                """
                params = []
                if from_date:
                    query += " AND CAST(B.Trdate AS DATE) >= %s"
                    params.append(from_date)
                if to_date:
                    query += " AND CAST(B.Trdate AS DATE) <= %s"
                    params.append(to_date)
                    
                query += """
                    GROUP BY CAST(B.Trdate AS DATE), MI.Category, MI.IName, KT.SaleRate
                    ORDER BY Date DESC, MI.Category, TotalCollection DESC
                """
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

                
            elif report_name == 'sales-vs-usage':
                cursor.execute("""
                    SELECT d.ItemName AS MenuItemSold,
                           SUM(CASE WHEN d.EventType IN ('NEW','INCREASED') THEN d.QtyDifference ELSE 0 END) AS QtySold,
                           SUM(CASE WHEN d.EventType IN ('REDUCED','REMOVED') THEN ABS(d.QtyDifference) ELSE 0 END) AS QtyReturned
                    FROM dbo.InventoryDelta d
                    GROUP BY d.ItemName
                    ORDER BY QtySold DESC
                """)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        return []
