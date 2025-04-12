# inventory/urls.py
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),
    
    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('products/<int:pk>/calculate-eoq/', views.calculate_eoq, name='calculate-eoq'),
    path('products/<int:pk>/demand-chart/', views.product_demand_chart, name='product-demand-chart'),
    
    # Inventory URLs
    path('inventory/', views.InventoryListView.as_view(), name='inventory-list'),
    path('inventory/create/', views.InventoryCreateView.as_view(), name='inventory-create'),
    path('inventory/<int:pk>/update/', views.InventoryUpdateView.as_view(), name='inventory-update'),
    
    # Transaction URLs
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction-create'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
]