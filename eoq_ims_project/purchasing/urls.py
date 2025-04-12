# purchasing/urls.py
from django.urls import path
from . import views

app_name = 'purchasing'

urlpatterns = [
    # Supplier URLs
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:supplier_id>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:supplier_id>/edit/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<int:supplier_id>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    
    # Purchase Order URLs
    path('purchase-orders/', views.PurchaseOrderListView.as_view(), name='po_list'),
    path('purchase-orders/add/', views.PurchaseOrderCreateView.as_view(), name='po_create'),
    path('purchase-orders/<int:po_id>/', views.PurchaseOrderDetailView.as_view(), name='po_detail'),
    path('purchase-orders/<int:po_id>/edit/', views.PurchaseOrderUpdateView.as_view(), name='po_update'),
    path('purchase-orders/<int:po_id>/delete/', views.PurchaseOrderDeleteView.as_view(), name='po_delete'),
    path('purchase-orders/<int:po_id>/update-status/', views.update_po_status, name='po_update_status'),
]