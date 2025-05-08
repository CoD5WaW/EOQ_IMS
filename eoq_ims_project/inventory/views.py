# inventory/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Category, Product, ProductImage, Inventory, InventoryTransaction
from .forms import (CategoryForm, ProductForm, ProductImageInlineFormSet, 
                   InventoryForm, InventoryTransactionForm)

import math
from decimal import Decimal

# Category Views
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    
class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'inventory/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.all()
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully.')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully.')
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('inventory:category-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Product Views
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        active_only = self.request.GET.get('active')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if active_only == 'true':
            queryset = queryset.filter(active=True)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get inventory levels across all warehouses
        context['inventories'] = self.object.inventories.all()
        # Get recent transactions
        context['transactions'] = InventoryTransaction.objects.filter(
            product=self.object
        ).order_by('-transaction_date')[:10]
        # Get product images
        context['images'] = self.object.additional_images.all()
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully.')
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('inventory:product-detail', kwargs={'pk': self.object.pk})

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Product Image Views
class ProductImageDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductImage
    template_name = 'inventory/product_image_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('inventory:product-update', kwargs={'pk': self.object.product.pk})
    
    def delete(self, request, *args, **kwargs):
        product_id = self.get_object().product.pk
        messages.success(request, 'Product image deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Inventory Views
class InventoryListView(LoginRequiredMixin, ListView):
    model = Inventory
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'inventories'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset()
        warehouse_id = self.request.GET.get('warehouse')
        
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
            
        return queryset.select_related('product', 'warehouse')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from warehouse.models import Warehouse
        context['warehouses'] = Warehouse.objects.filter(active=True)
        
        # Identify low stock items
        for inventory in context['inventories']:
            if inventory.quantity_on_hand <= inventory.product.reorder_point:
                inventory.low_stock = True
            else:
                inventory.low_stock = False
                
        return context

class InventoryCreateView(LoginRequiredMixin, CreateView):
    model = Inventory
    form_class = InventoryForm
    template_name = 'inventory/inventory_form.html'
    success_url = reverse_lazy('inventory:inventory-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Inventory record created successfully.')
        return super().form_valid(form)

class InventoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Inventory
    form_class = InventoryForm
    template_name = 'inventory/inventory_form.html'
    success_url = reverse_lazy('inventory:inventory-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Inventory record updated successfully.')
        return super().form_valid(form)

# Transaction Views
class TransactionListView(LoginRequiredMixin, ListView):
    model = InventoryTransaction
    template_name = 'inventory/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.GET.get('product')
        warehouse_id = self.request.GET.get('warehouse')
        transaction_type = self.request.GET.get('type')
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
            
        return queryset.select_related('product', 'warehouse').order_by('-transaction_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(active=True)
        from warehouse.models import Warehouse
        context['warehouses'] = Warehouse.objects.filter(active=True)
        context['transaction_types'] = dict(InventoryTransaction.TRANSACTION_TYPES)
        return context

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = InventoryTransaction
    form_class = InventoryTransactionForm
    template_name = 'inventory/transaction_form.html'
    success_url = reverse_lazy('inventory:transaction-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Transaction created successfully and inventory updated.')
        return response

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = InventoryTransaction
    template_name = 'inventory/transaction_detail.html'
    context_object_name = 'transaction'

@login_required
def calculate_eoq(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    try:
        from analytics.models import EOQParameters
        params = EOQParameters.objects.get(product=product)
        eoq = params.calculate_eoq()
        
        messages.success(request, f'EOQ calculated: {eoq:.2f} units')
    except EOQParameters.DoesNotExist:
        messages.error(request, 'EOQ parameters not found for this product')
    except Exception as e:
        messages.error(request, f'Error calculating EOQ: {str(e)}')
    
    return redirect('inventory:product-detail', pk=pk)

@login_required
def product_demand_chart(request, pk):
    """API endpoint to get chart data for product demand history"""
    product = get_object_or_404(Product, pk=pk)
    
    try:
        from analytics.models import DemandHistory
        
        # Get the last 12 months of demand data
        demand_data = DemandHistory.objects.filter(
            product=product, 
            demand_type='actual'
        ).order_by('period_date')[:12]
        
        data = {
            'labels': [item.period_date.strftime('%b %Y') for item in demand_data],
            'actual': [item.quantity_demanded for item in demand_data],
        }
        
        # Include forecast if available
        forecast_data = DemandHistory.objects.filter(
            product=product,
            demand_type='forecast'
        ).order_by('period_date')[:12]
        
        if forecast_data:
            data['forecast'] = [item.quantity_demanded for item in forecast_data]
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})