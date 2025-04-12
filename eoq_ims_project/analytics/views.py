# analytics/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Sum
import csv
import io
import datetime

from inventory.models import Product, Inventory
from .models import EOQParameters, DemandHistory
from .forms import EOQParametersForm, DemandHistoryForm, BulkDemandUploadForm

def eoq_parameters_selection(request):
    """Select a product to view/edit EOQ parameters"""
    products = Product.objects.all().order_by('product_name')
    
    # Get products with existing EOQ parameters
    products_with_eoq = EOQParameters.objects.select_related('product').all()
    
    context = {
        'products': products,
        'products_with_eoq': products_with_eoq,
    }
    return render(request, 'analytics/eoq_parameters_selection.html', context)

def eoq_parameters(request, product_id):
    """View/edit EOQ parameters for a specific product"""
    product = get_object_or_404(Product, product_id=product_id)
    
    # Check if EOQ parameters exist for this product
    try:
        eoq_params = EOQParameters.objects.get(product=product)
    except EOQParameters.DoesNotExist:
        eoq_params = None
    
    if request.method == 'POST':
        if eoq_params:
            form = EOQParametersForm(request.POST, instance=eoq_params)
        else:
            form = EOQParametersForm(request.POST)
        
        if form.is_valid():
            params = form.save(commit=False)
            if not eoq_params:
                params.product = product
            params.save()
            
            # Calculate and update EOQ
            eoq = params.calculate_eoq()
            messages.success(request, f'EOQ parameters updated. Calculated EOQ: {eoq:.2f}')
            return redirect('analytics:eoq_parameters', product_id=product.product_id)
    else:
        if eoq_params:
            form = EOQParametersForm(instance=eoq_params)
        else:
            # Pre-fill with initial data based on product
            initial_data = {
                'product': product,
                # You might want to calculate these based on historical data if available
                'annual_demand': product.demand_history.aggregate(total=Sum('quantity_demanded'))['total'] or 0,
            }
            form = EOQParametersForm(initial=initial_data)
    
    # Get demand history for the product
    demand_history = DemandHistory.objects.filter(product=product).order_by('-period_date')
    
    context = {
        'product': product,
        'form': form,
        'eoq_params': eoq_params,
        'demand_history': demand_history,
    }
    return render(request, 'analytics/eoq_parameters.html', context)

def eoq_parameters_list(request):
    """
    Display a list of all EOQ parameters for all products.
    """
    # Get all EOQ parameters
    eoq_parameters = EOQParameters.objects.select_related('product').all().order_by('product__product_name')
    
    # Pagination
    paginator = Paginator(eoq_parameters, 15)  # Show 15 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'analytics/eoq_parameters_list.html', context)

def add_demand_history(request, product_id=None):
    """Add a new demand history record"""
    product = None
    if product_id:
        product = get_object_or_404(Product, product_id=product_id)
    
    if request.method == 'POST':
        form = DemandHistoryForm(request.POST)
        if form.is_valid():
            demand_history = form.save()
            messages.success(request, f'Demand history added for {demand_history.product.product_name}')
            
            if product_id:
                return redirect('analytics:eoq_parameters', product_id=product_id)
            else:
                return redirect('analytics:demand_history_list')
    else:
        initial_data = {}
        if product:
            initial_data['product'] = product
        form = DemandHistoryForm(initial=initial_data)
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'analytics/demand_history_form.html', context)

def demand_history_list(request):
    """List all demand history records"""
    demand_history = DemandHistory.objects.select_related('product').all().order_by('-period_date')
    
    # Filter by product
    product_filter = request.GET.get('product', '')
    if product_filter:
        demand_history = demand_history.filter(product__product_id=product_filter)
    
    # Filter by date range
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    if start_date:
        demand_history = demand_history.filter(period_date__gte=start_date)
    if end_date:
        demand_history = demand_history.filter(period_date__lte=end_date)
    
    # Pagination
    paginator = Paginator(demand_history, 15)  # Show 15 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all products for the filter dropdown
    products = Product.objects.all()
    
    context = {
        'page_obj': page_obj,
        'products': products,
        'product_filter': product_filter,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'analytics/demand_history_list.html', context)

