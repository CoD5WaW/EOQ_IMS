# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import models
from django.urls import reverse

from inventory.models import Product, Inventory, InventoryTransaction
from purchasing.models import PurchaseOrder, Supplier
from warehouse.models import Warehouse
from analytics.models import DemandHistory, EOQParameters


@login_required
def dashboard(request):
    """
    Main dashboard view showing key metrics and recent activity across the entire system.
    Displays inventory statistics, purchasing data, recent transactions, and warehouse info.
    """
    # Get basic inventory statistics
    total_products = Product.objects.filter(active=True).count()
    
    # Calculate total inventory value with proper null handling
    total_inventory_value = Inventory.objects.select_related('product').annotate(
        value=ExpressionWrapper(
            F('quantity_on_hand') * F('product__unit_cost'),
            output_field=DecimalField()
        )
    ).aggregate(total=Sum('value', default=0))['total'] or 0
    
    # Count products with inventory below reorder point
    low_stock_count = Inventory.objects.select_related('product').filter(
        quantity_on_hand__lte=F('product__reorder_point')
    ).count()
    
    # Get purchasing statistics
    pending_orders = PurchaseOrder.objects.filter(
        po_status__in=['pending', 'approved', 'ordered']
    ).count()
    
    # Get most recent purchase orders
    recent_orders = PurchaseOrder.objects.select_related('supplier').order_by('-order_date')[:5]
    
    # Get recent transactions
    recent_transactions = InventoryTransaction.objects.select_related(
        'product', 'warehouse'
    ).order_by('-transaction_date')[:10]
    
    # Calculate activity metrics for the past 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    transactions_30days = InventoryTransaction.objects.filter(
        transaction_date__gte=thirty_days_ago
    ).count()
    
    orders_30days = PurchaseOrder.objects.filter(
        order_date__gte=thirty_days_ago
    ).count()
    
    # Get warehouse statistics with item counts
    warehouses = Warehouse.objects.filter(active=True).annotate(
        item_count=Count('inventories')
    )
    
    context = {
        'total_products': total_products,
        'total_inventory_value': total_inventory_value,
        'low_stock_count': low_stock_count,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
        'recent_transactions': recent_transactions,
        'transactions_30days': transactions_30days,
        'orders_30days': orders_30days,
        'warehouses': warehouses,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def inventory_overview(request):
    """
    Dashboard view for inventory overview.
    Shows inventory by category, low stock items, warehouse values, and recent transactions.
    """
    # Get inventory by category with proper null handling for categories
    categories = Product.objects.values(
        category_name=models.F('category__name')
    ).annotate(
        product_count=Count('product_id'),
    ).order_by('category_name')
    
    # Get low stock items
    low_stock_items = Inventory.objects.select_related(
        'product', 'warehouse'
    ).filter(
        quantity_on_hand__lte=F('product__reorder_point')
    ).order_by('product__product_name')[:10]
    
    # Get inventory value by warehouse
    warehouse_values = Inventory.objects.select_related(
        'product', 'warehouse'
    ).values('warehouse__warehouse_name').annotate(
        total_value=Sum(
            ExpressionWrapper(
                F('quantity_on_hand') * F('product__unit_cost'),
                output_field=DecimalField()
            ),
            default=0
        )
    ).order_by('-total_value')
    
    # Get recent inventory transactions
    recent_transactions = InventoryTransaction.objects.select_related(
        'product', 'warehouse'
    ).order_by('-transaction_date')[:15]
    
    context = {
        'categories': categories,
        'low_stock_items': low_stock_items,
        'warehouse_values': warehouse_values,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'dashboard/inventory_overview.html', context)


@login_required
def procurement_dashboard(request):
    """
    Dashboard view for procurement/purchasing.
    Shows orders by status, recent orders, awaiting deliveries, and active suppliers.
    """
    # Get summary of orders by status
    order_status_counts = PurchaseOrder.objects.values('po_status').annotate(
        count=Count('po_id')
    ).order_by('po_status')
    
    # Get most recent purchase orders
    recent_orders = PurchaseOrder.objects.select_related('supplier').order_by('-order_date')[:10]
    
    # Get orders that are awaiting delivery
    awaiting_delivery = PurchaseOrder.objects.select_related('supplier').filter(
        po_status='ordered',
        expected_delivery__isnull=False
    ).order_by('expected_delivery')[:10]
    
    # Get most active suppliers based on pending/active orders
    active_suppliers = Supplier.objects.filter(
        purchaseorder__po_status__in=['pending', 'approved', 'ordered']
    ).distinct().annotate(
        order_count=Count('purchaseorder')
    ).order_by('-order_count')[:5]
    
    context = {
        'order_status_counts': order_status_counts,
        'recent_orders': recent_orders,
        'awaiting_delivery': awaiting_delivery,
        'active_suppliers': active_suppliers,
    }
    return render(request, 'dashboard/procurement_dashboard.html', context)


@login_required
def eoq_dashboard(request):
    """
    Dashboard view for EOQ analysis.
    Shows products with EOQ parameters, products needing EOQ calculation, and high holding cost items.
    """
    # Get products that have EOQ values set with their calculated EOQ parameters
    products_with_eoq = Product.objects.select_related('category', 'eoq_parameters').filter(
        eoq__isnull=False
    ).order_by('product_name')[:15]
    
    # Get products that have parameters but need EOQ calculation
    # Include last_calculated date to show when parameters were last updated
    products_needing_eoq = Product.objects.select_related('category', 'eoq_parameters').filter(
        eoq__isnull=True,
        eoq_parameters__isnull=False
    ).order_by('product_name')
    
    # Get products with highest holding costs from EOQ parameters
    # This aligns with the actual EOQParameters model's holding_cost field
    high_holding_cost = EOQParameters.objects.select_related('product', 'product__category').order_by(
        '-holding_cost'
    )[:10]
    
    # Get count of products without EOQ parameters
    missing_params_count = Product.objects.filter(
        active=True, 
        eoq_parameters__isnull=True
    ).count()
    
    # Add recent EOQ calculations
    recent_eoq_updates = EOQParameters.objects.select_related('product').order_by(
        '-last_calculated'
    )[:10]
    
    context = {
        'products_with_eoq': products_with_eoq,
        'products_needing_eoq': products_needing_eoq,
        'high_holding_cost': high_holding_cost,
        'missing_params_count': missing_params_count,
        'recent_eoq_updates': recent_eoq_updates
    }
    return render(request, 'dashboard/eoq_dashboard.html', context)

@login_required
def warehouse_dashboard(request):
    """
    Dashboard view for warehouse management.
    Shows warehouse statistics and recent inventory transfers.
    """
    # Get all warehouses with inventory counts and total items
    warehouses = Warehouse.objects.filter(active=True).annotate(
        item_count=Count('inventories'),
        total_items=Sum('inventories__quantity_on_hand', default=0)
    )
    
    # Add warehouse URL links for each warehouse
    for warehouse in warehouses:
        warehouse.detail_url = reverse('warehouse:warehouse_detail', kwargs={'pk': warehouse.warehouse_id})
    
    # Get recent inventory transfers between warehouses
    recent_transfers = InventoryTransaction.objects.filter(
        transaction_type__in=['transfer_in', 'transfer_out']
    ).select_related('product', 'warehouse').order_by('-transaction_date')[:10]
    
    # Get warehouses with low stock items
    warehouses_with_low_stock = Warehouse.objects.filter(
        active=True,
        inventories__quantity_on_hand__lte=F('inventories__product__reorder_point')
    ).annotate(
        low_stock_count=Count('inventories', 
                              filter=Q(inventories__quantity_on_hand__lte=F('inventories__product__reorder_point')))
    ).order_by('-low_stock_count')
    
    # Add URL links for each warehouse with low stock
    for warehouse in warehouses_with_low_stock:
        warehouse.detail_url = reverse('warehouse:warehouse_detail', kwargs={'pk': warehouse.warehouse_id})
    
    context = {
        'warehouses': warehouses,
        'recent_transfers': recent_transfers,
        'warehouses_with_low_stock': warehouses_with_low_stock,
        'warehouse_list_url': reverse('warehouse:warehouse_list'),
        'warehouse_create_url': reverse('warehouse:warehouse_create'),
    }
    return render(request, 'dashboard/warehouse_dashboard.html', context)


@login_required
def demand_analysis(request):
    """
    Dashboard view for demand analysis.
    Shows products with demand history, recent demand entries, forecasted products and monthly demand.
    """
    # Get products with the most demand history entries
    products_with_demand = Product.objects.annotate(
        history_count=Count('demand_history')
    ).filter(history_count__gt=0).order_by('-history_count')[:10]
    
    # Get recent demand history entries - include demand_type to distinguish actual vs forecast
    recent_demand = DemandHistory.objects.select_related('product').order_by('-period_date')[:15]
    
    # Get products that have forecast data
    forecasted_products = Product.objects.filter(
        demand_history__demand_type='forecast'
    ).distinct().annotate(
        forecast_count=Count('demand_history', filter=Q(demand_history__demand_type='forecast')),
        actual_count=Count('demand_history', filter=Q(demand_history__demand_type='actual'))
    ).order_by('-forecast_count')[:10]
    
    # Get monthly demand trends for the past 6 months - separate actual and forecast data
    six_months_ago = timezone.now() - timedelta(days=180)
    
    # Get actual demand data
    actual_monthly_demand = DemandHistory.objects.filter(
        period_date__gte=six_months_ago,
        demand_type='actual'
    ).extra(
        select={'month': "EXTRACT(MONTH FROM period_date)", 
                'year': "EXTRACT(YEAR FROM period_date)"}
    ).values('month', 'year').annotate(
        total_demand=Sum('quantity_demanded')
    ).order_by('year', 'month')
    
    # Get forecast demand data for comparison
    forecast_monthly_demand = DemandHistory.objects.filter(
        period_date__gte=six_months_ago,
        demand_type='forecast'
    ).extra(
        select={'month': "EXTRACT(MONTH FROM period_date)", 
                'year': "EXTRACT(YEAR FROM period_date)"}
    ).values('month', 'year').annotate(
        total_demand=Sum('quantity_demanded')
    ).order_by('year', 'month')
    
    # Calculate trend data for visualization
    trend_labels = []
    actual_values = []
    forecast_values = []
    
    # Create a combined dictionary of months
    combined_months = {}
    
    # Add actual demand data to the dictionary
    for item in actual_monthly_demand:
        month_key = f"{int(item['year'])}-{int(item['month']):02d}"
        if month_key not in combined_months:
            combined_months[month_key] = {'month': int(item['month']), 'year': int(item['year']), 'actual': 0, 'forecast': 0}
        combined_months[month_key]['actual'] = item['total_demand']
    
    # Add forecast demand data to the dictionary
    for item in forecast_monthly_demand:
        month_key = f"{int(item['year'])}-{int(item['month']):02d}"
        if month_key not in combined_months:
            combined_months[month_key] = {'month': int(item['month']), 'year': int(item['year']), 'actual': 0, 'forecast': 0}
        combined_months[month_key]['forecast'] = item['total_demand']
    
    # Sort the dictionary by year and month and create trend data
    for month_key in sorted(combined_months.keys()):
        data = combined_months[month_key]
        month_name = datetime(2000, data['month'], 1).strftime('%b')
        trend_labels.append(f"{month_name} {data['year']}")
        actual_values.append(data['actual'])
        forecast_values.append(data['forecast'])
    
    # Get products with complete EOQ parameters for demand planning
    products_with_eoq = Product.objects.filter(
        eoq__isnull=False,
        eoq_parameters__isnull=False
    ).select_related('eoq_parameters').order_by('product_name')[:10]
    
    context = {
        'products_with_demand': products_with_demand,
        'recent_demand': recent_demand,
        'forecasted_products': forecasted_products,
        'trend_labels': trend_labels,
        'actual_values': actual_values,
        'forecast_values': forecast_values,
        'products_with_eoq': products_with_eoq
    }
    return render(request, 'dashboard/demand_analysis.html', context)