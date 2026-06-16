from django.urls import path
from .views import DashboardView, InventoryView, SyncRunView, SyncProcessView, PurchaseView, PurchaseDetailView, PurchaseItemDetailView, ReportView
from .auth_views import LoginView, UserManagementView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('users/', UserManagementView.as_view()),
    path('users/<int:user_id>/', UserManagementView.as_view()),
    path('dashboard/', DashboardView.as_view()),
    path('inventory/', InventoryView.as_view()),
    path('sync/run/', SyncRunView.as_view()),
    path('sync/process/', SyncProcessView.as_view()),
    path('purchases/', PurchaseView.as_view()),
    path('purchases/<int:purchase_id>/', PurchaseDetailView.as_view()),
    path('purchase-items/<int:item_id>/', PurchaseItemDetailView.as_view()),
    path('reports/<str:report_name>/', ReportView.as_view()),
]
