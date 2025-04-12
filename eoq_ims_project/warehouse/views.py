# warehouse/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Warehouse
from .forms import WarehouseForm

def warehouse_list(request):
    """Display a list of all warehouses"""
    warehouses = Warehouse.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        warehouses = warehouses.filter(warehouse_name__icontains=search_query)
    
    # Pagination
    paginator = Paginator(warehouses, 10)  # Show 10 warehouses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'warehouse/warehouse_list.html', context)

def warehouse_detail(request, pk):
    """Display details for a specific warehouse"""
    warehouse = get_object_or_404(Warehouse, pk=pk)
    
    # Get the inventory items for this warehouse
    inventory_items = warehouse.inventories.select_related('product').all()
    
    context = {
        'warehouse': warehouse,
        'inventory_items': inventory_items,
    }
    return render(request, 'warehouse/warehouse_detail.html', context)

def warehouse_create(request):
    """Create a new warehouse"""
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, f'Warehouse "{warehouse.warehouse_name}" created successfully.')
            return redirect('warehouse_detail', pk=warehouse.pk)
    else:
        form = WarehouseForm()
    
    context = {
        'form': form,
        'title': 'Add Warehouse',
    }
    return render(request, 'warehouse/warehouse_form.html', context)

def warehouse_update(request, pk):
    """Update an existing warehouse"""
    warehouse = get_object_or_404(Warehouse, pk=pk)
    
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, f'Warehouse "{warehouse.warehouse_name}" updated successfully.')
            return redirect('warehouse_detail', pk=warehouse.pk)
    else:
        form = WarehouseForm(instance=warehouse)
    
    context = {
        'form': form,
        'warehouse': warehouse,
        'title': 'Edit Warehouse',
    }
    return render(request, 'warehouse/warehouse_form.html', context)

def warehouse_delete(request, pk):
    """Delete a warehouse"""
    warehouse = get_object_or_404(Warehouse, pk=pk)
    
    if request.method == 'POST':
        warehouse_name = warehouse.warehouse_name
        warehouse.delete()
        messages.success(request, f'Warehouse "{warehouse_name}" deleted successfully.')
        return redirect('warehouse_list')
    
    context = {
        'warehouse': warehouse,
    }
    return render(request, 'warehouse/warehouse_confirm_delete.html', context)