def bulk_demand_upload(request):
    """Upload demand history in bulk via CSV file"""
    if request.method == 'POST':
        form = BulkDemandUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            
            # Validate file is CSV
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file')
                return redirect('analytics:bulk_demand_upload')
            
            # Process the file
            try:
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.reader(io_string)
                next(reader)  # Skip header row
                
                records_added = 0
                records_skipped = 0
                errors = []
                
                for row in reader:
                    try:
                        product_id, period_date, quantity, demand_type = row
                        
                        # Validate product exists
                        try:
                            product = Product.objects.get(product_id=product_id)
                        except Product.DoesNotExist:
                            errors.append(f"Product ID {product_id} does not exist, skipping row")
                            records_skipped += 1
                            continue
                        
                        # Validate demand type
                        if demand_type not in ['actual', 'forecast']:
                            errors.append(f"Invalid demand type '{demand_type}' for product {product_id}, skipping row")
                            records_skipped += 1
                            continue
                        
                        # Create the DemandHistory record
                        DemandHistory.objects.create(
                            product=product,
                            period_date=period_date,
                            quantity_demanded=int(quantity),
                            demand_type=demand_type
                        )
                        records_added += 1
                    
                    except Exception as e:
                        errors.append(f"Error processing row: {e}")
                        records_skipped += 1
                
                if errors:
                    for error in errors[:5]:  # Show first 5 errors only
                        messages.warning(request, error)
                    if len(errors) > 5:
                        messages.warning(request, f"... and {len(errors) - 5} more errors")
                
                messages.success(request, f'Successfully added {records_added} records. Skipped {records_skipped} records.')
                return redirect('analytics:demand_history_list')
            
            except Exception as e:
                messages.error(request, f'Error processing file: {e}')
    else:
        form = BulkDemandUploadForm()
    
    context = {
        'form': form,
    }
    return render(request, 'analytics/bulk_demand_upload.html', context)

def inventory_analysis(request):
    """View showing inventory analysis metrics"""
    # Get all warehouses with their inventory levels
    warehouses = Inventory.objects.select_related('warehouse', 'product').values(
        'warehouse__warehouse_name'
    ).annotate(
        total_items=Sum('quantity_on_hand')
    ).order_by('warehouse__warehouse_name')
    
    # Get products below reorder point
    products_to_reorder = []
    inventory_items = Inventory.objects.select_related('product', 'warehouse').all()
    
    for inventory in inventory_items:
        if inventory.quantity_on_hand <= inventory.product.reorder_point:
            products_to_reorder.append({
                'product': inventory.product,
                'warehouse': inventory.warehouse,
                'quantity_on_hand': inventory.quantity_on_hand,
                'reorder_point': inventory.product.reorder_point,
                'shortage': inventory.product.reorder_point - inventory.quantity_on_hand
            })
    
    # Sort by shortage (highest first)
    products_to_reorder.sort(key=lambda x: x['shortage'], reverse=True)
    
    context = {
        'warehouses': warehouses,
        'products_to_reorder': products_to_reorder,
    }
    return render(request, 'analytics/inventory_analysis.html', context)

def demand_chart_data(request, product_id):
    """API endpoint to get demand history for charts"""
    product = get_object_or_404(Product, product_id=product_id)
    
    # Get demand history for the last 12 months
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)
    
    demand_history = DemandHistory.objects.filter(
        product=product,
        period_date__gte=start_date,
        period_date__lte=end_date
    ).order_by('period_date')
    
    actual_data = []
    forecast_data = []
    
    for demand in demand_history:
        data_point = {
            'date': demand.period_date.strftime('%Y-%m-%d'),
            'quantity': demand.quantity_demanded
        }
        
        if demand.demand_type == 'actual':
            actual_data.append(data_point)
        else:
            forecast_data.append(data_point)
    
    response_data = {
        'product_name': product.product_name,
        'actual_data': actual_data,
        'forecast_data': forecast_data
    }
    
    return JsonResponse(response_data)

def eoq_calculation(request):
    """
    Calculate EOQ values for products that have parameters but no EOQ value.
    """
    # Get products that have parameters but need EOQ calculation
    products_needing_eoq = Product.objects.select_related('eoq_parameters').filter(
        eoq__isnull=True,
        eoq_parameters__isnull=False
    )
    
    # Check if any products need calculation
    if not products_needing_eoq.exists():
        messages.info(request, 'No products need EOQ calculation at this time.')
        # Return to the same page instead of redirecting
        return redirect(request.META.get('HTTP_REFERER', 'analytics:eoq_parameters_list'))
    
    calculated_count = 0
    for product in products_needing_eoq:
        if hasattr(product, 'eoq_parameters'):
            # Calculate EOQ and update the product
            eoq = product.eoq_parameters.calculate_eoq()
            calculated_count += 1
    
    if calculated_count > 0:
        messages.success(request, f'Successfully calculated EOQ for {calculated_count} products.')
    else:
        messages.warning(request, 'No products were updated during EOQ calculation.')
        
    return redirect('analytics:eoq_parameters_list')