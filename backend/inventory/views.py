from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import *
from .serializers import SyncLogSerializer
from .services import SyncService, StockService, PurchaseService, ReportService

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        stock_data = StockService.get_current_stock()
        
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        
        date_filter = ""
        params = []
        if start_date or end_date:
            if start_date:
                date_filter += " AND CAST(B.Trdate AS DATE) >= %s"
                params.append(start_date)
            if end_date:
                date_filter += " AND CAST(B.Trdate AS DATE) <= %s"
                params.append(end_date)
        else:
            # Default to today
            date_filter = " AND CAST(B.Trdate AS DATE) = CAST(GETDATE() AS DATE)"
            
        from django.db import connection
        with connection.cursor() as cursor:
            query = f"""
                SELECT 
                    UPPER(II.ItemName) AS category,
                    MI.IName AS name,
                    SUM(KT.SaleQty) AS total_qty,
                    SUM(KT.SaleQty * KT.SaleRate) AS total_amount
                FROM VANGROTIPARKDB.dbo.POS_Tab_KOTBill B
                INNER JOIN VANGROTIPARKDB.dbo.POS_Tab_KOTBill_Details BD ON B.BillId = BD.BillId
                INNER JOIN VANGROTIPARKDB.dbo.POS_TAB_KOTTRANSACTIONDATA KT ON BD.KtNo = KT.KTNo
                INNER JOIN (
                    SELECT ICode, IName
                    FROM VANGROTIPARKDB.dbo.IN_Menu_Items
                    GROUP BY ICode, IName
                ) MI ON KT.ICode = MI.ICode
                INNER JOIN BIERSYMPHONYDB.dbo.MenuItemConsumption MC ON MI.IName COLLATE DATABASE_DEFAULT = MC.MenuItemName COLLATE DATABASE_DEFAULT
                INNER JOIN BIERSYMPHONYDB.dbo.InventoryItem II ON MC.InventoryItemId = II.InventoryItemId
                WHERE B.BillSettled = 1 
                  {date_filter}
                  AND UPPER(II.ItemName) IN ('CHICKEN', 'MUTTON', 'BOTI', 'RICE', 'EGG')
                GROUP BY 
                    UPPER(II.ItemName),
                    MI.IName
                ORDER BY total_amount DESC
            """
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            item_sales = [dict(zip(columns, row)) for row in cursor.fetchall()]

            consumption_query = f"""
                SELECT 
                    I.ItemName AS ingredient_name,
                    SUM(KT.SaleQty * MC.ConsumptionPerQty) AS consumed_qty,
                    I.Unit
                FROM VANGROTIPARKDB.dbo.POS_Tab_KOTBill B
                INNER JOIN VANGROTIPARKDB.dbo.POS_Tab_KOTBill_Details BD ON B.BillId = BD.BillId
                INNER JOIN VANGROTIPARKDB.dbo.POS_TAB_KOTTRANSACTIONDATA KT ON BD.KtNo = KT.KTNo
                INNER JOIN (
                    SELECT ICode, IName
                    FROM VANGROTIPARKDB.dbo.IN_Menu_Items
                    GROUP BY ICode, IName
                ) MI ON KT.ICode = MI.ICode
                INNER JOIN BIERSYMPHONYDB.dbo.MenuItemConsumption MC ON MI.IName COLLATE DATABASE_DEFAULT = MC.MenuItemName COLLATE DATABASE_DEFAULT
                INNER JOIN BIERSYMPHONYDB.dbo.InventoryItem I ON MC.InventoryItemId = I.InventoryItemId
                WHERE B.BillSettled = 1 
                  {date_filter}
                GROUP BY I.ItemName, I.Unit
            """
            cursor.execute(consumption_query, params)
            c_columns = [col[0] for col in cursor.description]
            consumption_data = [dict(zip(c_columns, row)) for row in cursor.fetchall()]

        return Response({
            'stock': stock_data,
            'item_sales': item_sales,
            'consumption': consumption_data
        })

class InventoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        items = InventoryItem.objects.all()
        from .serializers import InventoryItemSerializer
        return Response(InventoryItemSerializer(items, many=True).data)

class SyncRunView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        return Response(SyncService.run_sync())

class SyncProcessView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        return Response(SyncService.process_deltas())

class PurchaseView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        purchases = Purchase.objects.order_by('-PurchaseDate')[:50]
        from .serializers import PurchaseSerializer
        return Response(PurchaseSerializer(purchases, many=True).data)

    def post(self, request):
        data = request.data
        try:
            purchase = PurchaseService.create_purchase(
                data['supplier_name'],
                data['invoice_number'],
                data['purchase_date'],
                data['items']
            )
            return Response({'message': 'Purchase recorded', 'id': purchase.PurchaseId})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PurchaseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, purchase_id):
        # Anyone can view details
        try:
            details = PurchaseService.get_purchase_details(purchase_id)
            return Response(details)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, purchase_id):
        if not request.user.is_staff:
            return Response({'error': 'Admin privileges required'}, status=status.HTTP_403_FORBIDDEN)
        try:
            PurchaseService.add_purchase_item(
                purchase_id,
                request.data['inventory_item_id'],
                request.data['quantity'],
                request.data['unit_price']
            )
            return Response({'message': 'Item added successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, purchase_id):
        # Only admin can delete entire purchase
        if not request.user.is_staff:
            return Response({'error': 'Admin privileges required'}, status=status.HTTP_403_FORBIDDEN)
        try:
            PurchaseService.delete_purchase(purchase_id)
            return Response({'message': 'Purchase deleted successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PurchaseItemDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, item_id):
        try:
            PurchaseService.update_purchase_item(
                item_id, 
                request.data['quantity'], 
                request.data['unit_price']
            )
            return Response({'message': 'Item updated successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, item_id):
        try:
            PurchaseService.delete_purchase_item(item_id)
            return Response({'message': 'Item deleted successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReportView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, report_name):
        from_date = request.GET.get('start')
        to_date = request.GET.get('end')
        data = ReportService.run_report(report_name, from_date, to_date)
        return Response(data)
